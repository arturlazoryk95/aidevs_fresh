# 1. INITIAL INPUT DATA
# This could come from your database, files, or API
initial_documents = [
    {
        "text": "The flywheel effect shows that success requires consistent effort in one direction. Companies that maintain steady progress over time build unstoppable momentum.",
        "metadata": {
            "author": "Jim Collins",
            "source": "Good to Great",
            "chapter": "The Flywheel Effect",
            "page": 164
        }
    },
    {
        "text": "Great companies focus on 'clock building' not 'time telling.' They create organizational structures and processes that last beyond any single leader or product.",
        "metadata": {
            "author": "Jim Collins",
            "source": "Built to Last",
            "chapter": "Clock Building",
            "page": 23
        }
    }
]

# 2. CONVERSION TO DOCUMENT OBJECTS
# The Document objects now contain the text and metadata in a structured format
documents = [
    Document(
        text=doc["text"],
        metadata=doc["metadata"]
    )
    for doc in initial_documents
]

# Example of what documents look like now:
"""
[
    Document(
        text="The flywheel effect shows that success requires consistent effort...",
        metadata={
            "author": "Jim Collins",
            "source": "Good to Great",
            "chapter": "The Flywheel Effect",
            "page": 164
        }
    ),
    Document(
        text="Great companies focus on 'clock building' not 'time telling.'...",
        metadata={
            "author": "Jim Collins",
            "source": "Built to Last",
            "chapter": "Clock Building",
            "page": 23
        }
    )
]
"""

# 3. DOCUMENT RANKING
# When user asks: "What does Jim Collins say about building lasting success?"
# _rank_documents() creates this:
ranked_documents = [
    (9.5, Document(text="Great companies focus on 'clock building'...", metadata={...})),  # High relevance
    (7.2, Document(text="The flywheel effect shows that success...", metadata={...}))      # Lower relevance
]

# 4. CONTEXT BUILDING
# _build_context() transforms ranked documents into this string:
context_string = """
[author: Jim Collins, source: Built to Last, chapter: Clock Building, page: 23]
Great companies focus on 'clock building' not 'time telling.' They create organizational structures and processes that last beyond any single leader or product.

[author: Jim Collins, source: Good to Great, chapter: The Flywheel Effect, page: 164]
The flywheel effect shows that success requires consistent effort in one direction. Companies that maintain steady progress over time build unstoppable momentum.
"""

# 5. SYSTEM PROMPT CREATION
# create_system_prompt() produces this:
system_prompt = """You are a helpful assistant with access to a specific knowledge base. 
Answer questions based only on the following information:

[author: Jim Collins, source: Built to Last, chapter: Clock Building, page: 23]
Great companies focus on 'clock building' not 'time telling.' They create organizational structures and processes that last beyond any single leader or product.

[author: Jim Collins, source: Good to Great, chapter: The Flywheel Effect, page: 164]
The flywheel effect shows that success requires consistent effort in one direction. Companies that maintain steady progress over time build unstoppable momentum.

If the provided information is not sufficient to answer the question, say so.
Base your answers solely on the provided context, not on any other knowledge.
Always cite specific parts of the text to support your answers."""

# 6. FINAL QUERY TO OPENAI
# query_with_context() sends this to OpenAI:
openai_messages = [
    {
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": "What does Jim Collins say about building lasting success?"
    }
]

# 7. OPENAI RESPONSE
# The response might look like:
response = """According to the provided texts, Jim Collins presents two key concepts for building lasting success:

1. The importance of "clock building" over "time telling" (from Built to Last): Companies should focus on creating enduring organizational structures and processes rather than relying on individual leaders or products. As the text states, these structures should "last beyond any single leader or product."

2. The flywheel effect (from Good to Great): Success comes from "consistent effort in one direction" and maintaining "steady progress over time" which builds "unstoppable momentum." This emphasizes the importance of sustained, focused effort rather than sporadic changes in direction.

Both concepts emphasize building sustainable, long-term success through systematic approaches rather than quick fixes or individual heroics."""
