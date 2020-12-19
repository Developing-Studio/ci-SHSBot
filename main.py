import discord
from discord.ext import commands
import aiosqlite
import sys, os
import traceback
import asyncio
import time
import random
from datetime import datetime
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 
os.environ["JISHAKU_HIDE"] = "True"

desc = "SHSBot is a bot made by averwhy#3899 for the Souhegan Discord."

class SHSBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    async def get_tag(self,guild,name):
        name = name.lower()
        cur = await bot.db.execute("SELECT pointsto FROM aliases WHERE name = ? AND guildid = ?",(name, guild.id))
        data = await cur.fetchone()
        if data is not None: # this checks for aliases. if its not none, its an alias
            name = data[0]
        cur = await bot.db.execute("SELECT content FROM tags WHERE name = ? AND guildid = ?",(name, guild.id))
        data = await cur.fetchone()
        if data is None:
            return f"Tag '{name}' not found."
        else:
            await bot.db.execute("UPDATE tags SET uses = (uses + 1) WHERE guildid = ? AND name = ?",(guild.id, name))
            return data[0]
        
    async def create_tag(self, name, content, user):
        cur = await bot.db.execute("SELECT content FROM tags WHERE name = ? AND guildid = ?",(name, user.guild.id))
        data = await cur.fetchone()
        if data is not None:
            return f"A tag already exists with that name."
        else:
            now = datetime.utcnow()
            tagid = bot.tag_counter + 1
            bot.tag_counter += 1
            await bot.db.execute("INSERT INTO tags VALUES (?, ?, ?, ?, ?, 0, ?)",(user.guild.id, name, content, tagid, user.id, now,))
            await bot.db.commit()
            return f"Tag '{name}' created successfully."
        
    async def create_alias(self, name, pointsto, user):
        cur = await bot.db.execute("SELECT name FROM aliases WHERE name = ? AND guildid = ?",(name, user.guild.id))
        data = await cur.fetchone()
        if data is not None:
            return f"A alias already exists with that name."
        cur = await bot.db.execute("SELECT * FROM tags WHERE name = ? AND guildid = ?",(pointsto, user.guild.id))
        data = await cur.fetchone()
        if data is None:
            return f"A tag does not exist with that name."
        else:
            now = datetime.utcnow()
            await bot.db.execute("INSERT INTO aliases VALUES (?, ?, ?, ?, 0, ?)",(user.guild.id, name, pointsto, user.id, now,))
            await bot.db.commit()
            return f"Alias '{name}' that points to '{pointsto}' created successfully."
        
    async def get_user_tags(self, user):
        cur = await bot.db.execute("SELECT name, id FROM tags WHERE ownerid = ?",(user.id,))
        data = await cur.fetchall()
        return data
    
    async def transfer_tag(self, recieving_user, sending_user, name):
        cur = await bot.db.execute("SELECT * FROM tags WHERE ownerid = ?",(sending_user.id,))
        data = await cur.fetchone()
        print(data)
        if data is None:
            return "That tag doesnt exist."
        if int(data[4]) != sending_user.id:
            return "You don't own that tag."
        
        await bot.db.execute("UPDATE tags SET ownerid = ? WHERE name = ?",(recieving_user.id, name,))
        await bot.db.commit()
        return (f"Tag ownership of {name} successfully transferred to {str(recieving_user)}.")
        
    async def add_trash_can(self, message, timeout = 60):
        await message.add_reaction('🗑️')
        def check(reaction, user):
            return user == message.author and str(reaction.emoji) == '🗑️'
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=timeout, check=check)
        except asyncio.TimeoutError:
            pass
        else:
            await message.delete()
        
    
            
bot = SHSBot(command_prefix=commands.when_mentioned_or("?"),description=desc,intents=discord.Intents(reactions = True, messages = True, guilds = True, members = True), max_messages = 100000)

bot.initial_extensions = ["jishaku","cogs.tags","cogs.mod","cogs.misc","cogs.meta","cogs.dev","cogs.welcome","cogs.stats"]
with open("TOKEN.txt",'r') as t:
    TOKEN = t.readline()
bot.time_started = time.localtime()
bot.version = '0.0.1'
bot.total_command_errors = 0
bot.total_command_completetions = 0
bot.launch_time = datetime.utcnow()

async def startup():
    await bot.wait_until_ready()
    bot.db = await aiosqlite.connect('shsbot.db')
    await bot.db.execute("CREATE TABLE IF NOT EXISTS tags (guildid int, name text, content text, id int, ownerid int, uses int, created text)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS aliases (guildid int, name text, pointsto text, ownerid int, uses int, created text)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS pittdar (entry int, content text)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS todo (userid int, content text, todoid int)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS starboard (userid int, stars int, starred int, starred_msgs int)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS stars (msgid int, stars int)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS starconfig (guildid int, channelid int, staramount int)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS commandstats (commandname text, uses int)")
    print("Database connected")
    
    bot.backup_db = await aiosqlite.connect('shsbot_backup.db')
    print("Backup database is ready")
    await bot.backup_db.close()
    
    c = await bot.db.execute("SELECT id FROM tags ORDER BY id DESC")
    n = await c.fetchone()
    if n is None: n = [0]
    bot.tag_counter = int(n[0])
    
bot.loop.create_task(startup())

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('---------------------------------')
    
@bot.event
async def on_command(command):
    await bot.db.commit() # just cuz
    
@bot.event
async def on_command_error(ctx, error): # this is an event that runs when there is an error
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.message.add_reaction("\U00002753") # red question mark
    elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown): 
        s = round(error.retry_after,2)
        if s > 3600: # over 1 hour
            s /= 3600
            s = round(s,1)
            s = f"{s} hour(s)"
        elif s > 60: # over 1 minute
            s /= 60
            s = round(s,2)
            s = f"{s} minute(s)"
        else: #below 1 min
            s = f"{s} seconds"
        msgtodelete = await ctx.send(f"ERROR: Cooldown for {s}!")
        await asyncio.sleep(15)
        await msgtodelete.delete()
        return
    elif isinstance(error, commands.CheckFailure):
        # these will be handled in cogs
        return
    else:
        await ctx.send(f"```diff\n- An internal error occured while attempting to perform this command.\n```")
        # All other Errors not returned come here. And we can just print the default TraceBack.
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


for cog in bot.initial_extensions:
    try:
        bot.load_extension(f"{cog}")
        print(f"loaded {cog}")
    except Exception as e:
        print(f"Failed to load {cog}, error:\n", file=sys.stderr)
        traceback.print_exc()
asyncio.set_event_loop(asyncio.SelectorEventLoop())
bot.run(TOKEN, bot = True, reconnect = True)