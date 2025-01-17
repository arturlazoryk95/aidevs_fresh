from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re
from tiktoken import encoding_for_model

@dataclass
class DocumentMetadata:
    tokens: int
    headers: Dict[str, List[str]]
    urls: List[str]
    images: List[str]
    additional: Dict = field(default_factory=dict)

@dataclass
class Document:
    text: str
    metadata: DocumentMetadata

class TextSplitter:
    def __init__(self, model_name: str = 'gpt-4'):
        self.model_name = model_name
        self.tokenizer = None
        self.SPECIAL_TOKENS = {
            '<|im_start|>': 100264,
            '<|im_end|>': 100265,
            '<|im_sep|>': 100266,
        }

    async def initialize_tokenizer(self, model: Optional[str] = None):
        if not self.tokenizer or model != self.model_name:
            self.model_name = model or self.model_name
            self.tokenizer = encoding_for_model(self.model_name)

    def count_tokens(self, text: str) -> int:
        if not self.tokenizer:
            raise RuntimeError('Tokenizer not initialized')
        formatted_content = self.format_for_tokenization(text)
        tokens = self.tokenizer.encode(formatted_content)
        return len(tokens)

    def format_for_tokenization(self, text: str) -> str:
        return f"<|im_start|>user\n{text}<|im_end|>\n<|im_start|>assistant<|im_end|>"

    async def split(self, text: str, limit: int) -> List[Document]:
        print(f"Starting split process with limit: {limit} tokens")
        await self.initialize_tokenizer()
        chunks = []
        position = 0
        total_length = len(text)
        current_headers = {}

        while position < total_length:
            print(f"Processing chunk starting at position: {position}")
            chunk_text, chunk_end = self.get_chunk(text, position, limit)
            tokens = self.count_tokens(chunk_text)
            print(f"Chunk tokens: {tokens}")

            headers_in_chunk = self.extract_headers(chunk_text)
            self.update_current_headers(current_headers, headers_in_chunk)

            content, urls, images = self.extract_urls_and_images(chunk_text)

            chunks.append(Document(
                text=content,
                metadata=DocumentMetadata(
                    tokens=tokens,
                    headers=dict(current_headers),
                    urls=urls,
                    images=images
                )
            ))

            print(f"Chunk processed. New position: {chunk_end}")
            position = chunk_end

        print(f"Split process completed. Total chunks: {len(chunks)}")
        return chunks

    def get_chunk(self, text: str, start: int, limit: int) -> tuple[str, int]:
        print(f"Getting chunk starting at {start} with limit {limit}")
        
        # Calculate overhead
        overhead = self.count_tokens(self.format_for_tokenization('')) - self.count_tokens('')
        
        # Initial end position
        end = min(
            start + int((len(text) - start) * limit / self.count_tokens(text[start:])),
            len(text)
        )
        
        # Adjust for token limit
        chunk_text = text[start:end]
        tokens = self.count_tokens(chunk_text)
        
        while tokens + overhead > limit and end > start:
            print(f"Chunk exceeds limit with {tokens + overhead} tokens. Adjusting...")
            end = self.find_new_chunk_end(text, start, end)
            chunk_text = text[start:end]
            tokens = self.count_tokens(chunk_text)

        # Align with newlines
        end = self.adjust_chunk_end(text, start, end, tokens + overhead, limit)
        
        chunk_text = text[start:end]
        print(f"Final chunk end: {end}")
        return chunk_text, end

    def extract_headers(self, text: str) -> Dict[str, List[str]]:
        headers = {}
        header_regex = re.compile(r'(^|\n)(#{1,6})\s+(.*)', re.MULTILINE)
        
        for match in header_regex.finditer(text):
            level = len(match.group(2))
            content = match.group(3).strip()
            key = f'h{level}'
            headers.setdefault(key, []).append(content)
            
        return headers

    def update_current_headers(self, current: Dict[str, List[str]], extracted: Dict[str, List[str]]):
        for level in range(1, 7):
            key = f'h{level}'
            if key in extracted:
                current[key] = extracted[key]
                self.clear_lower_headers(current, level)

    def clear_lower_headers(self, headers: Dict[str, List[str]], level: int):
        for l in range(level + 1, 7):
            headers.pop(f'h{l}', None)

    def extract_urls_and_images(self, text: str) -> tuple[str, List[str], List[str]]:
        urls = []
        images = []
        url_index = 0
        image_index = 0

        def replace_image(match):
            nonlocal image_index
            alt_text, url = match.groups()
            images.append(url)
            return f'![{alt_text}]({{{{$img{image_index}}}}})'.format(image_index:=image_index+1)

        def replace_url(match):
            nonlocal url_index
            link_text, url = match.groups()
            urls.append(url)
            return f'[{link_text}]({{{{$url{url_index}}}}})'.format(url_index:=url_index+1)

        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, text)
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_url, content)

        return content, urls, images

    async def document(
        self, 
        text: str, 
        model: Optional[str] = None, 
        additional_metadata: Optional[Dict] = None
    ) -> Document:
        await self.initialize_tokenizer(model)
        tokens = self.count_tokens(text)
        headers = self.extract_headers(text)
        content, urls, images = self.extract_urls_and_images(text)
        
        metadata = DocumentMetadata(
            tokens=tokens,
            headers=headers,
            urls=urls,
            images=images,
            additional=additional_metadata or {}
        )
        
        return Document(text=content, metadata=metadata)
