@echo off
REM Script para iniciar o PhoneAid LED Controller no Windows

cd /d "%~dp0"

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Instale Python 3.8+ de python.org
    pause
    exit /b 1
)

REM Verifica se PyQt5 está instalado
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  PyQt5 não instalado. Instalando dependências...
    pip install PyQt5 pyserial
)

REM Inicia a aplicação
echo 🚀 Iniciando PhoneAid LED Controller...
python app/main.py

if errorlevel 1 (
    echo ❌ Erro ao iniciar aplicação
    pause
)
