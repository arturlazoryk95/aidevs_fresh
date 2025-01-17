from decouple import config
import asyncio
from typing import List, Dict
from tabulate import tabulate
from openai_service import OpenAIService
from vector_service import VectorService
from text_service import TextSplitter

# Sample data - similar to your TypeScript example
data = [
    {"author": "Jim Collins", "text": "Good to Great: \"Good is the enemy of great. To go from good to great requires transcending the curse of competence.\""},
    {"author": "Jim Collins", "text": "Built to Last: \"Clock building, not time telling. Focus on building an organization that can prosper far beyond the presence of any single leader and through multiple product life cycles.\""},
    {"author": "Jim Collins", "text": "Great by Choice: \"20 Mile March. Achieve consistent performance markers, in good times and bad, as a way to build resilience and maintain steady growth.\""},
    {"author": "Simon Sinek", "text": "Start with Why: \"People don't buy what you do; they buy why you do it. And what you do simply proves what you believe.\""},
    {"author": "Simon Sinek", "text": "Leaders Eat Last: \"The true price of leadership is the willingness to place the needs of others above your own.\""}
]

COLLECTION_NAME = "aidevs"

async def initialize_data(
    text_splitter: TextSplitter,
    vector_service: VectorService
) -> None:
    """Initialize the vector database with document data"""
    points = []
    for item in data:
        doc = await text_splitter.document(
            item['text'],
            'gpt-4',
            {'author': item['author']}
        )
        points.append(doc)
    
    await vector_service.initialize_collection_with_data(COLLECTION_NAME, points)

async def main():
    # Initialize services
    openai_service = OpenAIService()
    vector_service = VectorService(openai_service)
    text_splitter = TextSplitter()

    # Example query
    query = "What do Sinek and Collins say about working with people?"

    # Initialize database with sample data
    await initialize_data(text_splitter, vector_service)

    # Determine relevant authors
    author_response = await openai_service.completion({
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that determines the author(s) of a given text. "
                          "Pick between Jim Collins and Simon Sinek. If both are relevant, list them "
                          "comma-separated. Write back with the name(s) and nothing else."
            },
            {
                "role": "user",
                "content": query
            }
        ]
    })

    authors = author_response.choices[0].message.content.split(',')
    authors = [author.strip() for author in authors]

    # Create filter for vector search
    filter_condition = {
        "should": [
            {
                "key": "author",
                "match": {"value": author}
            }
            for author in authors
        ]
    } if authors else None

    # Perform vector search
    search_results = await vector_service.perform_search(
        COLLECTION_NAME,
        query,
        filter_condition,
        15
    )

    # Check relevance of results
    relevant_results = []
    for result in search_results:
        relevance_check = await openai_service.completion({
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that determines if a given text is relevant "
                              "to a query. Respond with 1 if relevant, 0 if not relevant."
                },
                {
                    "role": "user",
                    "content": f"Query: {query}\nText: {result.payload['text']}"
                }
            ]
        })
        
        is_relevant = relevance_check.choices[0].message.content == '1'
        if is_relevant:
            relevant_results.append(result)

    # Display results
    print(f"\nQuery: {query}")
    print(f"Author(s): {', '.join(authors)}")
    
    # Format results for display
    table_data = [
        {
            'Author': result.payload.get('author', ''),
            'Text': result.payload.get('text', '')[:45] + '...',
            'Score': result.score
        }
        for result in relevant_results
    ]
    
    print("\nRelevant Results:")
    print(tabulate(table_data, headers='keys', tablefmt='grid'))

if __name__ == "__main__":
    asyncio.run(main())
