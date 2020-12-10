import discord
import platform
import asyncio
import re, os
from datetime import datetime
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
import aiosqlite
import inspect
import hashlib
from .utils import time
OWNER_ID = 267410788996743168

class misc(commands.Cog):
    """
    Misc commands. These dont really fall under any other category.
    """
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def sha256(self, ctx, *, text):
        """
        Encodes a message in `sha256`.
        """
        m = hashlib.sha256()
        btext = bytes(text, "utf-8")
        m.update(btext)
        await ctx.send(m.hexdigest())
        
    @commands.command()
    async def atbash(self, ctx, *, text):
        """
        Converts a message to and from Atbash.
        """
        text = text.lower() # because dict's arent case insensitive >:(
        lookup_table = {'a' : 'z', 'b' : 'y', 'c' : 'x', 'd' : 'w', 'e' : 'v', 
        'f' : 'u', 'g' : 't', 'h' : 's', 'i' : 'r', 'j' : 'q', 
        'k' : 'p', 'l' : 'o', 'm' : 'n', 'n' : 'm', 'o' : 'l', 
        'p' : 'k', 'q' : 'j', 'r' : 'i', 's' : 'h', 't' : 'g', 
        'u' : 'f', 'v' : 'e', 'w' : 'd', 'x' : 'c', 'y' : 'b', 'z' : 'a'}
        cipher = ''
        for letter in text: 
            # checks for space 
            if(letter == ' '): 
                #adds space 
                cipher += ' '
            elif(letter == '.'):
                cipher += "."
            elif(letter == "'"):
                cipher += "'"
            elif(letter == ","):
                cipher += ","
            else: 
                # adds letter
                cipher += lookup_table[letter]
        await ctx.send(cipher)
    
    @commands.command(aliases=["userinfo"])
    async def uinfo(self, ctx, *, user: discord.Member = None):
        """Shows info about a user."""

        user = user or ctx.author
        if ctx.guild and isinstance(user, discord.User):
            user = ctx.guild.get_member(user.id) or user

        e = discord.Embed()
        roles = [role.name.replace('@', '@\u200b') for role in getattr(user, 'roles', [])]
        shared = sum(g.get_member(user.id) is not None for g in self.bot.guilds)
        e.set_author(name=str(user))

        def format_date(dt):
            if dt is None:
                return 'N/A'
            return f'{dt:%Y-%m-%d %H:%M} ({time.human_timedelta(dt, accuracy=3)})'

        e.add_field(name='ID', value=user.id, inline=False)
        e.add_field(name='Servers', value=f'{shared} shared', inline=False)
        e.add_field(name='Joined', value=format_date(getattr(user, 'joined_at', None)), inline=False)
        e.add_field(name='Created', value=format_date(user.created_at), inline=False)

        voice = getattr(user, 'voice', None)
        if voice is not None:
            vc = voice.channel
            other_people = len(vc.members) - 1
            voice = f'{vc.name} with {other_people} others' if other_people else f'{vc.name} by themselves'
            e.add_field(name='Voice', value=voice, inline=False)

        if roles:
            e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles', inline=False)

        colour = user.colour
        if colour.value:
            e.colour = colour

        if user.avatar:
            e.set_thumbnail(url=user.avatar_url)

        if isinstance(user, discord.User):
            e.set_footer(text='This member is not in this server.')

        await ctx.send(embed=e)
        
    @commands.group(aliases=["pd"], invoke_without_command=True)
    async def pittdar(self, ctx, num: int = None):
        """
        The Pittdar. Weather/snow day predictions from Pitt.
        """
        if num is not None:
            c = await self.bot.db.execute("SELECT * FROM pittdar WHERE entry = ?",(num,))
            data = await c.fetchone()
            if data is None:
                await ctx.send("I couldnt find a Pittdar entry with that ID.")
                return
        else:
            c = await self.bot.db.execute("SELECT * FROM pittdar ORDER BY entry DESC")
            data = await c.fetchone()
        if data is None:
            await ctx.send("There is no Pittdar entries.")
            return
        e = discord.Embed(title=f"Pittdar Entry #{data[0]}",description=data[1],color=discord.Color.random())
        try:
            await ctx.reply(embed=e)
            return
        except:
            await ctx.send(embed=e)
            return
        
    @pittdar.command(aliases=["set"])
    async def new(self, ctx, *, content):
        if ctx.author.id not in [253010471412563970, 267410788996743168]:
            await ctx.send("Only Pitt can set a new Pittdar.")
            return
        c = await self.bot.db.execute("SELECT entry FROM pittdar ORDER BY entry DESC")
        latestentry = await c.fetchone()
        if latestentry is None:
            latestentry = -1 # zero indexed :verycool:
        else: 
            latestentry = int(latestentry[0])
        numbertoenter = latestentry + 1
        
        await self.bot.db.execute("INSERT INTO pittdar VALUES (?, ?)",(numbertoenter, content,))
        await self.bot.db.commit()
        await ctx.send("Entry submitted.")
        
        
        
def setup(bot):
    bot.add_cog(misc(bot))