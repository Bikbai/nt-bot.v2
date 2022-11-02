echo off
chcp 65001
echo Обновление программы
git pull
echo Настройка виртуальной инфраструктуры venv
python -m venv venv
echo Активация виртуализации"
call venv\Scripts\activate
echo Апгрейд необходимых для бота пакетов
pip install --upgrade -r requirements.txt
echo Стартуем
python .\src\main.py
call venv\Scripts\deactivate