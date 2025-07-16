# PowerShell script to start the frontend development server
Write-Host "Starting LiveKit RAG Frontend..." -ForegroundColor Green

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "❌ Error: Dependencies not installed!" -ForegroundColor Red
    Write-Host "Please run: npm install" -ForegroundColor Yellow
    exit 1
}

# Start the Vite development server
Write-Host "🚀 Starting Vite development server on http://localhost:5173" -ForegroundColor Yellow
npm run dev
