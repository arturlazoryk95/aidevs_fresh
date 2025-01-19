from ChatService import ChatService
from VectorService import VectorService
import json



def main():
    openai_service = ChatService()
    vector_service = VectorService(openai_service)
    

if __name__=='__main__':
    main()