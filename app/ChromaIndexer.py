import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# Hardcoded absolute path directly relative to this script file to prevent Windows path bugs
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(CURRENT_DIR, "knowledge")
DB_DIR = os.path.join(CURRENT_DIR, "chroma_db")


def build_vector_store():
    print(f"Checking for documents in: {KNOWLEDGE_DIR}")

    if not os.path.exists(KNOWLEDGE_DIR):
        print(f"❌ Error: The directory {KNOWLEDGE_DIR} does not exist!")
        return

    # 1. Manually find and read markdown/text files in the folder
    all_documents = []
    files_in_dir = os.listdir(KNOWLEDGE_DIR)
    print(f"Found files in knowledge directory: {files_in_dir}")

    for file_name in files_in_dir:
        if file_name.endswith(('.md', '.txt')):
            file_path = os.path.join(KNOWLEDGE_DIR, file_name)
            print(f"Loading document: {file_name}...")
            loader = TextLoader(file_path, encoding='utf-8')
            all_documents.extend(loader.load())

    if not all_documents:
        print("❌ Error: No text could be loaded. Ensure your markdown file has actual text content.")
        return

    # 2. Split text into chunks
    print(f"Successfully loaded {len(all_documents)} file(s). Splitting into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(all_documents)
    print(f"Created {len(chunks)} chunks.")

    # 3. Embed chunks using Gemini's stable active model
    print("Creating vector store...")
    print("Loading Google Generative AI Embeddings...")
    # 3. Initialize Gemini Embeddings (MUST match your ChromaIndexer.py exactly!)
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
    print("✓ Embeddings configured with model: gemini-embedding-2-preview")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )

    print(f"✓ Vector store successfully built at {DB_DIR}!")
    return vector_store


if __name__ == "__main__":
    build_vector_store()