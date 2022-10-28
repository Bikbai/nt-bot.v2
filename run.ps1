Write-Host "Настройка виртуальной инфраструктуры venv"
python -m venv venv
Write-Host "Активация виртуализации"
venv\Scripts\activate
Write-Host "Апгрейд необходимых для бота пакетов"
pip install --upgrade -r requirements.txt
Write-Host "Проверка наличия переменной окружения"
if (-not (Test-Path 'env:BOT_TOKEN')) {
    $path = Read-Host -Prompt 'Введите секретный токен бота'
    $env:BOT_TOKEN= $path
}
Write-Host "Стартуем"
python .\src\main.py
venv\Scripts\deactivate