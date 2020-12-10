import discord
import platform
import time
import asyncio
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
OWNER_ID = 267410788996743168

class todo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    @commands.group(invoke_without_command=True,name="todo")
    async def to_do(self, ctx):
        pass
    
    @to_do.command(name="list") # thank GOD for the list kwarg
    async def li_st(self, ctx, member: discord.Member = None):
        