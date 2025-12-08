#!/bin/bash
# Script para iniciar o PhoneAid LED Controller no Linux/Mac

cd "$(dirname "$0")"

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado! Instale Python 3.8+"
    exit 1
fi

# Verifica se PyQt5 está instalado
python3 -c "import PyQt5" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  PyQt5 não instalado. Instalando dependências..."
    pip3 install PyQt5 pyserial
fi

# Inicia a aplicação
echo "🚀 Iniciando PhoneAid LED Controller..."
python3 app/main.py

if [ $? -ne 0 ]; then
    echo "❌ Erro ao iniciar aplicação"
    exit 1
fi
