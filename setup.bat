@echo off
echo Setting up AI Recruitment Assistant...

REM Create necessary directories
if not exist ".streamlit" mkdir .streamlit
if not exist "temp" mkdir temp

REM Install dependencies
pip install -r requirements.txt

REM Create default secrets template
if not exist ".streamlit\secrets.toml" (
    echo # MongoDB connection (optional) > .streamlit\secrets.toml
    echo MONGODB_URI = "mongodb://localhost:27017" >> .streamlit\secrets.toml
)

echo Setup complete!
echo Run: streamlit run app.py
pause
