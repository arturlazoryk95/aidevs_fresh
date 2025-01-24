import requests
from decouple import config
import json

class CentralaService():
    def __init__(self):
        self.url_to_report = 'https://centrala.ag3nts.org/report'
        self.api_key = config('AIDEVS3_API_KEY')  

    def handle_submits(self,task:str, answer: str) -> dict[str, any]:
        data_for_send = {
            'task':task,
            'apikey':self.api_key,
            'answer':answer,
        }
        response = requests.post(url=self.url_to_report, data=json.dumps(data_for_send))
        return response.json()
    
    
    