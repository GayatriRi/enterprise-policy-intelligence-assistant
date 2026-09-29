from io import BytesIO

import pandas as pd
from pypdf import PdfReader
from langchain_core.documents import Document


def load_pdf(uploaded_file):
    """Extract text from an uploaded PDF file."""
    reader = PdfReader(BytesIO(uploaded_file.getvalue()))
    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text and text.strip():
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": uploaded_file.name,
                        "file_type": "pdf",
                        "page": page_number,
                    },
                )
            )

    return documents


def load_txt(uploaded_file):
    """Read text from an uploaded TXT file."""
    text = uploaded_file.getvalue().decode("utf-8", errors="replace")

    if not text.strip():
        return []

    return [
        Document(
            page_content=text,
            metadata={
                "source": uploaded_file.name,
                "file_type": "txt",
            },
        )
    ]


def load_csv(uploaded_file):
    """Read an uploaded CSV file."""
    dataframe = pd.read_csv(BytesIO(uploaded_file.getvalue()))

    if dataframe.empty:
        return []

    text = dataframe.to_csv(index=False)

    return [
        Document(
            page_content=text,
            metadata={
                "source": uploaded_file.name,
                "file_type": "csv",
            },
        )
    ]


def load_excel(uploaded_file):
    """Read all sheets from an uploaded Excel workbook."""
    workbook = pd.read_excel(
        BytesIO(uploaded_file.getvalue()),
        sheet_name=None,
    )

    documents = []

    for sheet_name, dataframe in workbook.items():
        if dataframe.empty:
            continue

        text = dataframe.to_csv(index=False)

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": uploaded_file.name,
                    "file_type": "excel",
                    "sheet": sheet_name,
                },
            )
        )

    return documents


def load_document(uploaded_file):
    """
    Select the correct loader based on the uploaded file extension.
    """
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return load_pdf(uploaded_file)

    if filename.endswith(".txt"):
        return load_txt(uploaded_file)

    if filename.endswith(".csv"):
        return load_csv(uploaded_file)

    if filename.endswith((".xlsx", ".xls")):
        return load_excel(uploaded_file)

    raise ValueError(
        f"Unsupported file type: {uploaded_file.name}"
    )