from time import time
from datetime import datetime, timedelta

import discord
from discord import ApplicationContext, SelectOption, WebhookMessage, Interaction
from discord.utils import get

import utility
from constant import RolesEnum
from ntbot import NtBot


class CommandContext:
    bot: NtBot
    duration: int = 0
    member: discord.Member
    selectedRole: discord.Role
    timeRoleList: list[SelectOption]

    def __init__(self, duration, member: discord.Member, bot: NtBot):
        self.duration = duration
        self.member = member
        self.bot = bot
        self.timeRoleList = RolesEnum.BuildSelectOption()
        # первая роль по-умолчанию выбрана
        self.timeRoleList[0].default = True
        self.selectedRole = get(self.member.guild.roles, name=self.timeRoleList[0].value)

    async def saveRole(self, interaction: discord.Interaction):
        #do some shit
        await self.bot.add_timed_role(member=self.member, role=self.selectedRole, ed=self.getDurationTS())
        await interaction.response.edit_message(content=f"Роль {self.selectedRole.name} для {self.member.display_name} длительностью {self.duration} дней сохранена.", view=None, delete_after=10)
        return

    def getDurationTS(self):
        return (datetime.now() + timedelta(days=self.duration)).timestamp()

    def selectRole(self, name: str):
        self.selectedRole = get(self.member.guild.roles, name=name)
        for r in self.timeRoleList:
            if r.label == name:
                r.default = True
            else:
                r.default = False


class DurationModal(discord.ui.Modal):
    tc: CommandContext

    def __init__(self, tc: CommandContext) -> None:
        self.tc = tc
        item = discord.ui.InputText(label="Длительность роли, в днях:", value=str(tc.duration))
        super().__init__(item, title="Введите длительность временной роли")

    async def callback(self, interaction: discord.Interaction):
        if str.isdecimal(self.children[0].value):
            self.tc.duration = int(self.children[0].value)
        await interaction.response.defer()
        return


class TimeRoleViewController:

    @classmethod
    async def handle(cls, interaction: discord.Interaction, tc: CommandContext):
        v = TimeRoleViewController.buildView(tc=tc)
        await interaction.message.edit(view=v)

    @classmethod
    def buildView(cls, tc: CommandContext) -> discord.ui.View:
        v = TimeRoleView(tc=tc)
        v.handle = cls.handle
        return v


class TimeRoleView(discord.ui.View):
    cctx: CommandContext

    def __init__(self, tc: CommandContext):
        self.cctx = tc
        super().__init__()
        dropdown = discord.ui.Select(row=1, placeholder="Выберите роль", options=self.cctx.timeRoleList)
        dropdown.callback = self.select_callback
        self.add_item(dropdown)
        lblDuration = discord.ui.Button(row=2, label="Длительность роли: ", disabled=True, style=discord.ButtonStyle.secondary)
        button = discord.ui.Button(row=2, label=str(self.cctx.duration), style=discord.ButtonStyle.secondary)
        button.callback = self.button_click
        self.add_item(lblDuration)
        self.add_item(button)
        saveBtn = discord.ui.Button(row=3, label="Сохранить", style=discord.ButtonStyle.primary)
        saveBtn.callback = self.cctx.saveRole
        self.add_item(saveBtn)

    async def select_callback(self, interaction: discord.Interaction): # the function called when the user is done selecting options
        self.cctx.selectRole(self.children[0].values[0])
        await interaction.response.defer()

    async def button_click(self, interaction: discord.Interaction):
        modal = DurationModal(tc=self.cctx)
        await interaction.response.send_modal(modal)
        await modal.wait()
        await self.handle(interaction=interaction, tc=self.cctx)

    async def handle(self, interaction, tc):
        pass

