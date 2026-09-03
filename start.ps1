# Run this script to start the MerchantAI project
Write-Host "Starting MerchantAI Backend (FastAPI)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit -Command `"cd D:\merchantai\backend; pip install -r requirements.txt; uvicorn main:app --reload`"" -WindowStyle Normal

Write-Host "Starting MerchantAI Frontend (Vite)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit -Command `"cd D:\merchantai\frontend; npm run dev`"" -WindowStyle Normal

Write-Host "Both servers are starting in new windows." -ForegroundColor Green
Write-Host "Make sure you have added your API keys to D:\merchantai\.env" -ForegroundColor Yellow
