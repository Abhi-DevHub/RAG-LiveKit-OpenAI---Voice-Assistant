from __future__ import annotations
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    function_tool,
    RoomInputOptions, 
)
from livekit.plugins import openai, silero, noise_cancellation
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
import os

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_INDEX_NAME = "rag-agent-ai-qa"
PINECONE_NAMESPACE = "ns3-rag-agent-ai-qa"

# Setup Pinecone and OpenAI
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY) # type: ignore
vectorstore = PineconeVectorStore(
    index=index,
    embedding=embeddings,
    namespace=PINECONE_NAMESPACE,
    text_key="text"
)
llm_model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4o") # type: ignore

# Define the RAG tool for the agent
# This tool retrieves relevant documents from Pinecone and uses the LLM to answer questions based on those documents.
@function_tool
async def rag_tool(query: str):
    """Answer questions using RAG over your Pinecone vector DB."""
    try:
        docs = vectorstore.similarity_search(query, k=20)
        print(f"DEBUG: Pinecone returned {len(docs)} docs for query: {query}")
        if not docs:
            return "No relevant documents found in Pinecone."
        context_str = "\n\n".join([
            f"Source: {doc.metadata.get('source', 'unknown')}, Page: {doc.metadata.get('page', 'unknown')}\n{doc.page_content}"
            for doc in docs
        ])
    except Exception as e:
        return f"Error retrieving documents from Pinecone: {e}"
    #tell that the context is not available in the submitted documents (add this if you only want the answer or content of the documents)
    prompt = f"""
You are an expert assistant. Use the following context to answer the question. Always respond in plain text only, without any Markdown formatting, asterisks, or special characters for bold/italic. If you can't find the answer, do your best to help. -- important

Context:
{context_str}

Question: {query}
"""
    response = llm_model.invoke(prompt)
    return response.content

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(
        instructions="""
            You are a helpful voice assistant with access to a document knowledge base.
            - Greet the user at the start.
            - If the user asks a question about the documents, use the `rag_tool`.
            - If unsure, ask clarifying questions.
            """,
        tools=[rag_tool],
    )
    session = AgentSession(
        vad=silero.VAD.load(),  # Use Silero VAD for voice activity detection
        stt=openai.STT(),
        llm=openai.LLM(model="gpt-4o"),
        tts=openai.TTS(),
    )

    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        )
    )
    await session.generate_reply(
        instructions="Say hello! You can ask me anything about your documents."
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))