# Script para iniciar o PhoneAid LED Controller no Windows PowerShell

$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptPath

# Define PYTHONPATH
$env:PYTHONPATH = "$ScriptPath;$($env:PYTHONPATH)"

Write-Host "🚀 Iniciando PhoneAid LED Controller..." -ForegroundColor Green

# Verifica se Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado! Instale Python 3.8+ de https://python.org" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verifica se PyQt5 está instalado
try {
    python -c "import PyQt5" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "PyQt5 não instalado"
    }
    Write-Host "✅ PyQt5 encontrado" -ForegroundColor Green
} catch {
    Write-Host "⚠️  PyQt5 não instalado. Instalando dependências..." -ForegroundColor Yellow
    pip install PyQt5 pyserial
}

# Inicia a aplicação
Write-Host "Iniciando aplicação..." -ForegroundColor Cyan
python app/main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao iniciar aplicação" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}
