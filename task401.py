import requests
from CentralaService import CentralaService
import json
import pprint
from VisualAIService import ChatService
import re

PHOTOS_URL = 'https://centrala.ag3nts.org/dane/barbara/'
PHOTOS_NAMES = ['IMG_559.PNG', 'IMG_1410.PNG', 'IMG_1443.PNG', 'IMG_1444.PNG']
PHOTOS_COMMANDS = ['REPAIR', 'DARKEN', 'BRIGHTEN']



def parse_ai_response(response:str) -> tuple[str, str]:
    pattern = r'<change>(.*?)</change>'
    match = re.search(pattern, response)
    if match:
        return 'change', match.group(1)
    
    pattern = r'<answer>(.*?)</answer>'
    match = re.search(pattern, response)
    if match:
        return 'answer', match.group(1)
    
    return 'none', ''
    

def main():
    centrala = CentralaService()
    openai_service = ChatService()
    with open('prompts/visual_prompt.md', 'r') as file:
        system_prompt = file.read()

    
    j=0
    rysopis_barbary = ''
    for j in range(0, 4):

        name_photo = PHOTOS_NAMES[j]
        print(f'IMAGE: {name_photo}')
        print('-'*50)
        i=1
        while True:
            if(i==5):
                break
    

            answer = openai_service.analyse_image(
                url=PHOTOS_URL+name_photo,
                system_prompt=system_prompt,
            )
            print(answer)
            response_type, response = parse_ai_response(answer)
            print(response_type, response)
            print('-'*50)
            if response_type == 'change':
                new_response = centrala.handle_submits(
                    task='photos',
                    answer=response+' '+name_photo,
                )
                print(new_response)
                name_photo = openai_service.extractImageName(new_response['message'])
                if name_photo == 'None':
                    break
                print(name_photo)
                i+=1
            elif response_type == 'answer':
                print(response)
                rysopis_barbary += response + '\n'
                break
            else:
                break
            print('='*50)
        j+=1
    
    submit = centrala.handle_submits(
        task='photos',
        answer=rysopis_barbary,
    )
    print(submit)





if __name__=='__main__':
    main()