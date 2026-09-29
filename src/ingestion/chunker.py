from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents):
    """
    Split loaded documents into smaller chunks for semantic search.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = text_splitter.split_documents(documents)

    return chunks
