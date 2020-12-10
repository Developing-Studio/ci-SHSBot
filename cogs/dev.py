import discord
import platform
import time
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
import asyncio
import aiosqlite
from datetime import datetime
OWNER_ID = 267410788996743168

class dev(commands.Cog):
    """
    Dev commands. thats really it
    """
    def __init__(self,bot):
        self.bot = bot
    
    async def cog_check(self,ctx):
        return ctx.author.id == OWNER_ID
    
    @commands.group(invoke_without_command=True,hidden=True,name="dev")
    async def developer(self, ctx):
        #bot dev commands
        await ctx.send("`You're missing one of the below arguements:` ```md\n- reload\n- loadall\n- status <reason>\n- ban <user> <reason>\n```")

    @developer.command(aliases=["r","reloadall"])
    async def reload(self, ctx):
        output = ""
        amount_reloaded = 0
        async with ctx.channel.typing():
            for e in self.bot.initial_extensions:
                try:
                    self.bot.reload_extension(e)
                    amount_reloaded += 1
                except Exception as e:
                    e = str(e)
                    output = output + e + "\n"
            await asyncio.sleep(1)
            if output == "":
                await ctx.send(content=f"`{len(self.bot.initial_extensions)} cogs succesfully reloaded.`") # no output = no error
            else:
                await ctx.send(content=f"`{amount_reloaded} cogs were reloaded, except:` ```\n{output}```") # output

    @developer.command(aliases=["load","l"])
    async def loadall(self, ctx):
        output = ""
        amount_loaded = 0
        async with ctx.channel.typing():
            for e in self.bot.initial_extensions:
                try:
                    self.bot.load_extension(e)
                    amount_loaded += 1
                except Exception as e:
                    e = str(e)
                    output = output + e + "\n"
            await asyncio.sleep(1)
            if output == "":
                await ctx.send(content=f"`{len(self.bot.initial_extensions)} cogs succesfully loaded.`") # no output = no error
            else:
                await ctx.send(content=f"`{amount_loaded} cogs were loaded, except:` ```\n{output}```") # output

    @developer.command()
    async def nick(self,ctx,*,nick):
        try:
            await ctx.guild.me.edit(nick=nick)
        except:
            await ctx.send("It seems i dont have permissions for that.")

    @developer.command()
    async def status(self, ctx, *, text):
        # Setting `Playing ` status
        if text is None:
            await ctx.send(f"{ctx.guild.me.status}")
        if len(text) > 60:
            await ctx.send("`Too long you pepega`")
            return
        try:
            await self.bot.change_presence(activity=discord.Game(name=text))
            await ctx.message.add_reaction("\U00002705")
        except Exception as e:
            await ctx.message.add_reaction("\U0000274c")
            await ctx.send(f"`{e}`")

    @developer.command()
    async def stop(self, ctx):
        askmessage = await ctx.send("`you sure?`")
        def check(m):
            newcontent = m.content.lower()
            return newcontent == 'yea' and m.channel == ctx.channel
        try:
            await self.bot.wait_for('message', timeout=5, check=check)
        except asyncio.TimeoutError:
            await askmessage.edit(content="`Timed out. haha why didnt you respond you idiot`")
        else:
            await ctx.send("`bye`")
            print(f"Bot is being stopped by {ctx.message.author} ({ctx.message.id})")
            await self.bot.db.commit()
            await self.bot.db.close()
            await self.bot.logout()
        
    @developer.group(invoke_without_command=True)
    async def sql(self, ctx):
        await ctx.send("`Youre missing one of the below params:` ```md\n- fetchone\n- fetchall\n- run\n```") 
            
    @sql.command()
    async def fetchone(self, ctx, *, statement):
        try:
            c = await self.bot.db.execute(statement)
            data = await c.fetchone()
            await self.bot.db.commit()
            await ctx.send(data)
        except Exception as e:
            await ctx.send(f"```sql\n{e}\n```")
            
    @sql.command()
    async def fetchall(self, ctx, *, statement):
        try:
            c = await self.bot.db.execute(statement)
            data = await c.fetchall()
            await self.bot.db.commit()
            await ctx.send(data)
        except Exception as e:
            await ctx.send(f"```sql\n{e}\n```")
    @sql.command()
    async def run(self, ctx, *, statement):
        try:
            c = await self.bot.db.execute(statement)
            await self.bot.db.commit()
            await ctx.message.add_reaction(emoji="\U00002705")
        except Exception as e:
            await ctx.send(f"```sql\n{e}\n```")
        
    @developer.command(aliases=["bu"])
    async def backup(self, ctx):
        try:
            await self.bot.db.commit()
            self.bot.backup_db = await aiosqlite.connect('ecox_backup.db')
            await self.bot.db.backup(self.bot.backup_db)
            await self.bot.backup_db.commit()
            await self.bot.backup_db.close()
            await ctx.send("The database was backed up successfully.")
            return
        except Exception as e:
            await ctx.send(f"An error occured while backing up the database:\n`{e}`")
            return
    
    @commands.command()
    async def react(self, ctx, m_id: int, emoji: str = None):
        msg = await ctx.channel.fetch_message(m_id)
        try:
            await msg.add_reaction(emoji)
            await ctx.message.add_reaction('✅')
        except Exception as e:
            await ctx.send(str(e))
        
def setup(bot):
    bot.add_cog(dev(bot))