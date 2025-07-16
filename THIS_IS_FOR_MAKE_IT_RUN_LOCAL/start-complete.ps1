# Complete startup script for LiveKit RAG Application
Write-Host "🚀 Starting Complete LiveKit RAG Application" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please create a .env file with your LiveKit and OpenAI credentials" -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 Starting all components..." -ForegroundColor Yellow
Write-Host ""

# Start backend in background
Write-Host "1️⃣ Starting Backend Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python main.py; Write-Host 'Backend stopped' -ForegroundColor Red"

# Wait for backend to start
Start-Sleep -Seconds 3

# Start LiveKit agent in background
Write-Host "2️⃣ Starting LiveKit Agent..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python livekit_agent.py dev; Write-Host 'Agent stopped' -ForegroundColor Red"

# Wait for agent to start
Start-Sleep -Seconds 2

# Start frontend
Write-Host "3️⃣ Starting Frontend..." -ForegroundColor Green
Set-Location frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev; Write-Host 'Frontend stopped' -ForegroundColor Red"

Write-Host ""
Write-Host "✅ All components starting!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Application URLs:" -ForegroundColor Cyan
Write-Host "• Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "• Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "• API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🤖 Components Running:" -ForegroundColor Cyan
Write-Host "• FastAPI Backend - Token generation and room management" -ForegroundColor White
Write-Host "• LiveKit Agent   - AI assistant with RAG capabilities" -ForegroundColor White
Write-Host "• React Frontend  - User interface for video calls" -ForegroundColor White
Write-Host ""
Write-Host "📱 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:5173 in your browser" -ForegroundColor White
Write-Host "2. Enter your name and join a room" -ForegroundColor White
Write-Host "3. Ask the AI assistant questions about the documents!" -ForegroundColor White
Write-Host ""
Write-Host "💡 Example questions to ask the AI:" -ForegroundColor Yellow
Write-Host "• 'What is machine learning?'" -ForegroundColor White
Write-Host "• 'Explain neural networks'" -ForegroundColor White
Write-Host "• 'How does deep learning work?'" -ForegroundColor White
