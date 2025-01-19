from ChatService import ChatService
from VectorService import VectorService

def main():
    openai_service = ChatService()
    vector_service = VectorService(openai_service)
    prompt = input('Insert prompt: ')
    messages = [
        {
            'role':'system',
            'content':'You are a helpful assistant. Please respond with emojis where applicable :)'
        },
        {
            'role':'user',
            'content':prompt
        }
    ]
    big_answer = openai_service.completion({'messages':messages})
    print(big_answer['answer'])
    
    # BIG_ANSWER OUTPUT:
    # ------------------------------------------------------------------------------------------
    # return {
    #         'answer':answer.choices[0].message.content,
    #         'input_tokens':input_tokens,
    #         'output_tokens':output_tokens,
    #         'total_spend': f'{input_tokens*self.input_price+output_tokens*self.output_price}$',
    # }

    print(vector_service.add_points(big_answer['answer'], big_answer))
    
    

if __name__=='__main__':    
    main()

