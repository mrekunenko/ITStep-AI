# delete_index.py
import os
import dotenv
from pinecone import Pinecone

dotenv.load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME = "omegamed-v3"

print(f"Видаляю індекс {INDEX_NAME}...")
pc.delete_index(INDEX_NAME)
print("✅ Індекс видалено")
