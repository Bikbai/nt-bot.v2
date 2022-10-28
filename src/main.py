import colorama
colorama.init()
import constant as c
import ntbot
from timerole import CommandContext, TimeRoleViewController, DurationModal
import discord

bot = ntbot.NtBot()


@bot.user_command()  # Create a global user command
async def newbie(ctx: discord.ApplicationContext, member: discord.Member):
    cctx = CommandContext(duration=30, member=member, bot=bot)
    modal = DurationModal(tc=cctx)
    await ctx.response.send_modal(modal)
    await modal.wait()

    msg = await bot.add_timed_role(member=member,
                             role=bot.known_roles[c.RolesEnum.NEWBIE_ROLE.name],
                             ed=cctx.getDurationTS(),
                             nextrole=bot.known_roles[c.RolesEnum.TRIAL_ROLE.name]
                             )
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


@bot.slash_command()  # Create a slash command
async def rp_hello(ctx: discord.ApplicationContext):
    """Say hello to the bot"""  # The command description can be supplied as the docstring
    await ctx.respond(f"Hello {ctx.author}!")

bot.run(c.BOT_TOKEN)
