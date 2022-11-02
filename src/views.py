import asyncio
import time
import discord
import datetime as d

from constant import RolesEnum
from discord import SelectOption, ApplicationContext
from discord.utils import get


class TimeRoleView(discord.ui.View):
    bot = None
    selectedRole: discord.Role = None
    member: discord.Member = None
    timeRoleList: list[SelectOption] = RolesEnum.BuildSelectOption()
    _ctx: ApplicationContext = None

    def __init__(self, ctx: ApplicationContext):
        super().__init__()
        self._ctx = ctx


    @discord.ui.button(row=2, label="Срок действия, дней:", disabled=True, style=discord.ButtonStyle.secondary)
    async def button1_callback(self, button, interaction):
        await interaction.response.defer()

    @discord.ui.button(row=2, label="30", style=discord.ButtonStyle.secondary)
    async def button2_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        modal = TimeRoleModal("SampleTitle")
        await self._ctx.send_modal(modal)
        await interaction.response.defer()

    @discord.ui.button(label="Submit", row=3, style=discord.ButtonStyle.primary)
    async def button5_callback(self, button, interaction):
        self.disable_all_items()

        await self.bot.add_timed_role(role=self.selectedRole, member=self.member)
        await interaction.response.send_message(f"S: {self.selectedRole.id}")





