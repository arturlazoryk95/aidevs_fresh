from ChatService import ChatService
import requests
from decouple import config
import json

def construct_zapytanie(query):
    zapytanie = {
        'task':'database',
        'apikey':config('AIDEVS3_API_KEY'),
        'query':query
    }
    return zapytanie

def main():
    openai_service = ChatService()

    with open('s3e3_prompt.md', 'r') as file:
        system_prompt = file.read()

    messages = [
        {
            'role':'system',
            'content':system_prompt,
        },
        {
            'role':'user',
            'content':'start'
        }
    ]

    # while True:
    #     circuit = input('Can we continue? y/n: ')
    #     if circuit == 'n':
    #         break
    #     else:
    #         url = 'https://centrala.ag3nts.org/apidb'
            
    #         query = openai_service.completion({'messages':messages})['answer']
    #         print(f'Model: {query}')
    #         new_assistant_message = {
    #             'role':'assistant',
    #             'content':query
    #         }
    #         messages.append(new_assistant_message)
    #         zapytanie = construct_zapytanie(query)
    #         request_to_db = requests.post(url=url, data=json.dumps(zapytanie))
    #         print(f'SYSTEM: {request_to_db.text}')
    #         new_answer = {
    #             'role':'user',
    #             'content':request_to_db.text
    #         }
    #         messages.append(new_assistant_message)
    #         messages.append(new_answer)

    # print(messages)
    answers = {
        'task':'database',
        'apikey':config('AIDEVS3_API_KEY'),
        'answer':[4278, 9294]
    }
    response = requests.post(url='https://centrala.ag3nts.org/report',data=json.dumps(answers))
    print(response.text)
            
            




if __name__=='__main__':
    main()