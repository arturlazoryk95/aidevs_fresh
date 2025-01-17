import tiktoken
import re

def count_tokens(text: str, model:str) -> [int, list[int], str]:
    start = '<|im_start|>user\n'
    end = '<|im_end|>'
    additional = '\n<|im_start|>assistant<|im_end|>'
    message = start + text + end + additional
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(message)
    decoded = encoding.decode(tokens)
    return len(tokens), tokens, decoded

def extract_urls(text:str) -> list[str]:
    return re.findall(r'https?://[^\s]+', text)

def main():
    with open('tmp_files/REGEX.md', 'r') as file:
        content = file.read()

    urls = extract_urls(content)
    for url in urls:
        print(url)

if __name__=='__main__':
    main()