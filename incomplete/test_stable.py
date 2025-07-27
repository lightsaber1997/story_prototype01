# ── Diffusers / Torch
import torch
from diffusers import StableDiffusionPipeline
from pathlib import Path
from typing import Optional, Union


class StableV15Engine:
    """
    Wraps the Stable Diffusion v1‑5 pipeline and exposes generate_image().
    """

    def __init__(
        self,
        model_id: str = "sd-legacy/stable-diffusion-v1-5",
        device: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
    ):
        device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        dtype = dtype or (torch.float16 if device.startswith("cuda") else torch.float32)

        # Load & move to device
        self.pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype)
        self.pipe.to(device)            #  ← no .eval() needed

    @torch.inference_mode()
    def generate_image(
        self,
        prompt: str,
        *,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        height: int = 512,
        width: int = 512,
        seed: Optional[int] = None,
        **kwargs,
    ):
        generator = (
            torch.Generator(device=self.pipe.device).manual_seed(seed) if seed is not None else None
        )
        result = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            height=height,
            width=width,
            generator=generator,
            **kwargs,
        )
        return result.images[0]

    @staticmethod
    def save_image(img, path: Union[str, Path]) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        img.save(path)


import re
from typing import Sequence

def first_sentence(text: str, *, eos: Sequence[str] = (".", "?", "!")) -> str:
    """
    Return the first sentence in *text*.

    Parameters
    ----------
    text : str
        The input string.
    eos : sequence of str, optional
        Characters that mark sentence endings.  Default: ('.', '?', '!')
        Pass a different set to customize—e.g. eos=("。",) for Japanese.
    """
    if not text:
        return ""

    # Escape each terminator for regex and join into a character class
    eos_class = "[" + re.escape("".join(eos)) + "]"

    # Non‑greedy up to the first terminator followed by space or end‑of‑string
    pattern = rf"(.+?{eos_class})(?:\s|$)"
    match = re.search(pattern, text.strip(), re.DOTALL)

    return match.group(1).strip() if match else text.strip()


if __name__ == "__main__":
    engine = StableV15Engine()
    sentence = "One day, a brave prince set out on a quest to find a magical flower that could heal his sick mother.Along his journey, he met a wise old owl who gave him three riddles to solve. "
    sentence = first_sentence(sentence)
    print(sentence)
    img = engine.generate_image(sentence + \
                                "children's picture book")
    engine.save_image(img, "astronaut_rides_horse.png")
    print("Saved to astronaut_rides_horse.png")
