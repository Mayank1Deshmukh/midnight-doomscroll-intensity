# reset_db.ps1 - Delete all data and restart (development only)

Write-Host "⚠️  WARNING: This will delete all data in the database!" -ForegroundColor Red
$confirm = Read-Host "Are you sure? (yes/no)"

if ($confirm -ne "yes") {
  Write-Host "Cancelled." -ForegroundColor Yellow
  exit 0
}

Write-Host ""
Write-Host "🛑 Stopping and removing container..." -ForegroundColor Yellow
docker stop doomscroll-postgres 2>$null
docker rm doomscroll-postgres 2>$null

Write-Host "✅ Container removed" -ForegroundColor Green
Write-Host ""
Write-Host "🔄 Reinitializing database..." -ForegroundColor Cyan

& .\scripts\setup_db.ps1

Write-Host ""
Write-Host "✨ Database reset complete" -ForegroundColor Green
