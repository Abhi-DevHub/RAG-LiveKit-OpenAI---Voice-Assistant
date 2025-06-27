import os
import time
from dotenv import load_dotenv
from pathlib import Path
from pinecone import Pinecone, ServerlessSpec

from langchain_community.document_loaders import PyMuPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

# --- Load environment variables ---
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("Missing Pinecone API key")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key")

# --- Configurations ---
# Pinecone
PINECONE_INDEX_NAME = "your-index-name"  # Replace with your actual index name
PINECONE_NAMESPACE = "your-namespace"  # Replace with your actual namespace
PINECONE_DIMENSION = 1536  # Dimension for OpenAI text-embedding-3-small
PINECONE_METRIC = "cosine"  # Metric for similarity search
PINECONE_CLOUD = "aws"  # Cloud provider for Pinecone
PINECONE_REGION = "us-east-1"  # Region for Pinecone        

#--- OpenAI --- Embedding model
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"

#--- Data --- Directory for PDF files
PDF_DIRECTORY = Path.cwd() / "pdfs"

#--- LangChain ---
CHUNK_SIZE = 200  # Size of each text chunk
CHUNK_OVERLAP = 50  # Overlap between text chunks
TOP_K_RESULTS = 3  # Number of top results to retrieve

# --- Initialization ---
print("Initializing services ...")

# Pinecone client
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    print("Pinecone client initialized.")
except Exception as e:
    print(f"X Failed to initialize Pinecone client: {e}")
    exit()

#--- OpenAI Embeddings ---
try:
    embeddings = OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY
    )
    print(f"OpenAI Embeddings model ({OPENAI_EMBEDDING_MODEL}) initialized.")
except Exception as e:
    print(f"X Failed to initialize OpenAI models: {e}")
    exit()

print("Initialization complete.")

# --- Pinecone Index Setup ---
print(f"\nChecking Pinecone index '{PINECONE_INDEX_NAME}' ...")
existing_indexes = pc.list_indexes()

#--- Create index if it doesn't exist ---
if PINECONE_INDEX_NAME not in [idx.name for idx in existing_indexes]:
    print(f"Index '{PINECONE_INDEX_NAME}' not found. Creating ...")
    try:
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=PINECONE_DIMENSION,
            metric=PINECONE_METRIC,
            spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION)
        )

        # Wait for the index to be ready
        while not pc.describe_index(PINECONE_INDEX_NAME).status['ready']:
            print("Waiting for index to be ready ...")
            time.sleep(5)

        print(f"Index '{PINECONE_INDEX_NAME}' created successfully.")
    except Exception as e:
        print(f"X Failed to create index '{PINECONE_INDEX_NAME}': {e}")
        exit()
else:
    print(f"Index '{PINECONE_INDEX_NAME}' already exists.")

#--- Validate index dimension ---
index_description = pc.describe_index(PINECONE_INDEX_NAME)
if index_description.dimension != PINECONE_DIMENSION:
    print(f"X ERROR: Index '{PINECONE_INDEX_NAME}' exists but has dimension {index_description.dimension}, "
          f"which does not match the required dimension {PINECONE_DIMENSION} for model '{OPENAI_EMBEDDING_MODEL}'.")
    print("Please delete the index or use an embedding model with matching dimensions.")
    exit()
else:
    print(f"Index '{PINECONE_INDEX_NAME}' has correct dimension ({PINECONE_DIMENSION}).")

#--- Connect to the index ---
try:
    index = pc.Index(PINECONE_INDEX_NAME)
    print(f"Connected to Pinecone index '{PINECONE_INDEX_NAME}'.")
except Exception as e:
    print(f"X Failed to connect to Pinecone index: {e}")
    exit()

# Show index stats before loading
print("Index stats before loading:", index.describe_index_stats())

# --- Data Loading and Processing ---
print(f"\nLoading documents from '{PDF_DIRECTORY}' ...")
if not PDF_DIRECTORY.exists() or not PDF_DIRECTORY.is_dir():
    print(f"X Error: PDF directory not found at '{PDF_DIRECTORY}'. Please create it and add your PDF files.")
    exit()

try:
    # --- Using DirectoryLoader with PyMuPDFLoader to load all PDFs ---
    loader = DirectoryLoader(
        str(PDF_DIRECTORY),
        glob="*.pdf",
        loader_cls=PyMuPDFLoader,
        show_progress=True,
        use_multithreading=True
    )

    documents = loader.load()
    print(f"Loaded {len(documents)} pages from PDF files.")

    if not documents:
        print(f"X No PDF documents found in '{PDF_DIRECTORY}'.")
        exit()

    # Split documents into chunks
    print("Splitting documents into chunks ...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    docs_chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} pages into {len(docs_chunks)} chunks.")

except Exception as e:
    print(f"Failed during document loading or splitting: {e}")
    exit()

# --- Vector Store Setup ---
print("\nSetting up Pinecone vector store ...")
try:
    # Manual batching to avoid Pinecone's 4MB per upsert limit
    batch_size = 100 
    for i in range(0, len(docs_chunks), batch_size):
        batch = docs_chunks[i:i+batch_size]
        PineconeVectorStore.from_documents(
            batch,
            index_name=PINECONE_INDEX_NAME,
            embedding=embeddings,
            namespace=PINECONE_NAMESPACE,
            text_key="text"
        )

    print(f"Data loaded and processed successfully. Indexed {len(docs_chunks)} chunks.")

    print("Waiting few seconds for Pinecone to index the data ...")
    time.sleep(5)  # Wait for Pinecone to index the data

    # Show index stats after loading
    print("Index stats after loading:", index.describe_index_stats())

except Exception as e:
    print(f"X Failed to set up Pinecone vector store: {e}")
    exit()

print("Waiting for Pinecone to index the data ...")
time.sleep(5)  # Wait for Pinecone to index the data