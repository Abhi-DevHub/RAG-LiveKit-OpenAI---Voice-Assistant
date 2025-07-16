# PowerShell script to setup the frontend
Write-Host "Setting up LiveKit RAG Frontend..." -ForegroundColor Green

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Found Node.js: $nodeVersion" -ForegroundColor Yellow
} catch {
    Write-Host "Error: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Check if npm is installed
try {
    $npmVersion = npm --version 2>&1
    Write-Host "Found npm: $npmVersion" -ForegroundColor Yellow
} catch {
    Write-Host "Error: npm is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend dependencies installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Setup complete! 🎉" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To start the application:" -ForegroundColor Cyan
    Write-Host "1. Start backend: cd .. && python main.py" -ForegroundColor White
    Write-Host "2. Start frontend: npm run dev" -ForegroundColor White
    Write-Host ""
    Write-Host "Frontend will be available at: http://localhost:5173" -ForegroundColor Green
    Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
