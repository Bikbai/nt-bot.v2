python.exe -m pip install --upgrade pip
python -m venv venv
venv\Scripts\activate
pip install --upgrade -r requirements.txt

if (Test-Path 'env:BOT_TOKEN' == False) {
    $path = Read-Host -Prompt 'Введите секретный токен бота:'
    $env:BOT_TOKEN= $path
}
python .\src\main.py
venv\Scripts\deactivate