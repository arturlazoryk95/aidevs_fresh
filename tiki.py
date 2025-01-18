import tiktoken
import re
from uuid import uuid4
import pprint

def count_tokens(text: str, model:str) -> [int, list[int], str]:
    start = '<|im_start|>user\n'
    end = '<|im_end|>'
    additional = '\n<|im_start|>assistant<|im_end|>'
    message = start + text + end + additional
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(message)
    decoded = encoding.decode(tokens)
    return len(tokens), tokens, decoded


def extract_urls(text: str) -> list[str]:
    # Updated regex to match more complete URLs, including query parameters, fragments, etc.
    return re.findall(r'https?://[a-zA-Z0-9-._~:/?#[\]@!$&\'(*+,;=]+', text)

def is_image_url(text: str) -> bool:
    extensions = ['.jpeg', '.png', '.jpg']
    # Checking for the file extensions in a case-insensitive manner
    return any(text.lower().endswith(ext) for ext in extensions)

def is_audio_url(text: str) -> bool:
    extensions = ['.mp3', '.mp4', '.m4a']
    # Checking for the file extensions in a case-insensitive manner
    return any(text.lower().endswith(ext) for ext in extensions)

class Url():
    def __init__(self, url_id: str, url:str):
        self.url_id = url_id
        self.url = url
    
    def __str__(self):
        print(f'{url} | id:{url_id}')

def main():
    # Read content from a file
    with open('tmp_files/sample_website_markdown.md', 'r') as file:
        content = file.read()

    # Extract all URLs
    urls = extract_urls(content)
    
    # Lists to categorize URLs
    image_urls = []
    audio_urls = []
    other_urls = []
    
    # Loop through each URL and categorize it
    for url in urls:
        url_id = uuid4()  # Generate a unique ID for each URL
        if is_image_url(url):
            image_urls.append(Url(url_id, url))
        elif is_audio_url(url):
            audio_urls.append(Url(url_id, url))
        else: 
            other_urls.append(Url(url_id, url))

    # Print categorized URLs
    for image in image_urls:
        print(image.url)
        print(image.url_id)
 
    

if __name__ == '__main__':
    main()
