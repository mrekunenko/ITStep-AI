# delete_namespace.py
import os
import dotenv
from pinecone import Pinecone

dotenv.load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "omegamed-v3"
NAMESPACE = "default"

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

print(f"Видаляю всі дані з namespace '{NAMESPACE}'...")
index.delete(delete_all=True, namespace=NAMESPACE)
print("✅ Namespace очищено")
