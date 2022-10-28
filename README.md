# nt-bot.v2

Перед установкой настраиваем питон, запустив следующие команды под правами админа:
```
  python -m ensurepip
  python -m pip install --upgrade pip
```

Далее запускаем powershell и идём в нужный путь, куда будем ставить бота
```
  powershell
  cd %НУЖНЫЙ ПУТЬ%
```

Далее команды:
```
git clone https://github.com/Bikbai/nt-bot.v2.git
cd nt-bot.v2
.\run.ps1
```

Командный файл спросит значение секретного токена бота, который можно на машине прописать в переменную окружения BOT_TOKEN

Последующие запуски - запуск в Powershell run.ps1
