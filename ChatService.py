from openai import OpenAI
from decouple import config
import tiktoken

class ChatService():
    def __init__(self, model='gpt-4o-mini'):
        self.openai = OpenAI(api_key=config('OPENAI_SEASON2_API_KEY'))
        self.IM_START = '<|im_start|>'
        self.IM_END = '<|im_end|>'
        self.model = model
        self.pricing = {
            'gpt-4o':{
                'input': 2.5 / 10**6,
                'output': 10.00 / 10**6,
            },
            'gpt-4o-mini':{
                'input': 0.15 / 10**6,
                'output': 0.60 / 10**6,
            },
            'gpt-4o-2024-08-06':{
                'input': 2.50 / 10**6,
                'output': 10.00 / 10**6,
            },
            'gpt-3.5-turbo':{
                'input': 3.00 / 10**6,
                'output': 6.00 / 10**6,
            },
            'text-embedding-3-small':{
                'input': 0.020 / 10**6,
                'output': 0.020 / 10**6,
            },
            'text-embedding-3-large':{
                'input': 0.130 / 10**6,
                'output': 0.130 / 10**6,
            },
        }
        self.input_price = self.pricing[self.model]['input']
        self.output_price = self.pricing[self.model]['output']


    def format_for_tokenization(self, messages:list) -> str:
        return f"{self.IM_START}system\n{messages[0]['content']}{self.IM_END}\n{self.IM_START}user\n{messages[1]['content']}{self.IM_END}"

    def count_tokens(self, text:str) -> int:
        encoding = tiktoken.encoding_for_model(self.model)
        tokens = encoding.encode(text)
        return len(tokens)

    def completion(self, parameters:dict) -> dict:
        messages = parameters['messages']
        model = parameters.get('model', self.model)
        max_tokens = parameters.get('max_tokens', 1000)

        params = {
            'messages':messages,
            'model':model,
            'max_tokens':max_tokens
        }
        answer = self.openai.chat.completions.create(**params) 
        input_tokens = self.count_tokens(self.format_for_tokenization(messages))
        output_tokens = self.count_tokens(answer.choices[0].message.content)

        return {
            'answer':answer.choices[0].message.content,
            'input_tokens':input_tokens,
            'output_tokens':output_tokens,
            'total_spend': f'{input_tokens*self.input_price+output_tokens*self.output_price}$',
        }

    def create_embedding(self, text:str) -> list[float]:
        embedding = self.openai.embeddings.create(
            input=text,
            model='text-embedding-3-small',
        )
        return embedding.data[0].embedding

        # OUTPUT:
        # ------------------------------------
        # {
        #     "object": "list",
        #     "data": [
        #         {
        #             "object": "embedding",
        #             "index": 0,
        #             "embedding": [
        #                 -0.006929283495992422,
        #                 -0.005336422007530928,
        #                 -4.547132266452536e-05,
        #                 -0.024047505110502243
        #             ],
        #         }
        #     ],
        #     "model": "text-embedding-3-small",
        #     "usage": {
        #         "prompt_tokens": 5,
        #         "total_tokens": 5
        #     }
        # }