# -*- coding: utf-8 -*-

"""
MyStoryPal AI Engines Package

Engines:
- ChatEngine: 채팅 처리 엔진
- ChatGPTEngine: OpenAI GPT API 엔진
- Phi3MiniEngine: 로컬 Phi-3 모델 엔진
- StableV15Engine: Stable Diffusion 이미지 생성 엔진
- ImageGenController: 이미지 생성 컨트롤러
"""

from .chat_engine import ChatController, ChatWorker
from .chat_gpt_engine import ChatGPTEngine
from .phi3_mini_engine import Phi3MiniEngine
from .stable_engine import StableV15Engine
from .image_gen_engine import ImageGenController, ImageGenWorker

__all__ = [
    'ChatController',
    'ChatWorker', 
    'ChatGPTEngine',
    'Phi3MiniEngine',
    'StableV15Engine',
    'ImageGenController',
    'ImageGenWorker'
]

__version__ = '1.0.0'
__author__ = 'MyStoryPal Team'