import discord
import platform
import time
import asyncio
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
OWNER_ID = 267410788996743168

class tags(commands.Cog):
    """
    Tag related commands.
    """
    def __init__(self,bot):
        self.bot = bot
    
    @commands.cooldown(1,1,BucketType.user)
    @commands.group(aliases=["p"],invoke_without_command=True)
    async def tag(self, ctx, *, name: str = None):
        """
        Allows you to tag something for later retrieval.
        """
        m = await self.bot.get_tag(ctx.guild, name)
        await ctx.send(m)
        
    @commands.cooldown(1,3,BucketType.user)  
    @tag.command(aliases=['add'])
    async def create(self, ctx, name, *, content):
        """
        Creates a new tag owned by you.
        Server moderators can delete your tag.
        """

        m = await self.bot.create_tag(name, content, ctx.author)
        await ctx.send(m)
        
    @tag.command()
    async def alias(self, ctx, aliasname, tagname):
        """
        Creates an alias for an existing tag.
        """
        m = await self.bot.create_alias(aliasname, tagname, ctx.author)
        await ctx.send(m)
    
    @tag.command()
    async def transfer(self, ctx, user: discord.Member, tagname):
        """
        Transfers ownership of a tag to someone else. Note that only tag owners can transfer ownership to others.
        """
        m = await self.bot.transfer_tag(user, ctx.author, tagname)
        await ctx.send(m)
        
    @commands.cooldown(1,3,BucketType.user)
    @commands.command()
    async def tags(self, ctx, user: discord.Member = None):
        """
        Allows you to see your tags, or someone elses.
        """
        if user is None:
            user = ctx.author
        usertags = await self.bot.get_user_tags(user)
        if usertags is None:
            await ctx.send("You have no tags.")
            return
        embed = discord.Embed(title=f"{str(user)}'s tags",color=discord.Color.teal_blue())
        step = 1
        cntent = ""
        for t in usertags:
            if step > 10:
                break
            cntent = cntent + (f"{step}. {t[0]} (ID:{t[1]})") + "\n"
            step += 1
        embed.add_field(name=f"{(step-1)}/{len(usertags)} tags on this page",value=cntent)
        await ctx.send(embed=embed)
        
        
def setup(bot):
    bot.add_cog(tags(bot))