from langfuse.openai import OpenAI
from pydantic import BaseModel
from typing import Literal
from openai import OpenAI
from decouple import config
import tiktoken
from langfuse.decorators import observe, langfuse_context

langfuse_context.configure(
    public_key=config('LANGFUSE_PUBLIC_KEY'),
    secret_key=config('LANGFUSE_SECRET_KEY'),
    host=config('LANGFUSE_HOST'),
)



class AnswerType(BaseModel):
    action: Literal['BRIGHTEN', 'DARKEN', 'REPAIR','NO_CHANGE_NEEDED', 'OTHER']

@observe()
class ChatService():
    def __init__(self, model='gpt-4o'):
        self.model = model
        self.openai_service = OpenAI(api_key=config('OPENAI_SEASON2_API_KEY'))

    def analyse_many_images(self, urls:list[str]):
        response = self.openai_service.chat.completions.create(
            model=self.model,
            messages = [
                {
                    'role':'system',
                    'content':'Describe please the person in these images. It should be Barbara. Please focus on her key characteristics. Describe her in a way that would make her recognizable. Write in Polish langguage!',
                },
                {
                    'role':'user',
                    'content': [
                        {
                            'type':'image_url',
                            'image_url': {
                                'url':url,
                            },
                        } for url in urls
                    ],
                },

            ],
        )
        return response.choices[0].message.content

    def analyse_image(self, url:str, system_prompt:str):
        response = self.openai_service.beta.chat.completions.parse(
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
            response_format=AnswerType,
        )
        return response.choices[0].message.parsed
    
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