import os
import streamlit as st
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_INDEX_NAME = "your-index-name"  # Replace with your actual index name
PINECONE_NAMESPACE = "your-namespace"  # Replace with your actual namespace

# Initialize Pinecone and OpenAI
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY) # type: ignore
vectorstore = PineconeVectorStore(
    index=index,
    embedding=embeddings,
    namespace=PINECONE_NAMESPACE,
    text_key="text"
)
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, # type: ignore
                    model="gpt-4o",
                )

# Streamlit UI
st.title("Chat with your Pinecone Data (OpenAI Agent)")
query = st.text_input("Ask a question about your documents:")

if query:
    # Retrieve relevant docs from Pinecone
    docs = vectorstore.similarity_search(query, k=700)
    context = "\n\n".join([doc.page_content for doc in docs])

    # Compose prompt for OpenAI
    prompt = f"Answer the question based on the following context:\n{context}\n\nQuestion: {query}"

    # Get answer from OpenAI
    response = llm.invoke(prompt)
    st.write("**Answer:**", response.content)