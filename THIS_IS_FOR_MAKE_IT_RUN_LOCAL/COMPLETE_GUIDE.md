# 🤖 LiveKit RAG Application - COMPLETE SETUP GUIDE

## 🎯 What This Application Does

This is a **complete video conferencing application** with an **AI-powered RAG (Retrieval-Augmented Generation) assistant** that can answer questions about your documents in real-time during video calls.

### 🔧 Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│◄──►│  FastAPI Backend│◄──►│ LiveKit Agent   │
│   (Port 5173)   │    │   (Port 8000)   │    │ (AI Assistant)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ LiveKit Cloud   │    │ Pinecone DB +   │
                       │ (Video/Audio)   │    │ OpenAI LLM      │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Complete Setup Instructions

### 1. Backend Setup ✅ (DONE)
- FastAPI server for token generation and room management
- Running on: http://localhost:8000

### 2. Frontend Setup ✅ (DONE)  
- React application with LiveKit components
- Running on: http://localhost:5173

### 3. **NEW: LiveKit Agent Setup** (REQUIRED FOR AI)

The LiveKit Agent is what provides the AI capabilities. **You MUST start this for RAG to work!**

## 📋 Step-by-Step Usage

### Step 1: Start All Components

**Option A: Start Everything at Once**
```powershell
.\start-complete.ps1
```

**Option B: Start Individually**
```powershell
# Terminal 1: Backend
python main.py

# Terminal 2: LiveKit Agent (AI Assistant)
python livekit_agent.py dev

# Terminal 3: Frontend
cd frontend
npm run dev
```

### Step 2: Use the Application

1. **Open Browser**: Go to http://localhost:5173
2. **Enter Your Name**: Required for room identification
3. **Join Room**: Click "Join Room" button
4. **Grant Permissions**: Allow camera and microphone access
5. **Wait for AI Greeting**: The AI assistant will introduce itself
6. **Ask Questions**: Start asking about machine learning, AI, or deep learning!

## 🎙️ How to Interact with the AI Assistant

### Voice Interaction
- **Speak naturally** - The AI uses voice activity detection
- **Wait for responses** - The AI will speak back to you
- **Ask follow-up questions** - Have a conversation!

### Example Questions to Try
- "What is machine learning?"
- "Explain neural networks to me"
- "How does deep learning work?"
- "What are the different types of machine learning algorithms?"
- "Tell me about supervised learning"
- "What is the difference between AI and machine learning?"

## 🔧 Troubleshooting

### ❌ Problem: "AI not responding to questions"
**Solution**: Make sure the LiveKit Agent is running!
```powershell
python livekit_agent.py dev
```

### ❌ Problem: "No relevant documents found"
**Solutions**:
1. Try rephrasing your question
2. Ask about ML/AI/Deep Learning topics specifically
3. Use simpler, more direct questions
4. Check that Pinecone credentials are correct in .env

### ❌ Problem: "Can't join room"
**Solutions**:
1. Check that backend is running: http://localhost:8000/health
2. Verify LiveKit credentials in .env file
3. Ensure browser has camera/microphone permissions

## 📊 Current Status Check

Run this to verify everything is working:
```powershell
.\check-status.ps1
```

## 🎥 What You Should See

### When Everything is Working:
1. **Frontend**: Clean interface at http://localhost:5173
2. **Backend**: API responses at http://localhost:8000
3. **Agent**: Console shows "Agent session started successfully"
4. **In Room**: AI greets you and explains its capabilities
5. **AI Responses**: Detailed answers about ML/AI topics

### Components Running:
- ✅ **FastAPI Backend** - Handles authentication and room creation
- ✅ **React Frontend** - Provides the user interface
- ✅ **LiveKit Agent** - AI assistant with RAG capabilities
- ✅ **LiveKit Cloud** - Video/audio infrastructure
- ✅ **Pinecone + OpenAI** - Knowledge base and language model

## 🎯 Key Features Now Available

### 🎥 Video Conferencing
- HD video and audio calls
- Multiple participants support
- Real-time communication

### 🤖 AI Assistant Capabilities
- **Document Q&A**: Ask questions about ML/AI concepts
- **Voice Interaction**: Speak naturally with the AI
- **Contextual Responses**: Detailed answers from knowledge base
- **Real-time Processing**: Immediate responses during video calls

### 📚 Knowledge Base Topics
- Machine Learning fundamentals
- Deep Learning concepts
- Neural network architectures
- AI algorithms and methodologies
- Research papers and academic content

## 🔑 Important Notes

1. **All three components must be running** for full functionality
2. **The LiveKit Agent is crucial** for AI features - don't skip it!
3. **Browser permissions** are required for camera/microphone
4. **Voice interaction** works best in quiet environments
5. **Ask specific questions** about ML/AI topics for best results

Your LiveKit RAG application is now **fully functional** with AI-powered document assistance! 🎉
