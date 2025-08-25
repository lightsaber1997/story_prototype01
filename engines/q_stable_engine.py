# ── Diffusers / Torch
import torch
from diffusers import StableDiffusionPipeline
from pathlib import Path
from typing import Optional, Union

import argparse
import numpy as np
from diffusers import (
    EulerDiscreteScheduler,
    EulerAncestralDiscreteScheduler,
    DPMSolverMultistepScheduler,
    KDPM2DiscreteScheduler,
    KDPM2AncestralDiscreteScheduler,
    PNDMScheduler,
    LMSDiscreteScheduler,
    HeunDiscreteScheduler,
    DDIMScheduler,
)
from PIL import Image
from qai_hub_models.models._shared.stable_diffusion.app import StableDiffusionApp
from qai_hub_models.utils.args import add_output_dir_arg
from qai_hub_models.utils.display import display_or_save_image, to_uint8
from qai_hub_models.utils.onnx_torch_wrapper import (
    OnnxModelTorchWrapper,
    OnnxSessionOptions,
)
from transformers import CLIPTokenizer

DEFAULT_PROMPT = "A girl taking a walk at sunset"
HF_REPO = "stabilityai/stable-diffusion-2-1-base"

# 스케줄러 맵핑 확장
SCHEDULERS = {
        "euler": EulerDiscreteScheduler,
        "euler_a": EulerAncestralDiscreteScheduler,
        "dpm": DPMSolverMultistepScheduler,
        "kdpm2": KDPM2DiscreteScheduler,
        "kdpm2_a": KDPM2AncestralDiscreteScheduler,
        "pndm": PNDMScheduler,
        "lms": LMSDiscreteScheduler,
        "heun": HeunDiscreteScheduler,
        "ddim": DDIMScheduler
        }

class QStableV21Engine:
    def __init__(self, text_encoder: str, vae_decoder: str, unet: str, scheduler, channel_last_latent=False):
        options = OnnxSessionOptions.aihub_defaults()
        options.context_enable = False

        scheduler_cls = SCHEDULERS[scheduler]
        scheduler = scheduler_cls.from_pretrained(HF_REPO, subfolder="scheduler")

        self.sdapp = StableDiffusionApp(
            OnnxModelTorchWrapper.OnNPU(text_encoder, options),
            OnnxModelTorchWrapper.OnNPU(vae_decoder, options),
            OnnxModelTorchWrapper.OnNPU(unet, options),
            CLIPTokenizer.from_pretrained(HF_REPO, subfolder="tokenizer"),
            scheduler,
            channel_last_latent=channel_last_latent
        ) 
       
    def generate_image(self, prompt: str, num_steps: int = 30, seed: int = 123):
        # Generate image
        image = self.sdapp.generate_image(prompt, num_steps=num_steps, seed=seed)
        pil_img = Image.fromarray(to_uint8(np.asarray(image))[0])
        return pil_img


    @staticmethod
    def save_image(img, path: Union[str, Path]) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        img.save(path)



