@echo off
cls
echo =====================================
echo Dashboard ...
echo =====================================

REM === path file ===
set "PROJ_DIR=C:\Fabiano Borges 2019\Meus estudos cientometria  2021\Arquivos Python\tabelaconsolidada_2024_400mil\bienio_QGIS_dashboard\4 STI cognitive\dashboard_colabs"

cd /d "%PROJ_DIR%"

REM === check env ===
if not exist ".venv" (
    echo 📦 Criando ambiente virtual .venv...
    python -m venv .venv
)

REM === Activate ===
call .venv\Scripts\activate.bat

REM === dependencies ===
echo 🔧 Instalando dependências...
pip install -r requirements.txt

REM === Execute the Streamlit ===
echo 🧭 Iniciando o Streamlit...
streamlit run app.py

pause
