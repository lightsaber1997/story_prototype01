# chat_gpt_engine.py
import openai
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

class ChatGPTEngine:
    """ChatGPT API wrapper that mimics Phi3MiniEngine interface."""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 model_name: Optional[str] = None,
                 temperature: Optional[float] = None,
                 top_p: Optional[float] = None,
                 env_file: str = ".env"):
        
        # Load environment variables
        load_dotenv(env_file)
        
        # Set API key
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "OpenAI API key not found. Please set OPENAI_API_KEY in .env file"
                )
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Set model and parameters
        self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.temperature = temperature if temperature is not None else float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.top_p = top_p if top_p is not None else float(os.getenv("OPENAI_TOP_P", "1.0"))
        
        print(f"ChatGPT Engine initialized with model: {self.model_name}")
        
        # Compatibility attributes
        self.tokenizer = None
        self.model = None
        self.EOS_ID = None
    
    def build_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Build prompt from messages (for compatibility)."""
        parts = []
        for m in messages:
            parts.append(f"{m['role']}: {m['content']}")
        return "\n".join(parts)
    
    def generate_reply(self, 
                       messages: List[Dict[str, str]], 
                       *, 
                       max_new_tokens: int = 128) -> str:
        """
        Generate a reply using ChatGPT API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            max_new_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated reply text
        """
        try:
            # Convert messages to OpenAI format
            formatted_messages = []
            for msg in messages:
                role = msg.get('role', 'user')
                if role in ['user', 'assistant', 'system']:
                    formatted_messages.append({
                        'role': role,
                        'content': msg['content']
                    })
                else:
                    formatted_messages.append({
                        'role': 'user',
                        'content': msg['content']
                    })
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=formatted_messages,
                max_tokens=max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                n=1,
                stop=None,
            )
            
            # Extract and return the reply
            reply = response.choices[0].message.content
            return reply.strip()
            
        except openai.OpenAIError as e:
            print(f"OpenAI API error: {e}")
            return f"Error generating response: {str(e)}"
        except Exception as e:
            print(f"Unexpected error: {e}")
            return f"Unexpected error occurred: {str(e)}"