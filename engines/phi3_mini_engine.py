# ── Transformers / Torch
import torch
from engines.base_engine import BaseEngine


# ── LLM Engine (new) ────────────────────────────────────────────────
class Phi3MiniEngine(BaseEngine):
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

    @torch.inference_mode()
    def generate_reply_stream(self, messages, *, max_new_tokens: int = 128):
        """
        Efficient streaming reply using Phi3 model with past_key_values.
        """
        prompt = self.build_prompt(messages)
        enc = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        # 첫 step: full forward (past_key_values 준비)
        outputs = self.model(**enc, use_cache=True)
        past_key_values = outputs.past_key_values

        next_token = torch.argmax(outputs.logits[:, -1, :], dim=-1)
        generated = [next_token.item()]

        for _ in range(max_new_tokens - 1):
            # 캐시된 past_key_values 활용 → 이전 프롬프트 전체 재계산 불필요
            outputs = self.model(
                input_ids=next_token.unsqueeze(0),
                past_key_values=past_key_values,
                use_cache=True,
            )
            past_key_values = outputs.past_key_values
            next_token = torch.argmax(outputs.logits[:, -1, :], dim=-1)

            if next_token.item() == self.EOS_ID:
                break

            generated.append(next_token.item())
            token_text = self.tokenizer.decode([next_token.item()], skip_special_tokens=True)

            if not any(tag in token_text for tag in ("<|assistant|>", "<|end|>", "<|user|>", "<|system|>")):
                yield token_text
