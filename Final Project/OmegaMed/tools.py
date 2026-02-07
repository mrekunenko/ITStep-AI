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
        google_api_key=GEMINI_API_KEY
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


# ✅ Debug функція ПІСЛЯ ініціалізації vector_store
def debug_search(query: str):
    """Перевірка scores для налаштування threshold"""
    results = vector_store.similarity_search_with_score(query, k=10)
    print(f"\n🔍 Debug для запиту: '{query}'")
    for i, (doc, score) in enumerate(results, 1):
        filename = doc.metadata.get("filename", "N/A")
        preview = doc.page_content[:100].replace("\n", " ")
        print(f"{i}. Score: {score:.3f} | {filename} | {preview}...")
    print("\n")


@tool
def search_policy_docs(query: str) -> str:
    """Search in hospital policy documents via Pinecone vector database."""
    try:
        q = (query or "").strip()
        if not q:
            return "Порожній запит."

        # Отримуємо результати зі score
        results_with_scores = vector_store.similarity_search_with_score(q, k=8)

        if not results_with_scores:
            return "У документах не знайдено релевантної інформації."

        # ✅ ПРАВИЛЬНА ФІЛЬТРАЦІЯ: score > 0.7 = релевантні
        filtered_docs = [
            (doc, score)
            for doc, score in results_with_scores
            if score > 0.70
        ]

        # Fallback: якщо нічого не знайшли, беремо 2 найкращі
        if not filtered_docs:
            filtered_docs = results_with_scores[:2]

        # Обмежуємо до топ-3
        filtered_docs = filtered_docs[:3]

        sources = set()
        results = []

        for doc, score in filtered_docs:
            filename = doc.metadata.get("filename", "N/A")
            sources.add(filename)
            results.append((doc.page_content or "").strip())

        content = "\n\n".join(results)
        sources_text = ", ".join(sorted(sources))

        return f"{content}\n\n📄 Джерела: {sources_text}"

    except Exception as e:
        return f"Помилка пошуку: {str(e)}"

        for doc, score in filtered_docs:
            filename = doc.metadata.get("filename", "N/A")
            sources.add(filename)
            content = (doc.page_content or "").strip()
            results.append(content)

        content = "\n\n".join(results)
        sources_text = ", ".join(sorted(sources))

        return f"{content}\n\n📄 Джерела: {sources_text}"

    except Exception as e:
        return f"Помилка пошуку: {str(e)}"
