# HTTP Streaming Integration Guide

This document explains how to integrate HTTP streaming functionality with the StorybookArea component, replacing direct Python LLM engine calls with C++ server communication.

## Overview

The refactoring introduces:
- `HttpStreamWorker`: QThread-based HTTP streaming client
- `AsyncHttpStreamClient`: Alternative async implementation using aiohttp
- Enhanced `StorybookArea` with streaming capabilities
- Token-based real-time text updates

## Key Components

### 1. HttpStreamWorker (`components/http_stream_worker.py`)

Handles streaming HTTP requests to C++ server using `requests` with `stream=True`:

```python
from components.http_stream_worker import HttpStreamWorker

# Create worker
worker = HttpStreamWorker(prompt="Tell me a story", server_url="http://localhost:8080")

# Connect signals
worker.token_received.connect(lambda token: print(f"Token: {token}"))
worker.error_occurred.connect(lambda err: print(f"Error: {err}"))
worker.finished.connect(lambda: print("Finished"))

# Start streaming
worker.start()
```

**Signals:**
- `token_received(str)`: Individual token from stream
- `chunk_received(str)`: Raw chunk data
- `error_occurred(str)`: Error message
- `started()`: Stream started
- `finished()`: Stream completed

### 2. Enhanced StorybookArea

New methods for HTTP streaming:

```python
# Start streaming for current page
storybook.startHttpStream("Once upon a time...")

# Start streaming for specific page
storybook.startHttpStream("Chapter 2 begins...", page=1)

# Stop current stream
storybook.stopHttpStream()

# Check streaming status
if storybook.isStreaming():
    print("Currently streaming...")

# Set server URL
storybook.setServerUrl("http://localhost:8080")
```

**New Signals:**
- `streamStarted()`: HTTP streaming started
- `streamFinished()`: HTTP streaming completed  
- `streamError(str)`: Streaming error occurred

## Integration Steps

### 1. Replace Direct LLM Calls

**Before (Direct LLM):**
```python
# Old approach - direct Python LLM calls
response = llm_engine.generate(prompt)
storybook.setStoryText(response, page=0, animated=True)
```

**After (HTTP Streaming):**
```python
# New approach - HTTP streaming
storybook.startHttpStream(prompt, page=0)
```

### 2. Handle Streaming Events

```python
class MainController:
    def __init__(self):
        self.storybook = StorybookArea()
        
        # Connect streaming signals
        self.storybook.streamStarted.connect(self.on_stream_started)
        self.storybook.streamFinished.connect(self.on_stream_finished)
        self.storybook.streamError.connect(self.on_stream_error)
    
    def generate_story(self, prompt: str):
        """Generate story using HTTP streaming"""
        self.storybook.startHttpStream(prompt)
    
    def on_stream_started(self):
        print("Story generation started...")
        # Update UI (disable buttons, show spinner, etc.)
    
    def on_stream_finished(self):
        print("Story generation completed")
        # Update UI (enable buttons, hide spinner, etc.)
    
    def on_stream_error(self, error: str):
        print(f"Story generation failed: {error}")
        # Show error message to user
```

### 3. Page Navigation

Page changes automatically stop any ongoing stream and restore cached text:

```python
# These methods now handle streaming properly
storybook.previousPage()  # Stops stream, restores cached text
storybook.nextPage()      # Stops stream, restores cached text
```

## C++ Server Requirements

Your C++ server should:

1. Accept POST requests to `/generate` endpoint
2. Support JSON payload: `{"prompt": "...", "stream": true}`
3. Return chunked transfer encoding or line-delimited responses

**Expected Response Formats:**

**Option 1 - Plain text tokens:**
```
Once
 upon
 a
 time
...
```

**Option 2 - JSON tokens:**
```json
{"token": "Once"}
{"token": " upon"}
{"token": " a"}
{"token": " time"}
```

**Option 3 - Structured response:**
```json
{"text": "Once", "done": false}
{"text": " upon", "done": false}
{"text": " a", "done": false}
{"text": " time", "done": true}
```

## Error Handling

The system handles various error conditions:

- **Network errors**: Connection timeouts, server unavailable
- **HTTP errors**: 4xx/5xx status codes
- **Parsing errors**: Invalid JSON responses  
- **Threading errors**: Worker thread failures

All errors are reported via the `streamError` signal with descriptive messages.

## Performance Considerations

- **Threading**: Uses QThread to avoid blocking UI
- **Memory**: Streams tokens incrementally, not buffering entire response
- **Caching**: Page text is cached in `_page_texts` dictionary
- **Auto-scroll**: Text area automatically scrolls as content arrives

## Example Usage

See `examples/http_stream_example.py` for a complete working demo.

## Migration Checklist

- [ ] Replace `llm_engine.generate()` calls with `startHttpStream()`
- [ ] Connect streaming signals (`streamStarted`, `streamFinished`, `streamError`)
- [ ] Update UI controls to handle streaming states
- [ ] Set appropriate server URL with `setServerUrl()`
- [ ] Test error handling (server down, invalid responses)
- [ ] Verify page navigation works correctly during streaming
- [ ] Test multi-page scenarios with streaming

## Troubleshooting

**Stream not starting:**
- Check server URL is correct and accessible
- Verify C++ server is running and accepting connections
- Check network connectivity

**Tokens not appearing:**
- Verify C++ server returns proper chunked responses
- Check response format matches expected JSON/text structure
- Enable debug logging to see raw chunks

**UI freezing:**
- Ensure worker is running in separate thread (should be automatic)
- Check for infinite loops in token handling
- Verify signals are connected properly