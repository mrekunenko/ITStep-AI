# tools.py
import os
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore

PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "omegamed-v3")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY не знайдено у .env")


def _get_vector_store() -> PineconeVectorStore:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GEMINI_API_KEY,
        task_type="retrieval_query"
    )

    return PineconeVectorStore.from_existing_index(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings,
        namespace=PINECONE_NAMESPACE,
    )


try:
    import streamlit as st


    @st.cache_resource
    def get_vector_store_cached():
        return _get_vector_store()


    vector_store = get_vector_store_cached()
except Exception:
    vector_store = _get_vector_store()


@tool
def search_policy_docs(query: str) -> str:
    """Пошук у внутрішніх документах лікарні через векторну базу даних Pinecone."""
    try:
        q = (query or "").strip()
        if not q:
            return "Порожній запит."

        docs = vector_store.similarity_search(q, k=3)

        if not docs:
            return "У документах не знайдено релевантної інформації."

        # Збираємо унікальні джерела
        sources = set()
        results = []

        for doc in docs:
            filename = doc.metadata.get("filename", "N/A")
            sources.add(filename)
            results.append((doc.page_content or "").strip())

        content = "\n\n".join(results)
        sources_text = ", ".join(sorted(sources))

        # Додаємо джерела в кінці
        return f"{content}\n\n📄 Джерела: {sources_text}"

    except Exception as e:
        return f"Помилка пошуку: {str(e)}"