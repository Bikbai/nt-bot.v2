import os
from enum import Enum
from discord.components import SelectOption

from utility import log_critical

BOT_TOKEN = os.environ.get('BOT_TOKEN')
if BOT_TOKEN is None:
    log_critical(f"Не задан секретный токен бота.")
    while BOT_TOKEN is None:
        BOT_TOKEN = input("Введите секретный токен бота, может быть указан в переменной окружения BOT_TOKEN:")
GUILD_LIST_URL = 'http://nordic-tribe.ru/guildlist.php'
GL_FILENAME = './data/guild.txt'
TR_FILENAME = "./data/timeroles.json"
SLEEP_DELAY = os.environ.get("SLEEP_DELAY", 3600)

# константы, определяющие названия ролей
class RolesEnum(Enum):
    ADMIN_ROLE = 'Администрация'
    PLAYER_ROLE = 'Участник'
    UNCONFIRM_ROLE = 'Неподтверждённые'
    BOT_ROLE = 'Bot'
    REQRUITER_ROLE = 'Рекрутеры'
    NEWBIE_ROLE = 'Новичок'
    TRIAL_ROLE = 'Аудит'
    CHILL_ROLE = 'Чилл'
    VAC_ROLE = 'Отпуск'
    PENY_ROLE = 'Штрафник'

    @classmethod
    def known_timeroles(cls):
        return {
            # сюда вписываем список доступных ролей для тайм-роли
            cls.CHILL_ROLE.name: "Освобождение от КТА на указанный срок",
            cls.NEWBIE_ROLE.name: "Новичок на произвольный срок",
            cls.VAC_ROLE.name: "После истечения срока можно будет уточнить наличие",
            cls.PENY_ROLE.name: "Чтобы отследить - выплатил ли штраф",
        }

    @classmethod
    def BuildSelectOption(cls) -> list[SelectOption]:
        lst = list()
        kt = cls.known_timeroles()
        for key, value in kt.items():
            lst.append(SelectOption(label=str(RolesEnum[key].value), value=str(RolesEnum[key].value), description=value))
        lst[0].default = True
        return lst
