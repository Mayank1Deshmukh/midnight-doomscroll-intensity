# setup_db.ps1 - Start PostgreSQL in Docker and initialize schema

Write-Host "🐳 Starting PostgreSQL container..." -ForegroundColor Cyan

docker run `
  --name doomscroll-postgres `
  --env POSTGRES_USER=doomscroll_user `
  --env POSTGRES_PASSWORD=secure_password_123 `
  --env POSTGRES_DB=doomscroll_db `
  --port 5432:5432 `
  -d `
  postgres:15-alpine

Write-Host "✅ PostgreSQL container started (doomscroll-postgres)" -ForegroundColor Green
Write-Host "   Waiting 5 seconds for PostgreSQL to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "🗄️  Initializing schema..." -ForegroundColor Cyan

$schema = Get-Content -Path "sql/01_schema.sql" -Raw
$schema | docker exec -i doomscroll-postgres psql -U doomscroll_user -d doomscroll_db

Write-Host "✅ Schema initialized" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Database ready!" -ForegroundColor Green
Write-Host "   Host: localhost" -ForegroundColor White
Write-Host "   Port: 5432" -ForegroundColor White
Write-Host "   User: doomscroll_user" -ForegroundColor White
Write-Host "   Password: secure_password_123" -ForegroundColor White
Write-Host "   Database: doomscroll_db" -ForegroundColor White
