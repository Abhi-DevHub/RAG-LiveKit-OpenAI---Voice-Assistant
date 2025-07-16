from __future__ import annotations
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    function_tool,
)
from livekit.plugins import openai, silero
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

# Validate environment variables
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY environment variable is required")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Setup Pinecone and OpenAI
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY) # type: ignore
    vectorstore = PineconeVectorStore(
        index=index,
        embedding=embeddings,
        namespace=PINECONE_NAMESPACE,
        text_key="text"
    )
    llm_model = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o") # type: ignore
    print("✅ Successfully connected to Pinecone and OpenAI")
except Exception as e:
    print(f"❌ Failed to initialize services: {e}")
    raise

@function_tool
async def rag_tool(query: str):
    """Answer questions using RAG over your Pinecone vector DB."""
    try:
        print(f"🔍 RAG Query: {query}")
        
        # Search with multiple strategies for better retrieval
        docs = vectorstore.similarity_search(query, k=20)
        print(f"📚 Found {len(docs)} documents from Pinecone")
        
        if not docs:
            # Try a broader search if no docs found
            broader_query = " ".join(query.split()[:3])  # Use first 3 words
            docs = vectorstore.similarity_search(broader_query, k=7)
            print(f"📚 Broader search found {len(docs)} documents")
        
        if not docs:
            return "I couldn't find relevant information in the knowledge base. Could you try rephrasing your question or asking about a different topic?"
        
        # Build context with better formatting
        context_parts = []
        for i, doc in enumerate(docs[:5], 1):  # Limit to top 5 for better quality
            source = doc.metadata.get('source', 'Document')
            page = doc.metadata.get('page', 'N/A')
            content = doc.page_content.strip()
            context_parts.append(f"[Source {i}: {source}, Page {page}]\n{content}")
        
        context_str = "\n\n".join(context_parts)
        
        prompt = f"""You are an expert assistant with access to educational documents. Answer the question using ONLY the provided context. Be specific, accurate, and helpful.

IMPORTANT: Respond in plain text only - no markdown, asterisks, or special formatting.

Context from documents:
{context_str}

Question: {query}

Answer based on the context above:"""

        print(f"💭 Sending query to LLM......")
        response = llm_model.invoke(prompt)
        answer = str(response.content).strip() if hasattr(response, 'content') else str(response).strip()
        
        print(f"✅ RAG Response generated: {len(answer)} characters")
        return answer
        
    except Exception as e:
        print(f"❌ ERROR in rag_tool: {e}")
        import traceback
        traceback.print_exc()
        return f"I encountered an error while searching the knowledge base: {str(e)}"

async def entrypoint(ctx: JobContext):
    try:
        await ctx.connect()
        print("✅ Connected to LiveKit room")
        print(f"🏠 Room name: {ctx.room.name}")
        print(f"👥 Participants: {len(ctx.room.remote_participants)}")

        agent = Agent(
            instructions="""
You are an intelligent AI assistant with access to documents and research papers.

Your capabilities:
- Answer questions about machine learning, deep learning, and AI concepts
- Provide detailed explanations from the knowledge base
- Help with academic and technical queries

When a user asks a question:
1. Always try to use the rag_tool to search the knowledge base first
2. Provide detailed, accurate answers based on the documents
3. If no relevant information is found, let the user know and suggest they try a different question
4. Be conversational but informative
5. Cite sources when possible

Start by greeting the user and explaining your capabilities.
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
            room=ctx.room
        )
        
        # Generate initial greeting
        await session.generate_reply(
            instructions="Greet the user warmly and explain that you can answer questions about the documents in your knowledge base. Mention topics like machine learning, deep learning, and AI concepts."
        )
        
        print("✅ Agent session started successfully")
        print("🤖 AI Assistant is ready to answer questions!")
        
    except Exception as e:
        print(f"❌ Error in entrypoint: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))