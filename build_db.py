import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

with open("cyber_security.json", "r", encoding="utf-8") as f:
    data = json.load(f)

docs = [Document(page_content=x["text"]) for x in data if "text" in x]

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

db = FAISS.from_documents(docs, embeddings)

db.save_local("faiss_index")

print("FAISS DB created successfully")
