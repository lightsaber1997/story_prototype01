# -*- coding: utf-8 -*-

"""
MyStoryPal UI Components Package

이 패키지는 MyStoryPal 애플리케이션의 UI 컴포넌트들을 포함합니다.

Components:
- NavigationBar: 왼쪽 네비게이션 바
- ChatArea: 중간 채팅 영역  
- StorybookArea: 오른쪽 스토리북 영역
"""

from .navigation_bar import NavigationBar
from .chat_area import ChatArea, ChatMessageDelegate
from .storybook_area import StorybookArea

__all__ = [
    'NavigationBar',
    'ChatArea', 
    'ChatMessageDelegate',
    'StorybookArea'
]

__version__ = '1.0.0'
__author__ = 'MyStoryPal Team'