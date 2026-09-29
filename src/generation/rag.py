import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


def generate_answer(query, documents):
    """
    Generate a grounded answer using retrieved document context.
    """

    context = "\n\n".join(
        document.page_content for document in documents
    )

    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
    )

    prompt = f"""
You are an enterprise document assistant.

Answer the user's question using ONLY the context below.

If the answer is not present in the context, say:
"I could not find enough information in the uploaded documents."

Context:
{context}

Question:
{query}

Answer:
"""

    response = llm.invoke(prompt)

    return response.content