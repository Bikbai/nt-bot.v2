import asyncio
import sys
from datetime import datetime, timedelta
from time import time, time_ns
import os
from dataclasses import dataclass
from typing import Optional
from urllib import request
import discord
from discord.ext import commands
import jsonpickle
from discord.utils import get

from utility import log_warning, log_critical, log_info, parse_name
import constant as c


@dataclass
class TimeRole:
    memberid: int
    roleid: int
    endDate: float
    member_display_name: Optional[str]
    nextRoleId: int


class TimeRoles:
    _storage: list[TimeRole] = list()

    def load(self) -> bool:
        if os.path.exists(c.TR_FILENAME):
            try:
                with open(c.TR_FILENAME, "r") as file:
                    s = file.read()
                    if len(s) < 1:
                        return True
                    self._storage = jsonpickle.decode(s)
            except Exception as e:
                log_critical(f"Ошибка чтения файла {c.TR_FILENAME}: {e}")
                return False
        return True

    def delete(self, tr: TimeRole):
        for v in self._storage:
            if v.memberid == tr.memberid and v.roleid == tr.roleid:
                self._storage.remove(tr)
                self.save()
        return

    def save(self):
        try:
            with open(c.TR_FILENAME, "w") as file:
                jsonpickle.set_preferred_backend('json')
                jsonpickle.set_encoder_options('json', ensure_ascii=False)
                tr_json = jsonpickle.encode(self._storage, unpicklable=True, indent=4)
                file.write(tr_json)
        except Exception as e:
            log_critical(f"Ошибка записи в файл {c.TR_FILENAME}: {e}")
        return True

    def merge(self, tr: TimeRole):
        if tr.endDate <= time():
            self.delete(tr)
            return 'D'
        val: TimeRole
        for val in self._storage:
            if val.roleid == tr.roleid and val.memberid == tr.memberid:
                val.endDate = tr.endDate
                val.nextRoleId = tr.nextRoleId
                val.member_display_name = tr.member_display_name
                self.save()
                return 'U'
        self._storage.append(tr)
        self.save()
        return 'I'

    def find(self, member: discord.Member, role: discord.Role) -> Optional[TimeRole]:
        for v in self._storage:
            if v.memberid == member.id and v.roleid == role.id:
                return v
        return None


