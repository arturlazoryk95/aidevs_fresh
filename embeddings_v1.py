from ChatService import ChatService
from VectorService import VectorService
from tabulate import tabulate


def main():
    openai_service = ChatService()
    vector_service = VectorService(openai_service)

    # countries = [
    #     "Poland: Warsaw boasts a mix of medieval architecture and contemporary design elements.",
    #     "Belgium: Brussels is home to a thriving Belgian beer scene and delicious waffles.",
    #     "Croatia: Dubrovnik boasts beautiful stone walls and stunning views from atop City Walls.",
    #     "Czech Republic: Prague's iconic Charles Bridge is an architectural marvel adorned with statues of saints.",
    #     "Denmark: Copenhagen is known for its impressive harbor, canals, and the Little Mermaid statue.",
    #     "France: The Eiffel Tower in Paris is one of the most recognizable structures in the world.",
    #     "Germany: German efficiency and precision are evident in their punctual train networks and high-quality automotive industry.",
    #     "Greece: Ancient sites like the Acropolis in Athens provide a glimpse into Greek civilization's rich past.",
    #     "Hungary: Budapest is famous for its thermal baths, offering soothing and historical experiences.",
    #     "Ireland: Dublin boasts lively pubs and traditional music performances, where the spirit of 'The Craic' thrives.",
    #     "Italy: The Italian Renaissance left an indelible mark on art and architecture in cities like Florence, Rome, and Venice.",
    #     "Latvia: Riga's old town features Art Nouveau architecture that blends seamlessly into a modern cityscape.",
    #     "Luxembourg: Luxembourg City is known for its charming old town and stunning blend of French and German influences.",
    #     "Netherlands: The Netherlands is famous for its windmills, canals, and liberal social values.",
    #     "Norway: Norway is home to the picturesque fjords and dramatic landscapes that have inspired artists and adventurers for centuries.",
    #     "Portugal: Lisbon's colorful trams and Fado music, a melancholic traditional genre, create an authentic charm.",
    #     "Romania: Carpathian Mountains hold stunning castles, monasteries, and hiking trails, making it a popular destination for nature enthusiasts.",
    #     "Spain: Barcelona is famous for its vibrant art scene, world-renowned architecture (e.g., the Sagrada Familia), and lively nightlife.",
    #     "Sweden: Sweden is known for its high quality of life, especially for healthcare, education, and work-life balance.",
    # ]


    # for country_prompt in countries:
    #     messages = [
    #         {
    #             'role':'system',
    #             'content':'You are a helpful assistant. For each sentence please, return only 4 keywords including the name of the country based on this one sentences. Nothing else. Just these few keywords'
    #         },
    #         {
    #             'role':'user',
    #             'content':country_prompt
    #         }
    #     ]
    #     big_answer = openai_service.completion({'messages':messages})
    #     big_answer['country_prompt'] = country_prompt
    #     print(vector_service.add_points(big_answer['country_prompt'], big_answer))

    while True:

        query = input('What do you want to do on vacations: ')
        if query == 'exit':
            break
        results = vector_service.search(query).points
        table_data = []
        for result in results:
            country_prompt = result.payload.get('country_prompt', "N/A")
            keywords = result.payload.get('answer', "N/A")
            score = f'{result.score:.4f}'
            table_data.append([
                country_prompt, keywords, score
            ])
        print('\nSearch Results:')
        print(tabulate(
            tabular_data=table_data,
            headers=['Country Description', 'Keywords', 'Score'],
            tablefmt='grid',
            maxcolwidths = [50,30,10],
        ))
        print()



if __name__=='__main__':    
    main()

