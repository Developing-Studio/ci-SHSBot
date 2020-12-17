from typing import Mapping
import typing
import discord
import platform
import time
import random
import asyncio
import re, os
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
import aiosqlite
import inspect
OWNER_ID = 267410788996743168
# CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL CREDIT TO KAL
# oh and also credit to kal

class HelpCommand(commands.HelpCommand):
    """Sup averwhy hopefully this is all easy to understand."""

    # This fires once someone does `<prefix>help`
    async def send_bot_help(self, mapping: Mapping[typing.Optional[commands.Cog], typing.List[commands.Command]]):
        ctx = self.context
        clr = discord.Color.random()
        embed = discord.Embed(title="SHS Commands & Help", color=clr)
        embed.set_footer(text=f"Do {self.clean_prefix}help [command] for more info on a command or category")
        categories = []
        for cog, cmds in mapping.items():
            filtered = await self.filter_commands(cmds, sort=True)
            if filtered:
                all_commands = " ".join(f"`{c.name}`  " for c in cmds)
                if cog and cog.description:
                    embed.add_field(name=cog.qualified_name,
                                    value=f"-> {all_commands}",
                                    inline=False)

        await ctx.send(embed=embed)

    # This fires once someone does `<prefix>help <cog>`
    async def send_cog_help(self, cog: commands.Cog):
        ctx = self.context
        embed = discord.Embed(title=f"Help for {cog.qualified_name}")
        embed.set_footer(text=f"Do {self.clean_prefix}help [command] for more help")

        entries = await self.filter_commands(cog.get_commands(), sort=True)
        for cmd in entries:
            embed.add_field(name=f"{self.clean_prefix}{cmd.name} {cmd.signature}",
                            value=f"{cmd.help}",
                            inline=False)

        await ctx.send(embed=embed)

    # This fires once someone does `<prefix>help <command>`
    async def send_command_help(self, command: commands.Command):
        ctx = self.context
        embed = discord.Embed(title=f"{self.clean_prefix}{command.qualified_name} {command.signature}",
                              description=f"{command.help}")
        embed.set_footer(text=f"Do {self.clean_prefix}help [command] for more help")

        await ctx.send(embed=embed)

    # This fires once someone does `<prefix>help <group>`
    async def send_group_help(self, group: commands.Group):
        ctx = self.context

        embed = discord.Embed(title=f"{self.clean_prefix}{group.qualified_name} {group.signature}",
                              description=f"{group.help}")
        embed.set_footer(text=f"Do {self.clean_prefix}help [command] for more help")

        for command in group.commands:
            embed.add_field(name=f"{self.clean_prefix}{command.name} {command.signature}",
                            value=command.description,
                            inline=False)

        await ctx.send(embed=embed)


class meta(commands.Cog):
    """
    These are meta about the bot.
    """
    def __init__(self,bot):
        self.bot = bot

        self.bot._original_help_command = bot.help_command

        bot.help_command = HelpCommand()
        bot.help_command.cog = self
    
    def cog_unload(self):
        self.bot.help_command = self.bot._original_help_command
    
    @commands.cooldown(1,10,BucketType.channel)
    @commands.command(aliases=["i"])
    async def info(self,ctx):
        await ctx.send("hi")
    
    @commands.cooldown(1,10,BucketType.user)
    @commands.command()
    async def uptime(self, ctx):
        delta_uptime = datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"```autohotkey\n{days}d, {hours}h, {minutes}m, {seconds}s\n```")

        
    # CREDIT TO RAPPTZ FOR THIS
    # https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/meta.py#L355-L393
    @commands.command()
    @commands.is_owner() # temp
    async def source(self, ctx, *, command: str = None):
        source_url = 'https://github.com/averwhy/EconomyX'
        branch = 'main/src'
        if command is None:
            return await ctx.send(source_url)
        
        if command == 'help':
            await ctx.send("The help command is built into discord.py. However, the code for that can be found here:\n<https://github.com/Rapptz/discord.py/blob/master/discord/ext/commands/help.py>")
            return
        if command == 'jsk' or command == 'jishaku':
            await ctx.send("Jishaku is a debug and testing command made for discord.py. The code can be found here:\n<https://github.com/Gorialis/jishaku>")
            return
        else:
            obj = self.bot.get_command(command.replace('.', ' '))
            if obj is None:
                return await ctx.send('Could not find command.')

            # since we found the command we're looking for, presumably anyway, let's
            # try to access the code itself
            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith('discord'):
            # not a built-in command
            location = os.path.relpath(filename).replace('\\', '/')
        else:
            location = module.replace('.', '/') + '.py'

        final_url = f'<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>'
        await ctx.send(final_url)
        
    @commands.command()
    async def ping(self, ctx):
        em = discord.PartialEmoji(name="loading",animated=True,id=782995523404562432)
        
        #typing check
        start = time.perf_counter()
        message = await ctx.send(embed=discord.Embed(title=f"Ping... {em}",color=discord.Color.random()))
        end = time.perf_counter()
        
        #db ping checker
        start2 = time.perf_counter()
        c = await self.bot.db.execute("SELECT * FROM pittdar")
        data = await c.fetchone()
        await self.bot.db.commit()
        end2 = time.perf_counter()
        
        #do mafs
        duration = round(((end - start) * 1000),1)
        db_duration = round(((end2 - start2) * 1000),1)
        newembed = discord.Embed(title="Pong!",color=discord.Color.random())
        ws = round((self.bot.latency * 1000),1)
        typing_emote = discord.PartialEmoji(name="typing",animated=True,id=784148703149424650)
        sqlite_emote = discord.PartialEmoji(name="sqlite",animated=False,id=784151151472934942)
        
        #now make it pretty
        newembed.add_field(name=f"{typing_emote} Typing",value=f"{duration}ms")
        newembed.add_field(name="📶 Websocket",value=f"{ws}ms")
        newembed.add_field(name=f"{sqlite_emote} Database",value=f"{db_duration}ms")
        await message.edit(embed=newembed)


        

        
def setup(bot):
    bot.add_cog(meta(bot))