class NtBot(commands.Bot):
    known_roles: dict[str, discord.Role] = dict()
    __guild_list = dict()
    trStorage: TimeRoles = TimeRoles()

    def __init_token__(self):
        if c.BOT_TOKEN is not None:
            return
        if c.BOT_TOKEN is None:
            if os.path.exists(c.TOKEN_FILENAME):
                with open(c.TOKEN_FILENAME, "r") as file:
                    c.BOT_TOKEN = file.readline()
                    if c.BOT_TOKEN is not None:
                        return
                    log_warning(f"Не задан секретный токен бота в переменной окружения, считан из файла")

        while c.BOT_TOKEN is None:
            c.BOT_TOKEN = input(
                "Введите секретный токен бота, может быть указан в переменной окружения BOT_TOKEN:")
        with open(c.TOKEN_FILENAME, "w") as file:
            file.write(c.BOT_TOKEN)
            log_warning(f"Cекретный токен бота сохранён в файле {c.TOKEN_FILENAME}")

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        self.__init_token__()
        super().__init__(
            command_prefix=commands.when_mentioned_or("rp!"), intents=intents
        )

    async def on_ready(self):
        log_info(f"Logged in as {self.user} (ID: {self.user.id})")
        log_info(f"init roles")
        success = self.__init_roles()
        if success:
            log_info(f"done. loading guild list")
            success = self.fill_guildlist()
            if success:
                log_info(f"done. loading timed roles")
                success = self.trStorage.load()
                if success:
                    start_time = datetime.now()

                    log_info(f"done. starting main loop")
                    while True:
                        if start_time + timedelta(hours=24) < datetime.now():
                            log_info(f'Перезагрузка бота для обновления')
                            sys.exit()
                        log_info(f'Запуск проверки')
                        await self.check_guild()
                        log_info(f"Следующая проверка в: {datetime.fromtimestamp(time() + c.SLEEP_DELAY)}")
                        await asyncio.sleep(c.SLEEP_DELAY)

        return

    def __init_roles(self) -> bool:
        for a in c.RolesEnum:
            dcGuild: discord.Guild
            for dcGuild in self.guilds:
                role = discord.utils.get(dcGuild.roles, name=a.value)
                if role is None:
                    err = f"Сервер: {dcGuild.name}, не найдена роль {a.value}"
                    log_critical(err)
                    return False
                self.known_roles[str(a.name)] = role
        return True

    def fill_guildlist(self):
        self.__guild_list.clear()
        log_info('Читаем список мемберов с сайта гильдии')
        try:
            request.urlretrieve(c.GUILD_LIST_URL, c.GL_FILENAME)
        except:
            log_critical("Не удалось скачать список мемберов!")
            return False
        if os.path.exists(c.GL_FILENAME):
            with open(c.GL_FILENAME, "r") as file:
                for line in file:
                    line = line.strip().lower()
                    self.__guild_list.update({line: 0})
        else:
            log_critical("Не удалось скачать список мемберов!")
            return False
        log_info("Количество членов гильдии: {}".format(len(self.__guild_list)))
        return True

    async def saveRole(self, interaction: discord.Interaction):
        await interaction.message.edit(content=f"Роль успешно сохранена.", view=None, delete_after=15)

    async def add_timed_role(self, member: discord.Member, role: discord.Role, ed: float) -> (str):
        try:
            nextRoleId = self.known_roles[c.RolesEnum.TRIAL_ROLE.name].id
            tr = TimeRole(member.id, role.id, ed, member.display_name, nextRoleId)
            code = self.trStorage.merge(tr)
            match code:
                case "I":
                    log_warning(f"Временная роль добавлена пользователю {member.display_name}")
                    msg = "Роль добавлена"
                case "U":
                    msg = "Роль продлена"
                case "D":
                    msg = "Роль удалена"
                case _:
                    raise Exception(f"self.trStorage.merge: неизвестный код возврата {code}")
            await member.add_roles(get(member.guild.roles, id=role.id))
            await asyncio.sleep(1)
            return msg
        except Exception as e:
            return str(e)

    async def validate_member(self, member: discord.Member, writeMode: bool = False) -> str:
        # разбираем ник дискорда
        m = parse_name(member.display_name)
        try:
            # если бот - сразу выходим
            if self.isBot(member) or self.isOfficier(member):
                result = f"Пользователь {member.display_name}: бот или офицер, проверки не требуются"
                log_info(result)
                return result
            if not self.isPlayer(member):
                result = f"Пользователь {member.display_name} - не участник, проверки не требуются"
                log_info(result)
                return result
            # если роль "Участник" и корявый ник - выходим, ставим "Неподтверждённые"
            if not m["valid"] and not self.isUnconfirmed(member):
                if writeMode:
                    await member.add_roles(get(member.guild.roles, id=self.known_roles['UNCONFIRM_ROLE'].id))
                    await asyncio.sleep(1)
                result = f"Формат имени пользователя {member.display_name} некорректный, выставлена роль Неподтверждённые!"
                log_warning(result)
                return result
            # если нет в списке гильдии - выходим, ставим "Неподтверждённые"
            if m["ingameName"] not in self.__guild_list:
                result = f"Пользователь {member.display_name} не найден в гильдии, выставлена роль Неподтверждённые"
                if writeMode:
                    await member.add_roles(get(member.guild.roles, id=self.known_roles['UNCONFIRM_ROLE'].id))
                    await asyncio.sleep(1)
                log_warning(result)
                return result
            if self.isUnconfirmed(member):
                result = f"Пользователь {member.display_name} проверки прошёл успешно, очищаем роль Неподтверждённые"
                log_warning(result)
                await member.remove_roles(get(member.guild.roles, id=self.known_roles['UNCONFIRM_ROLE'].id))
                await asyncio.sleep(1)
                return result
            return f"{member.display_name}: все проверки проведены - ошибок нет"
        except Exception as e:
            return str(e)

    def isOfficier(self, member: discord.Member) -> bool:
        pname = parse_name(member.display_name)
        if pname['valid'] and pname['officier'] == '*' and self.isPlayer(member):
            return True
        return False

    def isAdmin(self, member: discord.Member):
        if get(member.roles, id=self.known_roles['PLAYER_ROLE'].id) is None:
            return False
        return True

    def isBot(self, member: discord.Member):
        if get(member.roles, id=self.known_roles['BOT_ROLE'].id) is None:
            return False
        return True

    def isReqruiter(self, member: discord.Member):
        if get(member.roles, id=self.known_roles['REQRUITER_ROLE'].id) is None:
            return False
        return True

    def isPlayer(self, member: discord.Member):
        if get(member.roles, id=self.known_roles["PLAYER_ROLE"].id) is None:
            return False
        return True

    def isUnconfirmed(self, member: discord.Member):
        if get(member.roles, id=self.known_roles["UNCONFIRM_ROLE"].id) is None:
            return False
        return True

    async def check_guild(self):
        self.fill_guildlist()
        g: discord.Guild
        for g in self.guilds:
            t = time_ns()
            log_info(f"Старт цикла проверки сервера: {g.name}")
            m: discord.Member
            for m in g.members:
                if self.isBot(m):
                    continue
                log_info(f"Проверка мембера: {m.display_name}")
                await self.validate_member(m, True)
                log_info(f"Проверка ролей мембера: {m.display_name}")
                await self.validate_timed_roles(m)
            log_info(f"Цикл проверки сервера {g.name} закончен, затрачено {(time_ns() - t) / 1000000} мс")

    async def __validate_timed_role__(self,
                                      member: discord.Member,
                                      role: discord.Role) -> (int, Optional[str]):
        """
        внутренний механизм проверки, возвращает код ошибки и строку сообщения
        -1: Ошибка
         0: Роль не является временной
         1: Роль временная и действует
         2: Роль временная и очищена
        """
        if role is None:
            msg = f"__validate_timed_role__: Ошибка! Передана пустая роль туда, куда не следует!!!"
            log_critical(msg)
            return -1, msg
        iTr = self.trStorage.find(member, role)
        if iTr is None:
            return 0, "Ок, временная роль не найдена"
        # всё есть, проверяем - жива или нет. Если просрочена - очищаем
        msg = f"Мембер {member.display_name}, найдена временная роль {role.name}, срок до {datetime.fromtimestamp(iTr.endDate)}"
        log_info(msg)
        if iTr.endDate < time():
            # роль не удаляется, вешается аудит
            self.trStorage.delete(iTr)
            # если выставлена подменяющая роль - выставляем
            if iTr.nextRoleId is None:
                pass
            else:
                await member.add_roles(get(member.guild.roles, id=iTr.nextRoleId))
                await asyncio.sleep(10)
                log_info(f"Добавлена роль {get(member.guild.roles, id=iTr.nextRoleId).name}")
            await member.remove_roles(get(member.guild.roles, id=iTr.roleid))
            await asyncio.sleep(10)
            msg = f"Временная роль очищена у пользователя {member.display_name}"
            log_warning(msg)
            return 2, msg
        return 1, msg

    async def dm(self, to: discord.Member, msg: str):
        if to is None:
            raise Exception("Метод dm: пустой параметр 'to'")
        dm = await self.create_dm(to)
        await dm.send(msg)
        return

    async def validate_timed_roles(self, member: discord.Member):
        """
        Метод проверки членов гильдии на предмет просроченных временных ролей
        :param member:
        :return:
        """
        if self.isBot(member):
            return
        for r in member.roles:
            await self.__validate_timed_role__(member, r)
        return

    async def validate_timed_roles_cmd(self, ctx: discord.ApplicationContext, member: discord.Member):
        """
        Метод проверки членов гильдии на предмет просроченных временных ролей
        :param member:
        :return:
        """
        if self.isBot(member) or self.isOfficier(member):
            msg = "Боты и офицеры не проверяются"
            await ctx.followup.send(content=msg, ephemeral=True)
            return
        for r in member.roles:
            code, msg = await self.__validate_timed_role__(member, r)
            if code != 0:
                await ctx.followup.send(content=msg, ephemeral=True)
        return
