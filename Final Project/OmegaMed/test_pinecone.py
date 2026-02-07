# test_pinecone.py
import os
import dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore

dotenv.load_dotenv()

PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "omegamed-v3")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GEMINI_API_KEY
)

vector_store = PineconeVectorStore.from_existing_index(
    index_name=PINECONE_INDEX_NAME,
    embedding=embeddings,
    namespace=PINECONE_NAMESPACE,
)

# Тестові запити
test_queries = [
    "тривалість відпустки",
    "місія та візія Омега-Мед",
    "випробувальний термін",
    "медичне обладнання МРТ",
]

print("=" * 70)
print("🔍 ТЕСТУВАННЯ PINECONE SCORES")
print("=" * 70)

for query in test_queries:
    print(f"\n📝 Запит: '{query}'")
    print("-" * 70)

    results = vector_store.similarity_search_with_score(query, k=5)

    # Рядки 30-37
    for i, (doc, score) in enumerate(results, 1):
        filename = doc.metadata.get("filename", "N/A")
        preview = doc.page_content[:80].replace("\n", " ")

        # ✅ ПРАВИЛЬНА ШКАЛА для cosine similarity
        if score > 0.75:
            status = "🟢 ВІДМІННО"
        elif score > 0.65:
            status = "🟡 ДОБРЕ"
        elif score > 0.50:
            status = "🟠 СЕРЕДНЄ"
        else:
            status = "🔴 ПОГАНО"

        print(f"{i}. {status} | Score: {score:.3f} | {filename}")
        print(f"   {preview}...")

    print()

print("=" * 70)
print("💡 РЕКОМЕНДАЦІЇ:")
print("   • Якщо хороші результати мають score < 0.4 → встанови threshold < 0.45")
print("   • Якщо хороші результати мають score < 0.3 → встанови threshold < 0.35")
print("   • Якщо погані результати мають score > 0.6 → все ОК, залиш < 0.5")
print("=" * 70)
