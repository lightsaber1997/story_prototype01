import format_helper

# ── LLM Engine (new) ────────────────────────────────────────────────
class Phi3MiniEngine:
    """Owns the tokenizer/model and exposes generate_reply()."""

    def __init__(self, model_name: str = "microsoft/Phi-3-mini-128k-instruct"):
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch

        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
        ).eval()

        # expose eos once
        self.EOS_ID = self.tokenizer.eos_token_id or self.tokenizer.convert_tokens_to_ids("<|end|>")

    def build_prompt(self, messages):
        if hasattr(self.tokenizer, "apply_chat_template"):
            return self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        parts = [f"<|{m['role']}|>\n{m['content']}<|end|>" for m in messages]
        parts.append("<|assistant|>\n")
        return "\n".join(parts)

    @torch.inference_mode()
    def generate_reply(self, messages, *, max_new_tokens: int = 128):
        prompt = self.build_prompt(messages)
        enc = self.tokenizer(prompt, return_tensors="pt")
        enc = {k: v.to(self.model.device) for k, v in enc.items()}

        out_ids = self.model.generate(
            **enc,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            eos_token_id=self.EOS_ID,
            pad_token_id=self.tokenizer.pad_token_id or self.EOS_ID,
        )
        gen = out_ids[0][enc["input_ids"].shape[1]:]
        reply = self.tokenizer.decode(gen, skip_special_tokens=True)
        for tag in ("<|assistant|>", "<|end|>"):
            if tag in reply:
                reply = reply.split(tag)[0]
        return reply.strip()
