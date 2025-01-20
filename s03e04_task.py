from decouple import config
import json
from openai import OpenAI
from pydantic import BaseModel
import requests


class People(BaseModel):
    names: list[str]

class Places(BaseModel):
    city_names: list[str]

class OnlyBool(BaseModel):
    barbara_found: bool

class ChatService():

    def __init__(self, model:str = 'gpt-4o-mini'):
        self.openai_service = OpenAI(api_key=config('OPENAI_SEASON2_API_KEY'))
        self.searched_places: list[dict] = []
        self.searched_people: list[dict] = []
        self.model = model
        self.people_prompt = 'Extract people names (only first name) from the text. Do not use Polish letters. Always return nouns in "mianownik".'
        self.places_prompt = 'Extract city names from the text. Do not use Polish letters. Always return nouns in "mianownik".'
        self.barbara_prompt = 'Based on text, are we certain 100% that Barbara Zawadzka is located in this city?'

    def extract_info(self, system_prompt: str, text_input: str, object_type):
        completion = self.openai_service.beta.chat.completions.parse(
            model=self.model,
            messages = [
                {
                    'role':'system',
                    'content': system_prompt,
                },
                {
                    'role':'user',
                    'content':text_input,
                },
            ],
            response_format = object_type
        )
        parsed_data = completion.choices[0].message.parsed
        
        if isinstance(parsed_data, People):  # Ensure names are uppercase
            parsed_data.names = [self.replace_polish_letters(name.upper()) for name in parsed_data.names]
        
        elif isinstance(parsed_data, Places):  # Ensure city names are uppercase
            parsed_data.city_names = [self.replace_polish_letters(city.upper()) for city in parsed_data.city_names]
        
        return parsed_data
    
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
        self.report_url = 'https://centrala.ag3nts.org/report'
        self.people_url = 'https://centrala.ag3nts.org/people'
        self.places_url = 'https://centrala.ag3nts.org/places'
        self.api_key = config('AIDEVS3_API_KEY')

    def submit_answer(self, task_name:str, answer_data:str) -> str:
        answer = {
            'task':task_name,
            'apikey':self.api_key,
            'answer':answer_data,
        }
        response = requests.post(
            url=self.report_url,
            data=json.dumps(answer)
        )
        return response.text
    
    def get_people_info(self, query_text:str) -> str:
        answer = {
            'apikey':self.api_key,
            'query':query_text,
        }
        response = requests.post(
            url=self.people_url,
            data=json.dumps(answer)
        )
        data = response.json()
        text = data['message']
        return self.replace_polish_letters(text).split()
    
    def get_places_info(self, query_text:str) -> str:
        answer = {
            'apikey':self.api_key,
            'query':query_text,
        }
        response = requests.post(
            url=self.places_url,
            data=json.dumps(answer)
        )
        data = response.json()
        text = data['message']
        return self.replace_polish_letters(text).split()
   
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



def main():
    openai_service = ChatService()
    centrala = Centrala()

    with open('text.txt', 'r') as file:
        text_input = file.read()

    people_tmp = openai_service.extract_info(openai_service.people_prompt, text_input, People).names
    places = openai_service.extract_info(openai_service.places_prompt, text_input, Places).city_names
    
    people_searches = []
    city_searches = []
    i=0
    
    people = []
    for p in people_tmp:
        if p != 'BARBARA':
            people.append(p)
    
    # print(people)
    # print(places)
        

    while True:
        for place in places:
            if place not in city_searches:
                print(f'Searching now in {place}:')
                new_people = centrala.get_places_info(place)
                print(f'Found these people: {new_people}')
                if 'FLG' in new_people:
                    print(f'FOUND: {place}!!')
                    break
                else:
                    for new_person in new_people:
                        if new_person not in people:
                            people.append(new_person)
                for person in people:
                    if person not in people_searches:
                        print(f'Searching now for {person}:')
                        new_places = centrala.get_people_info(person)
                        print(f'Found these places: {new_places}')
                        for new_place in new_places:
                            if new_place not in places:
                                places.append(new_place)
                        people_searches.append(person)
                city_searches.append(place)
                print('\n\n')

    print(centrala.submit_answer('loop','ELBLAG'))
            

if __name__ == '__main__':
    main()
