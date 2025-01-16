import os
from langfuse.decorators import observe, langfuse_context
from langfuse.openai import OpenAI
from decouple import config
import json
import requests
import pprint

# Set up
langfuse_context.configure(
    public_key=config('LANGFUSE_PUBLIC_KEY'),
    secret_key=config('LANGFUSE_SECRET_KEY'),
    host=config('LANGFUSE_HOST'),
)

client = OpenAI(
    api_key=config('OPENAI_SEASON2_API_KEY')
)

def construct_memory_base():
    memory_base = ''
    folder_path = 'pliki_z_fabryki'
    with open('prompts/s3e1_prompt.md', 'r') as file:
        prompt = file.read()

    facts_folder_path = f'{folder_path}/facts'
    facts_folder = os.listdir(facts_folder_path)
    for file in facts_folder:
        file_path = f'{facts_folder_path}/{file}'
        with open(file_path, 'r') as f:
            content = f.read()
        memory_base += f'# ---Fact Name: {file}---\n'
        # memory_base += f'## ---Content End of {file}---\n\n'
        keywords = analyse_text_keywords(f'{prompt}\n{content}', content)
        memory_base += f'## ---Keywords of{file}---\n{keywords}\n'
        memory_base += f'## ---Keywords of{file}---\n\n'

  

    return memory_base

def supply_txt_files():
    memory_base = ''
    pliki_folder = os.listdir('pliki_z_fabryki/')
    with open('prompts/s3e1_prompt.md', 'r') as file:
        prompt = file.read()

    for file in pliki_folder:
        if file.endswith('txt'):
            # print(file)
            file_path = f'pliki_z_fabryki/{file}'
            with open(file_path, 'r') as f:
                content = f.read()
            memory_base += f'# ---File Name: {file}---\n{content}\n'
            memory_base += f'## ---Content End of {file}---\n\n'
            keywords = analyse_text_keywords(f'{prompt}\n{content}', content)
            memory_base += f'## ---Keywords of{file}---\n{keywords}\n'
            memory_base += f'## ---Keywords of{file}---\n\n'


    return memory_base

def construct_the_database():
    memory_base = '# MEMORY_BASE: \n\n'
    memory_base+= construct_memory_base()
    # memory_base+= supply_txt_files()
    return memory_base



@observe()
def analyse_text_keywords(prompt, user_prompt):
    response = client.chat.completions.create(
        model = 'gpt-4o',
        messages= [
            {
                'role':'system',
                'content':prompt
            },
            {
                'role':'user',
                'content':user_prompt
            },
        ]
    )  
    return response.choices[0].message.content


def main():
    # MEMORY = construct_the_database()
    # with open('tmp_files/MEMORY.md', 'w') as file:
    #     file.write(MEMORY)
    with open('tmp_files/MEMORY.md', 'r') as file:
        MEMORY = file.read()
    
    with open('prompts/s3e1_prompt.md', 'r') as file:
        prompt = file.read()
    
    questions_folder_path = 'pliki_z_fabryki'

    answers = {}

    for file in os.listdir(questions_folder_path):
        if file.endswith('txt'):
           
            file_path = f'{questions_folder_path}/{file}'
            user_prompt = file
            with open(file_path, 'r') as f:
                user_prompt += f.read()
            
            keywords = analyse_text_keywords(prompt=f'{prompt}\n{MEMORY}', user_prompt=user_prompt)            
            answers[file]=keywords


    pprint.pprint(answers, indent=4)
    
    json_answer = answers
    to_be_sent = {
        'task':'dokumenty',
        'apikey': config('AIDEVS3_API_KEY'),
        'answer':json_answer,
    }
    response = requests.post('https://centrala.ag3nts.org/report',data=json.dumps(to_be_sent))
    print(response.text)

if __name__=='__main__':
    main()