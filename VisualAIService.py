from openai import OpenAI

from openai import OpenAI
from decouple import config
import tiktoken

class ChatService():
    def __init__(self, model='gpt-4o'):
        self.model = model
        self.openai_service = OpenAI(api_key=config('OPENAI_SEASON2_API_KEY'))
    
    def analyse_image(self, url:str, system_prompt:str) -> str:
        response = self.openai_service.chat.completions.create(
            model=self.model,
            messages = [
                {
                    'role':'system',
                    'content':system_prompt,
                },
                {
                    'role':'user',
                    'content': [
                        {
                            'type':'image_url',
                            'image_url': {
                                'url':url,
                            },
                        },
                    ],
                },
            ],

        )
        return response.choices[0].message.content
    
    def extractImageName(self, user_query:str) -> str:
        response = self.openai_service.chat.completions.create(
            model=self.model,
            messages = [
                {
                    'role':'system',
                    'content':'Extract image name. Output should be the name of the image. Nothing else. If there is no image name, output "None".',
                },
                {
                    'role':'user',
                    'content':user_query,
                },
            ],
        )
        return response.choices[0].message.content