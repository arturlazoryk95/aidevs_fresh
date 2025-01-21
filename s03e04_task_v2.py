from openai import OpenAI
from decouple import config
import json
import re
import requests


class ChatService():
    def __init__(self, model_name: str = 'gpt-4o-mini'):
        self.chat_service = OpenAI(api_key=config('OPENAI_SEASON2_API_KEY'))
        self.model = model_name

    def completion(self, system_prompt:str, query:str, max_tokens:int = 10000) -> str:
        response = self.chat_service.chat.completions.create(
            model = self.model,
            max_tokens = max_tokens,
            messages = [
                {
                    'role':'system',
                    'content':system_prompt,
                },
                {
                    'role':'user',
                    'content':query,
                }
            ]
        )
        return response.choices[0].message.content
    
    def response_parser(self, generated_response: str) -> tuple[str, str]:
        response_type = ''
        answer_pattern = r'<answer>(.*?)</answer>'
        people_pattern = r'<people>(.*?)</people'
        places_pattern = r'<places>(.*?)</places>'
        response_type = 'No matches.'
        response_text = "N/A"
        match = re.match(answer_pattern, generated_response)
        if match:
            response_type = 'answer'
            response_text = match.group(1)
        match = re.match(people_pattern, generated_response)
        if match:
            response_type = 'people'
            response_text = match.group(1)
        match = re.match(places_pattern, generated_response)
        if match:
            response_type = 'places'
            response_text = match.group(1)
            
        return self.replace_polish_letters(response_text), response_type
    
    def replace_polish_letters(self, text):
        replacements = {
            'Ł': 'L', 'ł': 'l',
            'Ą': 'A', 'ą': 'a',
            'Ć': 'C', 'ć': 'c',
            'Ę': 'E', 'ę': 'e',
            'Ń': 'N', 'ń': 'n',
            'Ó': 'O', 'ó': 'o',
            'Ś': 'S', 'ś': 's',
            'Ź': 'Z', 'ź': 'z',
            'Ż': 'Z', 'ż': 'z'
        }
        for polish, ascii in replacements.items():
            text = text.replace(polish, ascii)
        return text
        





class Centrala():
    def __init__(self):
        self.url_to_report = 'https://centrala.ag3nts.org/report'
        self.url_for_people = 'https://centrala.ag3nts.org/people'
        self.url_for_places = 'https://centrala.ag3nts.org/places'
        self.api_key = config('AIDEVS3_API_KEY')  

    def route_requests(self, query:str, request_type:str) -> dict[str, any]:
        if request_type == 'people':
            return self.handle_people_requests(query)
        elif request_type == 'places':
            return self.handle_places_requests(query)
        elif request_type == 'answer':
            return self.handle_submits(query)

    def handle_people_requests(self, person: str) -> dict[str, any]:
        data_for_send = {
            'apikey':self.api_key,
            'query':person,
        }
        response = requests.post(url=self.url_for_people, data=json.dumps(data_for_send))
        return response.json()

    def handle_places_requests(self, place: str) -> dict[str, any]:
        data_for_send = {
            'apikey':self.api_key,
            'query':place,
        }
        response = requests.post(url=self.url_for_places, data=json.dumps(data_for_send))
        return response.json()

    def handle_submits(self, answer: str) -> dict[str, any]:
        data_for_send = {
            'task':'loop',
            'apikey':self.api_key,
            'answer':answer,
        }
        response = requests.post(url=self.url_to_report, data=json.dumps(data_for_send))
        return response.json()
    

class Detective():
    def __init__(self, system_prompt_path:str, knowledge_path:str, base_knowledge_path:str):
        with open(knowledge_path, 'r') as file:
            self.knowledge = file.read()

        with open(base_knowledge_path, 'r') as file:
            self.knowledge = self.knowledge.replace(
                '</base_kwnoledge>',
                f'{file.read()}\n</base_kwnoledge>'
            )
        
        with open(system_prompt_path, 'r') as file:
            self.system_prompt = file.read()

    def just_update(self, query:str, code:int, message:dict):
        self.update_do_not_ask_again(query)
        if code == 0:
            self.update_relationships(query, message)
        else:
            self.update_additional(query, message)

    def update_do_not_ask_again(self, do_not_ask_again: str):
        self.knowledge = self.knowledge.replace(
            '</do_not_ask_again>',
            f'{do_not_ask_again}\n</do_not_ask_again>'
        )

    def update_relationships(self, query:str, relationships: str):
        self.knowledge = self.knowledge.replace(
            '</relationships_between_people_and_places>',
            f'{query}: {relationships}\n</relationships_between_people_and_places>'
        )

    def update_additional(self, query:str, response: str):
        self.knowledge = self.knowledge.replace(
            '</additional_knowledge>',
            f'{query}: {response}\n</additional_knowledge>'
        )



def main():

    chat_service = ChatService('gpt-4o')
    centrala = Centrala()
    detective = Detective(
        system_prompt_path='prompts/claude_prompt.md', 
        knowledge_path='prompts/s3eo4_knowledge.md', 
        base_knowledge_path='text.txt'
    )
    
    while True:
        generated_response = chat_service.completion(detective.system_prompt, detective.knowledge)
        response_text, response_type = chat_service.response_parser(generated_response)
        print(f'Generated Response: {generated_response} -> {response_type}:{response_text}')
        print(f'Doing now the handling of <{response_type}> ... ')
        the_answer_json = centrala.route_requests(response_text, response_type)
        # print(the_answer_json)

        
        print(f"... We got this: {the_answer_json['code']}|{the_answer_json['message']}")
        if 'FLG' in the_answer_json['message']:
            print(f"WE FOUND IT!!! {the_answer_json['message']}")
            break

        code = the_answer_json['code']
        message = the_answer_json['message'].split()
        detective.just_update(response_text, code, message)
        print('Knowledge has been updated.')



if __name__=='__main__':
    main()