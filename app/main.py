import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 1. Import LangChain / Gemini components
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

app = FastAPI(
    title="CV Agent API",
    description="Backend API for the AI agent",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Path to the folder where ChromaIndexer.py saved your database
CHROMA_PATH = "./chroma_db"

# 3. Initialize Gemini Embeddings (Must match what you used in ChromaIndexer.py)
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

# 4. Load the existing vector store from your local folder
# 4. Load the existing vector store from your local folder
if not os.path.exists(CHROMA_PATH):
    print(f"⚠️ Warning: Chroma directory not found at {CHROMA_PATH}. Run ChromaIndexer.py first!")
    db = None
    retrieval_chain = None
else:
    print("Connecting to local ChromaDB database...")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 3})
    print("✓ ChromaDB connected successfully.")

    print("Initializing Gemini-2.5-flash LLM model...")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
    print("✓ LLM configuration created.")

    system_prompt = (
        "You are an expert AI representative answering questions about Ishay's CV, projects, and experience.\n"
        "Use the following pieces of retrieved context to answer the question. If you don't know the answer, "
        "say that you don't know.\n\n"
        "{context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    print("Assembling the RAG retrieval chain...")
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, question_answer_chain)
    print("✓ RAG chain completely ready to handle requests!")

# Define the request body schema for the API
class QueryRequest(BaseModel):
    question: str


# 7. Create the POST endpoint for asking questions
@app.post("/ask")
async def ask_agent(request: QueryRequest):
    if not retrieval_chain:
        raise HTTPException(status_code=500, detail="Vector database not initialized. Run the indexer.")

    try:
        # Run the query through the RAG pipeline
        response = retrieval_chain.invoke({"input": request.question})
        return {
            "question": request.question,
            "answer": response["answer"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "CV Agent API is running"}