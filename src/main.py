import colorama
import os
from discord.ext import commands

colorama.init()
import constant as c
import ntbot
from timerole import CommandContext, TimeRoleViewController, DurationModal
import discord
from utility import log_warning, log_info

bot = ntbot.NtBot()

@bot.user_command()  # Create a global user command
async def newbie(ctx: discord.ApplicationContext, member: discord.Member):
    cctx = CommandContext(duration=30, member=member, bot=bot)
    modal = DurationModal(tc=cctx)
    await ctx.response.send_modal(modal)
    await modal.wait()

    msg = await bot.add_timed_role(member=member,
                             role=bot.known_roles[c.RolesEnum.NEWBIE_ROLE.name],
                             ed=cctx.getDurationTS())
    await ctx.send(f"Новичок: {msg}", delete_after=15)


@bot.user_command()  # Create a global user command
async def timerole(ctx: discord.ApplicationContext, member: discord.Member):  # User commands give a member param
    # тут контекст хранить бесполезно, ибо view не в диалоге работает и нельзя ждать окончания, как у модалки
    view = TimeRoleViewController.buildView(CommandContext(duration=30, member=member, bot=bot))
    # вся логика обработки команды - внутри view + контекста TRContext
    await ctx.respond("Назначение временной роли", view=view)


@bot.user_command()  # Create a global user command
async def check(ctx: discord.ApplicationContext, member: discord.Member):  # User commands give a member param
    await ctx.respond(content="Запуск проверок...", delete_after=10)
    msg = await bot.validate_member(member, True)
    await ctx.followup.send(content=msg, ephemeral=True)
    await bot.validate_timed_roles_cmd(ctx=ctx, member=member)


@bot.event
async def on_command_error(context, exception):
    if isinstance(exception, commands.CommandNotFound):
        pass

try:
    bot.run(c.BOT_TOKEN)
except Exception as e:
    log_info(f"Поймали исключение: {e}")

