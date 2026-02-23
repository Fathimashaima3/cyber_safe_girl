import os
import json
from fastapi import FastAPI
from pydantic import BaseModel

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

app = FastAPI()

# ---------- PATH SETUP ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

json_path = os.path.join(ROOT_DIR, "cyber_security.json")
faiss_path = os.path.join(ROOT_DIR, "faiss_index")

# ---------- AI SETUP ----------
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.4)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ---------- LOAD DATA ----------
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

documents = [Document(page_content=entry["text"]) for entry in data]

vectorstore = FAISS.load_local(
    faiss_path,
    embeddings,
    allow_dangerous_deserialization=True
)

# ---------- PROMPT ----------
system_prompt = (
    "You are an expert Cyber Security Educator.\n"
    "Use the given context first, otherwise answer normally.\n\n"
    "Context:\n{context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

combine_docs_chain = create_stuff_documents_chain(llm, prompt)
chain = create_retrieval_chain(vectorstore.as_retriever(), combine_docs_chain)

# ---------- API ----------
class ChatInput(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(input_data: ChatInput):
    response = chain.invoke({"input": input_data.message})
    return {"reply": response["answer"]}