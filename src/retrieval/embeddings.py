from langchain_huggingface import HuggingFaceEmbeddings


def get_embeddings():
    """
    Create the embedding model used for semantic search.
    """

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )