import os
import re
import tempfile
import uuid

import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


def clean_filename(filename):
    """Strip '(number)' patterns from filenames so they're safe as Chroma collection names."""
    return re.sub(r"\s\(\d+\)", "", filename)


def get_pdf_text(uploaded_file):
    """Load an uploaded PDF (Streamlit UploadedFile) and return a list of Document objects."""
    try:
        input_file = uploaded_file.read()
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(input_file)
        temp_file.close()

        loader = PyPDFLoader(temp_file.name)
        return loader.load()
    finally:
        os.unlink(temp_file.name)


def split_document(documents, chunk_size, chunk_overlap):
    """Split documents into overlapping chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    return text_splitter.split_documents(documents)


def get_embedding_function():
    """Local sentence-transformers embeddings — no API key required."""
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def create_vectorstore(chunks, embedding_function, file_name, vector_store_path="db"):
    """Build a Chroma vector store from chunks, deduping by content hash."""
    ids = [str(uuid.uuid5(uuid.NAMESPACE_DNS, doc.page_content)) for doc in chunks]

    seen = set()
    unique_chunks = []
    unique_ids = []
    for chunk, _id in zip(chunks, ids):
        if _id not in seen:
            seen.add(_id)
            unique_chunks.append(chunk)
            unique_ids.append(_id)

    return Chroma.from_documents(
        documents=unique_chunks,
        collection_name=clean_filename(file_name),
        embedding=embedding_function,
        ids=unique_ids,
        persist_directory=vector_store_path,
    )


def create_vectorstore_from_texts(documents, file_name):
    """End-to-end: split documents, embed, and build a Chroma store."""
    docs = split_document(documents, chunk_size=1000, chunk_overlap=200)
    embedding_function = get_embedding_function()
    return create_vectorstore(docs, embedding_function, file_name)


def load_vectorstore(file_name, vectorstore_path="db"):
    """Load a previously created Chroma store from disk."""
    embedding_function = get_embedding_function()
    return Chroma(
        persist_directory=vectorstore_path,
        embedding_function=embedding_function,
        collection_name=clean_filename(file_name),
    )


PROMPT_TEMPLATE = """
You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer
the question. If you don't know the answer, say that you
don't know. DON'T MAKE UP ANYTHING.

{context}

---

Answer the question based on the above context: {question}
"""


class ExtractedInfoWithSources(BaseModel):
    """Extracted information about the research article."""

    paper_title: str = Field(..., description="The title of the paper, or 'Not specified' if unknown.")
    paper_summary: str = Field(..., description="A concise summary of the paper.")
    publication_year: str = Field(..., description="The year the paper was published, or 'Not specified' if unknown.")
    paper_authors: str = Field(..., description="The authors of the paper, or 'Not specified' if unknown.")
    sources: str = Field(..., description="Direct text from the context supporting the extracted information.")
    reasoning: str = Field(..., description="Reasoning behind the extracted information.")


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def query_document(vectorstore, query, api_key=None):
    """Run a structured RAG query and return the result as a transposed DataFrame."""
    groq_api_key = api_key or os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError(
            "No Groq API key found. Set GROQ_API_KEY in .env or pass api_key explicitly."
        )

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        api_key=groq_api_key,
    )

    retriever = vectorstore.as_retriever(search_type="similarity")
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt_template
        | llm.with_structured_output(ExtractedInfoWithSources)
    )

    structured_response = rag_chain.invoke(query)
    df = pd.DataFrame([structured_response.model_dump()])
    return df.T.rename(columns={0: "Value"})
