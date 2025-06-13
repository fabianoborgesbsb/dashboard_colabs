@echo off
cls
echo =====================================
echo 🚀 Iniciando o dashboard STI...
echo =====================================

REM === Defina aqui o caminho da sua pasta do projeto ===
set "PROJ_DIR=file path\dashboard_colabs"

cd /d "%PROJ_DIR%"

REM === Verifica se o ambiente virtual já existe ===
if not exist ".venv" (
    echo 📦 Criando ambiente virtual .venv...
    python -m venv .venv
)

REM === Ativa o ambiente virtual ===
call .venv\Scripts\activate.bat

REM === Instala as dependências ===
echo 🔧 Instalando dependências...
pip install -r requirements.txt

REM === Executa o Streamlit ===
echo 🧭 Iniciando o Streamlit...
streamlit run app.py

pause
