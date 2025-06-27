from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import os

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("rag-agent-ai-qa")
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
vectorstore = PineconeVectorStore(
    index=index,
    embedding=embeddings,
    namespace="ns3-rag-agent-ai-qa",
    text_key="text"
)
docs = vectorstore.similarity_search("test", k=3)
print(docs)