# run_pipeline.ps1 - Execute complete ETL pipeline

$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot

Write-Host "🚀 Starting Midnight Doomscroll Intensity ETL Pipeline..." -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Step 1: Extract & Transform
Write-Host "📥 Step 1/4: Extracting and transforming data..." -ForegroundColor Yellow
python -m etl.etl_pipeline
if ($LASTEXITCODE -eq 0) {
  Write-Host "✅ ETL transformation complete" -ForegroundColor Green
} else {
  Write-Host "❌ ETL transformation failed" -ForegroundColor Red
  exit 1
}

Write-Host ""

# Step 2: Load
Write-Host "📤 Step 2/4: Loading data into PostgreSQL..." -ForegroundColor Yellow
python -m etl.load_to_db
if ($LASTEXITCODE -eq 0) {
  Write-Host "✅ Data load complete" -ForegroundColor Green
} else {
  Write-Host "❌ Data load failed" -ForegroundColor Red
  exit 1
}

Write-Host ""

# Step 3: Compute MDI
Write-Host "📊 Step 3/4: Computing MDI metrics..." -ForegroundColor Yellow
python -m etl.calculate_mdi
if ($LASTEXITCODE -eq 0) {
  Write-Host "✅ MDI computation complete" -ForegroundColor Green
} else {
  Write-Host "❌ MDI computation failed" -ForegroundColor Red
  exit 1
}

Write-Host ""

# Step 4: Detect Anomalies
Write-Host "🚨 Step 4/4: Detecting anomalies..." -ForegroundColor Yellow
python -m etl.detect_anomalies
if ($LASTEXITCODE -eq 0) {
  Write-Host "✅ Anomaly detection complete" -ForegroundColor Green
} else {
  Write-Host "❌ Anomaly detection failed" -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "✨ ETL Pipeline completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📈 Next step: Connect Tableau to the database" -ForegroundColor Cyan
Write-Host "   PostgreSQL: localhost:5432 / doomscroll_db" -ForegroundColor White
