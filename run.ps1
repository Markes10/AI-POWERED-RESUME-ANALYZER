$ErrorActionPreference = 'Stop'

$RootDir = (Get-Location).Path
$BackendUrl = 'http://localhost:8000/health'
$FrontendUrl = 'http://localhost:8080'

Write-Host '=================================================== '
Write-Host '         AI Resume Analyzer - Start All'
Write-Host '=================================================== '
Write-Host ''

# Detect Python
$PyCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $PyCmd = 'python'
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $PyCmd = 'py'
} else {
    Write-Error 'Python not found in PATH. Install Python 3.11+ and add it to PATH.'
    exit 1
}

# Ensure venv exists
$VenvDir = Join-Path $RootDir '.venv'
$VenvPython = Join-Path $VenvDir 'Scripts\python.exe'
if (-not (Test-Path $VenvPython)) {
    Write-Host '[1/4] Creating Python virtual environment (.venv)...'
    & $PyCmd -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Error 'Failed to create virtual environment.'
        exit 1
    }
}

# Install Python deps
Write-Host '[1/4] Installing Python dependencies...'
& $VenvPython -m pip install --upgrade pip *> $null
& $VenvPython -m pip install -r (Join-Path $RootDir 'requirements.txt')
if ($LASTEXITCODE -ne 0) {
    Write-Warning 'Python dependency install completed with errors. Retry manually with:'
    Write-Warning "   $VenvPython -m pip install -r requirements.txt"
}
else {
    Write-Host '[OK] Python dependencies installed.'
}

# Install Node deps if needed
if (-not (Test-Path (Join-Path $RootDir 'node_modules'))) {
    Write-Host '[2/4] Installing Node dependencies...'
    & npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Warning 'npm install failed. You can retry manually in this folder.'
    }
    else {
        Write-Host '[OK] Node dependencies installed.'
    }
}
else {
    Write-Host '[2/4] Node dependencies found.'
}

Write-Host ''
Write-Host '[3/4] Starting FastAPI backend on port 8000...'
Start-Process -FilePath $VenvPython -ArgumentList '-m uvicorn main:app --host 0.0.0.0 --port 8000 --reload' -WorkingDirectory $RootDir

Write-Host '[4/4] Starting Vite frontend on port 8080...'
Start-Process -FilePath 'npm' -ArgumentList 'run dev -- --host 0.0.0.0' -WorkingDirectory $RootDir

Write-Host ''
Write-Host '=================================================== '
Write-Host '  All services starting (or attempted).'
Write-Host ''
Write-Host "  Frontend : $FrontendUrl"
Write-Host '  Backend  : http://localhost:8000'
Write-Host '  API Docs : http://localhost:8000/api/docs'
Write-Host '=================================================== '
Write-Host ''

# Wait for backend health
$BackendReady = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri $BackendUrl -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $BackendReady = $true
            break
        }
    }
    catch {
        Start-Sleep -Seconds 1
    }
}

if ($BackendReady) {
    Write-Host '[OK] Backend health check passed.'
}
else {
    Write-Warning 'Backend health check did not respond yet. Check http://localhost:8000 manually.'
}

Start-Process $FrontendUrl
Read-Host 'Press Enter to exit'
