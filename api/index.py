import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

app = FastAPI()

# --- 1. Path Setup (CRITICAL FIX) ---
# This locates the folder where index.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# This looks one level up for the JSON file
json_path = os.path.join(BASE_DIR, "..", "cyber_security.json")

# --- 2. AI Setup (Environment Variables) ---
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.5)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# --- 3. Load Knowledge Base ---
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
documents = [Document(page_content=entry["text"]) for entry in data]
vectorstore = DocArrayInMemorySearch.from_documents(documents, embeddings)

# --- 4. Translation-Focused Prompt ---
system_prompt = (
    "You are an expert Cyber Security Educator.\n"
    "Rule: If the user asks for Hindi, Kannada, or Tulu, provide a "
    "meaningful and proper translation using natural, local phrasing. "
    "Do not use robot-like or broken grammar.\n\n"
    "Context:\n{context}"
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt), 
    ("human", "{input}")
])

# Create the RAG chain
combine_docs_chain = create_stuff_documents_chain(llm, prompt_template)
chain = create_retrieval_chain(vectorstore.as_retriever(), combine_docs_chain)

class ChatInput(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(input_data: ChatInput):
    response = chain.invoke({"input": input_data.message})
    return {"reply": response["answer"]}