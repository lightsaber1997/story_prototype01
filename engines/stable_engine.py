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



