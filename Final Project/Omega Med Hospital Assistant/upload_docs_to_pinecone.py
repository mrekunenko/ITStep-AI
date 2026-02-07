# upload_docs_to_pinecone.py
import os
import json
import dotenv
from uuid import uuid4
from datetime import datetime, timezone
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

dotenv.load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "omegamed-v3")
NAMESPACE = os.getenv("PINECONE_NAMESPACE", "default")
DOCS_FOLDER = os.getenv("DOCS_FOLDER", "docs")

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY не знайдено у .env")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY не знайдено у .env")
if not os.path.exists(DOCS_FOLDER):
    raise ValueError(f"Папка {DOCS_FOLDER} не існує")

files = [f for f in os.listdir(DOCS_FOLDER) if f.lower().endswith((".pdf", ".docx"))]
if not files:
    raise ValueError(f"Папка {DOCS_FOLDER} порожня")

print(f"Папка: {DOCS_FOLDER}")
print(f"Файлів: {len(files)}\n")

EMBEDDING_DIMENSION = 3072

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GEMINI_API_KEY,
    task_type="retrieval_document"
)

pc = Pinecone(api_key=PINECONE_API_KEY)

if not pc.has_index(INDEX_NAME):
    print(f"Створюю індекс: {INDEX_NAME}")
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
else:
    print(f"Індекс {INDEX_NAME} вже існує")

index = pc.Index(INDEX_NAME)

vector_store = PineconeVectorStore(
    index=index,
    embedding=embeddings,
    namespace=NAMESPACE
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def load_file(path: str) -> List[Document]:
    """Завантаження документа з файлу"""
    if path.lower().endswith(".pdf"):
        loader = PyPDFLoader(path)
    else:
        loader = Docx2txtLoader(path)

    return loader.load()


def get_section_title(text: str) -> str:
    """Отримання заголовка розділу з першого рядка"""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return "Без розділу"
    return lines[0][:100]


docs: List[Document] = []
ids: List[str] = []

upload_time = datetime.now(timezone.utc).isoformat()

print("Обробка документів:\n")

for filename in files:
    file_path = os.path.join(DOCS_FOLDER, filename)

    try:
        base_docs = load_file(file_path)
        text_all = "\n".join([d.page_content for d in base_docs if d.page_content])

        if not text_all.strip():
            print(f"{filename}: порожній файл\n")
            continue

        chunks = splitter.split_text(text_all)
        print(f"{filename}: {len(chunks)} частин")

        for i, chunk in enumerate(chunks):
            metadata = {
                "filename": filename,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "upload_time": upload_time,
                "section_title": get_section_title(chunk),
            }

            doc = Document(page_content=chunk, metadata=metadata)
            docs.append(doc)
            ids.append(str(uuid4()))

    except Exception as e:
        print(f"Помилка {filename}: {e}\n")
        continue

if not docs:
    raise ValueError("Жодного документа не оброблено")

print(f"\nВсього частин: {len(docs)}")
print("Завантаження у Pinecone...")

try:
    vector_store.add_documents(documents=docs, ids=ids)
    print(f"✅ Успішно завантажено {len(docs)} частин\n")
except Exception as e:
    print(f"❌ Помилка: {e}")
    raise

# Збереження ID у JSON файл
id_map = {}
for doc, doc_id in zip(docs, ids):
    filename = doc.metadata.get("filename")
    chunk_idx = doc.metadata.get("chunk_index")
    section = doc.metadata.get("section_title", "")

    key = f"{filename}_chunk_{chunk_idx}"
    id_map[key] = {
        "id": doc_id,
        "filename": filename,
        "chunk_index": chunk_idx,
        "section_title": section
    }

with open("document_ids.json", "w", encoding="utf-8") as f:
    json.dump(id_map, f, ensure_ascii=False, indent=2)

print("✅ Завершено")
print(f"Індекс: {INDEX_NAME}")
print(f"Документів: {len(files)}")
print(f"Частин: {len(docs)}")
print(f"ID збережено у document_ids.json")
