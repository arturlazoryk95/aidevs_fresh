from openai import OpenAI
from decouple import config
from tiktoken import encoding_for_model
from typing import List, Dict, Union, AsyncIterable, Optional
import requests

class OpenAIService:
    def __init__(self):
        self.openai = OpenAI(api_key=config('OPENAI_API_KEY'))
        self.tokenizers = {}
        self.IM_START = "<|im_start|>"
        self.IM_END = "<|im_end|>"
        self.IM_SEP = "<|im_sep|>"
        self.JINA_API_KEY = config('JINA_API_KEY')

    def get_tokenizer(self, model_name: str):
        if model_name not in self.tokenizers:
            self.tokenizers[model_name] = encoding_for_model(model_name)
        return self.tokenizers[model_name]

    async def count_tokens(self, messages: List[Dict], model: str = 'gpt-4') -> int:
        tokenizer = self.get_tokenizer(model)
        formatted_content = ''
        
        for message in messages:
            formatted_content += f"{self.IM_START}{message['role']}{self.IM_SEP}{message.get('content', '')}{self.IM_END}"
        formatted_content += f"{self.IM_START}assistant{self.IM_SEP}"

        tokens = tokenizer.encode(formatted_content)
        return len(tokens)

    async def create_embedding(self, text: str) -> List[float]:
        try:
            response = self.openai.embeddings.create(
                model="text-embedding-3-large",
                input=text
            )
            return response.data[0].embedding
        except Exception as error:
            print("Error creating embedding:", error)
            raise

    async def create_jina_embedding(self, text: str) -> List[float]:
        try:
            response = requests.post(
                'https://api.jina.ai/v1/embeddings',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f"Bearer {self.JINA_API_KEY}"
                },
                json={
                    'model': 'jina-embeddings-v3',
                    'task': 'text-matching',
                    'dimensions': 1024,
                    'late_chunking': False,
                    'embedding_type': 'float',
                    'input': [text]
                }
            )
            response.raise_for_status()
            data = response.json()
            return data['data'][0]['embedding']
        except Exception as error:
            print("Error creating Jina embedding:", error)
            raise

    async def completion(self, config: Dict) -> Union[Dict, AsyncIterable]:
        messages = config['messages']
        model = config.get('model', 'gpt-4')
        stream = config.get('stream', False)
        json_mode = config.get('json_mode', False)
        max_tokens = config.get('max_tokens', 4096)

        try:
            completion_params = {
                'messages': messages,
                'model': model,
            }

            if model not in ['o1-mini', 'o1-preview']:
                completion_params.update({
                    'stream': stream,
                    'max_tokens': max_tokens,
                    'response_format': {'type': 'json_object'} if json_mode else {'type': 'text'}
                })

            return await self.openai.chat.completions.create(**completion_params)
        except Exception as error:
            print("Error in OpenAI completion:", error)
            raise

    def calculate_image_tokens(self, width: int, height: int, detail: str = 'low') -> int:
        token_cost = 0

        if detail == 'low':
            return token_cost + 85

        MAX_DIMENSION = 2048
        SCALE_SIZE = 768

        # Resize to fit within MAX_DIMENSION
        if width > MAX_DIMENSION or height > MAX_DIMENSION:
            aspect_ratio = width / height
            if aspect_ratio > 1:
                width = MAX_DIMENSION
                height = round(MAX_DIMENSION / aspect_ratio)
            else:
                height = MAX_DIMENSION
                width = round(MAX_DIMENSION * aspect_ratio)

        # Scale shortest side to SCALE_SIZE
        if width >= height and height > SCALE_SIZE:
            width = round((SCALE_SIZE / height) * width)
            height = SCALE_SIZE
        elif height > width and width > SCALE_SIZE:
            height = round((SCALE_SIZE / width) * height)
            width = SCALE_SIZE

        # Calculate 512px squares
        num_squares = -(-width // 512) * -(-height // 512)  # Ceiling division
        token_cost += (num_squares * 170) + 85

        return token_cost
