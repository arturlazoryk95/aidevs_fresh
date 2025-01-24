import requests
from CentralaService import CentralaService
import json
import pprint
from VisualAIService import ChatService
import re
from langfuse.decorators import observe, langfuse_context
from decouple import config

PHOTOS_URL = 'https://centrala.ag3nts.org/dane/barbara/'
PHOTOS_NAMES = ['IMG_559.PNG', 'IMG_1410.PNG', 'IMG_1443.PNG', 'IMG_1444.PNG']
PHOTOS_COMMANDS = ['REPAIR', 'DARKEN', 'BRIGHTEN']

langfuse_context.configure(
    public_key=config('LANGFUSE_PUBLIC_KEY'),
    secret_key=config('LANGFUSE_SECRET_KEY'),
    host=config('LANGFUSE_HOST'),
)

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
    


@observe()
def main():
    centrala = CentralaService()
    openai_service = ChatService()
    with open('prompts/visual_prompt.md', 'r') as file:
        system_prompt = file.read()

    final_images = ['IMG_559_NRR7.PNG', 'IMG_1410_FXER.PNG', 'IMG_1443_FT12.PNG', 'IMG_1444.PNG']
    # for photo in PHOTOS_NAMES:

    #     photo_name = photo
    #     print('New photo: ', photo_name)
    #     print('-'*50)   
    #     while True:
    #         answer = openai_service.analyse_image(PHOTOS_URL+photo_name, system_prompt)
    #         print('Model suggests: ', answer.action)
    #         if answer.action == 'NO_CHANGE_NEEDED':
    #             print('No action needed')
    #             final_images.append(photo_name)
    #             break
    #         else:
    #             response = centrala.handle_submits('photos', answer.action+' '+photo_name)
    #             print('Centrala says: ', response['message'])
    #             found_new_image = openai_service.extractImageName(response['message'])
    #             if found_new_image == 'None':
    #                 print('No image name found.')
    #                 final_images.append(photo_name)
    #                 break
    #             else:
    #                 print('Found new image:', found_new_image)
    #                 photo_name = found_new_image
            
    
    # print('Final images:', final_images)
    # response = openai_service.analyse_many_images([PHOTOS_URL+photo for photo in final_images])
    # print('Final response:', response)

    final_response = 'Nie wiem, kto to jest. Opisując osobę na zdjęciach, mogę powiedzieć, że to kobieta o długich, ciemnych włosach, nosząca okulary. Wydaje się, że ma na sobie szary t-shirt, a na jednym ze zdjęć widać tatuaż z pająkiem na ramieniu. Na jednym z obrazów kobieta trzyma kubek, a na innym znajduje się w siłowni.'
    
    an = centrala.handle_submits('photos', final_response)
    print(an)


if __name__=='__main__':
    main()