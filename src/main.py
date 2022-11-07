import datetime

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

@bot.user_command()
async def fix_noob(ctx: discord.ApplicationContext, member: discord.Member):
    await ctx.respond(content="Запуск проверок...", delete_after=10)
    tmp_roles= [['07.10.2022', 'Tumiou',21],
                ['11.10.2022', 'DekaEmp',14],
                ['11.10.2022', 'Satygatt',14],
                ['19.10.2022', 'Mateuszik',30],
                ['19.10.2022', 'Masturbek3000',30],
                ['19.10.2022', 'D0KO0',21],
                ['19.10.2022', 'BlitzTime',30],
                ['20.10.2022', 'Ruandrgarius',30],
                ['20.10.2022', 'Kyoudan',14],
                ['20.10.2022', 'ewrxxrs',3],
                ['21.10.2022', 'qLucky',21],
                ['21.10.2022', 'uzuk228',21],
                ['21.10.2022', 'Orcs',21],
                ['21.10.2022', 'Ozz0',21],
                ['21.10.2022', 'Pbl6ka',14],
                ['21.10.2022', 'xGladxPWNZx',21],
                ['22.10.2022', 'Soullar',14],
                ['22.10.2022', 'Deminist',14],
                ['23.10.2022', 'Dragonil0730',14],
                ['23.10.2022', 'exStela',30],
                ['24.10.2022', 'LiveYouLife',14],
                ['24.10.2022', 'TAV3RON',7],
                ['24.10.2022', 'w1zik',7],
                ['24.10.2022', 'Toom4ik',14],
                ['24.10.2022', 'vddd',14],
                ['24.10.2022', 'YakovRabinovich',14],
                ['24.10.2022', 'psyxxo',14],
                ['25.10.2022', 'ArguSiK',30],
                ['25.10.2022', 'IDominatingI',30],
                ['26.10.2022', 'Saitaf',30],
                ['26.10.2022', 'AveVeretas',30],
                ['26.10.2022', 'iogansb',21],
                ['27.10.2022', 'HomaZyarazhai',28],
                ['28.10.2022', 'Sovnegard',14],
                ['28.10.2022', 'MbIWb24',14],
                ['28.10.2022', 'zSTALKERz',28],
                ['28.10.2022', 'Xisilaria',14],
                ['28.10.2022', 'Ze1d',28],
                ['28.10.2022', 'Alwaysdie',28],
                ['29.10.2022', 'Andreisuh',31],
                ['29.10.2022', 'zippo4ka',14],
                ['30.10.2022', 'Forenum',14],
                ['30.10.2022', 'Chefir89',14],
                ['30.10.2022', 'Apabgin',14],
                ['31.10.2022', 'АnosVoldigoad555',14],
                ['31.10.2022', 'MrDmitrik',28],
                ['31.10.2022', 'Krasatulia',7],
                ['31.10.2022', 'MainZlo',14],
                ['01.11.2022', 'Shapery',30],
                ['01.11.2022', 'Raktys1500',14],
                ['01.11.2022', 'Arrrrhon',21],
                ['01.11.2022', 'Egermecter',21],
                ['01.11.2022', 'FriendliAlf',21],
                ['01.11.2022', 'Danozavr',30],
                ['01.11.2022', 'QwantumRU',31],
                ['01.11.2022', 'PZRK8',31],
                ['02.11.2022', 'diker007',14],
                ['04.11.2022', 'AkameMyMistress',30],
                ['04.11.2022', 'Fleksia',30],
                ['05.11.2022', 'Kazi4elo',28],
                ['05.11.2022', 'MishaMoh',28],
                ['06.11.2022', 'Ondzin',14],
                ['06.11.2022', 'lokibess',14],
                ['07.11.2022', 'Jubey',21],
                ['07.11.2022', 'Schkuralinda',21],
                ['07.11.2022', 'FunT0Play',30],
                ['07.11.2022', 'D0NAT1K',30],
                ['07.11.2022', 'Lalalissa',30],
                ['07.11.2022', 'Dolbantino',14],
                ['01.11.2022', 'Quniraya',1]]

    for v in tmp_roles:
        enddate = datetime.datetime.strptime(v[0], '%d.%m.%Y') + datetime.timedelta(days=v[2])
        for m in ctx.guild.members:
            if v[1] in m.display_name:
                await bot.add_timed_role(member=m,
                                         role=bot.known_roles[c.RolesEnum.NEWBIE_ROLE.name],
                                         ed=enddate.timestamp()
                                         )
                await ctx.followup.send(content=f"Member: {m.display_name}, set newbie role until: {enddate}", ephemeral=True, delete_after=15)
    pass


@bot.event
async def on_command_error(context, exception):
    if isinstance(exception, commands.CommandNotFound):
        pass

try:
    bot.run(c.BOT_TOKEN)
except Exception as e:
    log_info(f"Поймали исключение: {e}")

