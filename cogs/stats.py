import discord
import platform
import time
import asyncio
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
OWNER_ID = 267410788996743168

class stats(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_command(self, ctx):
        cur = await self.bot.db.execute("SELECT name FROM commandstats WHERE commandname = ?",(ctx.command.name,))
        data = await cur.fetchone()
        if data is None:
            await self.bot.db.execute("INSERT INTO commandstats VALUES (?, 0)",(ctx.command.name,))
        await self.bot.db.execute("UPDATE commandstats SET uses = (uses + 1) WHERE commandname = ?",(ctx.command.name,))
        await self.bot.db.commit()
        
    @commands.command(name="stats")
    async def _stats(self, ctx, command = None):
        if command is not None:
            return
        
        cur = await self.bot.db.execute("SELECT * FROM commandstats ORDER BY uses DESC")
        data = await cur.fetchmany(3)
        embed = discord.Embed(title="Command stats for SHS Discord",color=discord.Color.random())
        for c in data:
            embed.add_field(name=c[0],value=f"{c[1]} uses")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)
        
        
def setup(bot):
    bot.add_cog(stats(bot))