# -*- coding: utf-8 -*-

import requests
import json
from PySide6.QtCore import QThread, Signal
from typing import Dict, Any, Optional

class HttpStreamWorker(QThread):
    """
    QThread worker for streaming HTTP responses from C++ server
    Emits tokens as they arrive from chunked transfer encoding
    """
    
    # Signals
    token_received = Signal(str)  # Individual token received
    chunk_received = Signal(str)  # Raw chunk received
    error_occurred = Signal(str)  # Error message
    finished = Signal()  # Stream completed
    started = Signal()   # Stream started
    
    def __init__(self, prompt: str, server_url: str = "http://localhost:8080", endpoint: str = "/generate"):
        super().__init__()
        self.prompt = prompt
        self.server_url = server_url
        self.endpoint = endpoint
        self.should_stop = False
        
    def stop(self):
        """Request the worker to stop streaming"""
        self.should_stop = True
        
    def run(self):
        """Main thread execution - handles HTTP streaming"""
        try:
            self.started.emit()
            url = f"{self.server_url}{self.endpoint}"
            
            payload = {
                "prompt": self.prompt,
                "stream": True  # Request streaming response
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "text/plain, application/json"
            }
            
            with requests.post(
                url,
                json=payload,
                headers=headers,
                stream=True,
                timeout=(10, None)  # 10s connection timeout, no read timeout
            ) as response:
                
                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    self.error_occurred.emit(error_msg)
                    return
                
                # Process streaming response
                for line in response.iter_lines(decode_unicode=True):
                    if self.should_stop:
                        break
                        
                    if not line or not line.strip():
                        continue
                        
                    # Emit raw chunk
                    self.chunk_received.emit(line)
                    
                    # Try to parse as JSON for structured response
                    try:
                        data = json.loads(line)
                        if isinstance(data, dict):
                            # Extract token from structured response
                            token = data.get('token', data.get('text', data.get('content', '')))
                            if token:
                                self.token_received.emit(token)
                        else:
                            # Direct string response
                            self.token_received.emit(str(data))
                    except json.JSONDecodeError:
                        # Plain text token
                        self.token_received.emit(line.strip())
                        
        except requests.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self.error_occurred.emit(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.error_occurred.emit(error_msg)
        finally:
            self.finished.emit()


class AsyncHttpStreamClient:
    """
    Alternative async implementation using aiohttp for better performance
    Can be used with asyncio bridge if needed
    """
    
    def __init__(self, server_url: str = "http://localhost:8080"):
        self.server_url = server_url
        
    async def stream_request(self, prompt: str, endpoint: str = "/generate"):
        """
        Async generator that yields tokens from HTTP stream
        Usage: async for token in client.stream_request(prompt):
        """
        import aiohttp
        
        url = f"{self.server_url}{endpoint}"
        payload = {
            "prompt": prompt,
            "stream": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")
                
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    if not line_str:
                        continue
                        
                    try:
                        data = json.loads(line_str)
                        if isinstance(data, dict):
                            token = data.get('token', data.get('text', data.get('content', '')))
                            if token:
                                yield token
                        else:
                            yield str(data)
                    except json.JSONDecodeError:
                        yield line_str