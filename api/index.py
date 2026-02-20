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

# 1. AI Setup (Keys are set in Vercel Dashboard)
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.5)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# 2. Load Knowledge Base
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
documents = [Document(page_content=entry["text"]) for entry in data]
vectorstore = DocArrayInMemorySearch.from_documents(documents, embeddings)

# 3. Translation-Focused Prompt
system_prompt = (
    "You are an expert Cyber Security Educator.\n"
    "Rule: If the user asks for Hindi, Kannada, or Tulu, provide a "
    "'Meaningful and Proper' translation using natural, local phrasing.\n\n"
    "Context:\n{context}"
)

prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{input}")])
chain = create_retrieval_chain(vectorstore.as_retriever(), create_stuff_documents_chain(llm, prompt))

class ChatInput(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(input: ChatInput):
    response = chain.invoke({"input": input.message})
    return {"reply": response["answer"]}