from ChatService import ChatService
from VectorService import VectorService
import json
import os
import re
from uuid import uuid4
from tabulate import tabulate
import requests
from decouple import config



def main():
    openai_service = ChatService()
    collection_name = 'aidevs_weapons'
    vector_service = VectorService(collection_name, openai_service)

    files_folder_path = 'pliki_z_fabryki/do-not-share/'
    my_reports = []
    for file in os.listdir(files_folder_path):
        file_path = f'{files_folder_path}{file}'
        date = re.search(r'(\d{4})_(\d{2})_(\d{2})', file)
        real_date = f'{date.group(1)}-{date.group(2)}-{date.group(3)}'
        with open(file_path, 'r') as f:
            content = f.read()

        new_article={
            'id':str(uuid4()),
            'article_date':real_date,
            'content':content[:50],
            'embedding':openai_service.create_embedding(content),
        }   
        my_reports.append(new_article)
        # vector_service.add_points(new_article['content'], new_article)

    query = 'W raporcie, z którego dnia znajduje się wzmianka o kradzieży prototypu broni?'
    results = vector_service.search(query).points
    table = []
    for result in results:
        date = result.payload.get('article_date', "N/A")
        content = result.payload.get('content', "N/A")
        score = f'{result.score:.4f}'
        table.append([date,content,score])
    # print(tabulate(
    #     tabular_data=table,
    #     headers=['Date', 'Content', 'Score'],
    #     tablefmt='grid',
    #     maxcolwidths=[50,30,10]

    # ))
    # print()
    print(results[0].payload['article_date'])
    answers = {
        'task':'wektory',
        'apikey':config('AIDEVS3_API_KEY'),
        'answer':results[0].payload['article_date'],
    }
    response = requests.post(url='https://centrala.ag3nts.org/report',data=json.dumps(answers))
    print(response.text)


if __name__=='__main__':
    main()