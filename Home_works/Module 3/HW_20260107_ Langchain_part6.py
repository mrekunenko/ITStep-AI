# Курс: AI+Python
# Модуль 3. Generative AI, LLM
# Тема: Langchain. Частина 6
# Завдання 1
# Добавте в створену базу даних файл
# data/lesson_rag/huge_file.txt про умови користування гуглом
# Оскільки файл надто великий, то його треба добавляти
# частинами. Для цього:
#  прочитайте вміст файлу
#  розділіть його на окремі блоки(між блоками два
# порожніх рядка, дивись файл)
#  отримайте перший рядок кожного блоку – це його
# назва
#  створіть документи для кожного блоку. В метаданих:
# o назва файлу
# o назва блоку
#  створіть ID та добавте все в існуючу базу даних
#  добавте ID у json файл
#  перевірте агента

import os
import json
import re
from pathlib import Path
from uuid import uuid5, NAMESPACE_DNS
import dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from pinecone import Pinecone
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage

dotenv.load_dotenv()

llm = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',
    api_key=os.getenv("GEMINI_API_KEY")
)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
vector_store = PineconeVectorStore(
    index=pc.Index("soup"),
    embedding=embeddings
)

# Читання файлу
file_path = Path("data/lesson_rag/huge_file.txt")
content = file_path.read_text(encoding='utf-8')

# Розділення через regex (уникає проблем з пробілами)
blocks = re.split(r'\n\s*\n\s*\n', content)

documents = []
doc_ids = []
batch_size = 75

for block in blocks:
    if not block.strip():
        continue

    lines = block.strip().split('\n', 1)
    block_title = lines[0].strip()
    block_text = lines[1].strip() if len(lines) > 1 else ""

    # Детермінований UUID на основі назви блоку
    doc_id = str(uuid5(NAMESPACE_DNS, f"huge_file.txt:{block_title}"))

    doc = Document(
        page_content=f"{block_title}\n{block_text}",
        metadata={
            "file_name": "huge_file.txt",
            "block_title": block_title
        }
    )

    documents.append(doc)
    doc_ids.append(doc_id)

# Додавання батчами
for i in range(0, len(documents), batch_size):
    batch_docs = documents[i:i + batch_size]
    batch_ids = doc_ids[i:i + batch_size]
    vector_store.add_documents(documents=batch_docs, ids=batch_ids)
    print(f"Додано батч {i // batch_size + 1}: {len(batch_docs)} блоків")

# Збереження ID без дублікатів
json_path = Path("document_ids.json")
if json_path.exists():
    existing = set(json.loads(json_path.read_text()))
else:
    existing = set()

existing.update(doc_ids)
json_path.write_text(json.dumps(list(existing), indent=2, ensure_ascii=False))

print(f"\nВсього додано {len(doc_ids)} блоків")


# Пошуковий інструмент з фільтром
def find_google_conditions(query: str) -> list:
    """Пошук умов використання Google у базі знань"""
    results = vector_store.similarity_search(
        query,
        k=5,
        filter={"file_name": "huge_file.txt"}
    )
    return results


# Агент
agent = create_react_agent(
    model=llm,
    tools=[find_google_conditions]
)

dialog = [
    SystemMessage(
        "Ти консультуєш з умов використання Google. "
        "Використовуй find_google_conditions для пошуку точної інформації. "
        "Відповідай мовою запиту. Якщо даних немає — скажи чесно."
    )
]

print("\n=== Агент запущено ===\n")

while True:
    question = input("Ви: ")
    if not question.strip():
        break

    dialog.append(HumanMessage(question))
    response = agent.invoke({"messages": dialog})
    dialog = response['messages']

    print(f"Бот: {dialog[-1].content}\n")