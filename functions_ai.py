from langfuse.decorators import observe, langfuse_context
from langfuse.openai import OpenAI
from decouple import config
from pathlib import Path



langfuse_context.configure(
    public_key=config('LANGFUSE_PUBLIC_KEY'),
    secret_key=config('LANGFUSE_SECRET_KEY'),
    host=config('LANGFUSE_HOST'),
)

client = OpenAI(api_key=config('OPENAI_SEASON2_API_KEY'))

@observe()
def analyse_text(prompt, content):
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {
                'role': 'system', 
                'content': prompt
            },
            {
                'role': 'user', 
                'content': content
            },
        ],
        max_tokens=10000,

    )
    return response.choices[0].message.content

def get_prompt(file_path):
    with open(file_path, 'r') as file:
        return file.read()

@observe()
def get_transcription(file_path):
    audio_file = Path(file_path)
    with open(audio_file, "rb") as file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=file
        )
    return transcription.text

@observe()
def analyse_image(url, context):
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {
                'role': 'system', 
                'content': f'Analyse the following image based on the below context. Write just 1 sentence about the image. The context: {context}'
            },
            {
                'role': 'user', 
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
        max_tokens=10000,

    )
    return response.choices[0].message.content



@observe()
def really_answer_the_questions(prompt, questions):
    response = client.chat.completions.create(
        model = 'gpt-4o-mini',
        response_format = {
            "type": "json_object" 
        },
        messages=[
            {
                'role':'system',
                'content':prompt,
            },
            {
                'role':'user',
                'content':questions
            },
        ]
    )
    return response.choices[0].message.content
