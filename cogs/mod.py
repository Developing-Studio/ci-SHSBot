import discord
import platform
import time, re, sys
import traceback
import asyncio
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
OWNER_ID = 267410788996743168
CATEGORIES_TO_IGNORE = [None, 363080948721385474, 360169295558344704, 781410672779984937]
CHANNELS_TO_IGNORE = [700454038445097061]

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h":3600, "s":1, "m":60, "d":86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time


class mod(commands.Cog):
    """
    Moderator commands for Supreme Admins and Admins.
    """

    def __init__(self, bot):
        self.bot = bot
    
    @commands.has_role(362974017436647425)
    @commands.command()
    async def ban(self, ctx, usertoban: discord.Member, reason = None, daystodelete = 0):
        try:
            await ctx.guild.ban(usertoban, reason=reason, delete_message_days=daystodelete)
            await ctx.send(f"***THE BAN HAMMER HAS SPOKEN!! BEGONE, {(str(usertoban).upper())}!!!")
        except Exception as e:
            await ctx.send(f"I was unable to ban that user.\n`{e}`")
    
    @commands.has_role(362974017436647425)
    @commands.command()
    async def massban(self, ctx, userstoban: commands.Greedy[discord.Member], reason = None, daystodelete = 0):
        banned = 0
        notbanned = 0
        somefailed = False
        for m in userstoban:
            await asyncio.sleep(0.5) # ratelimit easer
            try:
                await ctx.guild.ban(m, reason=reason, delete_message_days=daystodelete)
                await ctx.send(f"***THE BAN HAMMER HAS SPOKEN!! BEGONE, {(str(m).upper())}!!!")
                banned += 1
            except Exception as e:
                await ctx.send(f"I was unable to ban one or more of those user(s).\n`{e}`")
                notbanned += 1
        if somefailed is False: await ctx.send(f"Massban success. Banned {banned} members.")
        else: await ctx.send(f"Massban partial success. Banned {banned} members, and failed to ban {notbanned} members.")
            
    @commands.has_role(362974017436647425)
    @commands.command()
    async def kick(self, ctx, usertokick: discord.Member, reason = None, daystodelete = 0):
        try:
            await ctx.guild.kick(usertokick, reason=reason, delete_message_days=daystodelete)
            await ctx.send(f"\U0001f44c")
        except Exception as e:
            await ctx.send(f"I was unable to kick that user.\n`{e}`")
            
    @commands.has_any_role(362974017436647425, 327501122308800513)
    @commands.command()
    async def masskick(self, ctx, userstokick: commands.Greedy[discord.Member], reason = None, daystodelete = 0):
        kicked = 0
        notkicked = 0
        somefailed = False
        for m in userstokick:
            await asyncio.sleep(0.5) # ratelimit easer
            try:
                await ctx.guild.ban(m, reason=reason, delete_message_days=daystodelete)
                await ctx.send(f"Kicked {(str(m).upper())}!")
                kicked += 1
            except Exception as e:
                await ctx.send(f"I was unable to ban one or more of those user(s).\n`{e}`")
                notkicked += 1
        if somefailed is False: await ctx.send(f"Massban success. Banned {kicked} members.")
        else: await ctx.send(f"Massban partial success. Banned {kicked} members, and failed to ban {notkicked} members.")
            
    @commands.command()
    @commands.has_any_role(362974017436647425, 327501122308800513)
    async def mute(self, ctx, member:discord.Member, *, time:TimeConverter = None):
        """Mutes a member for the specified time- time in 2d 10h 3m 2s format ex:
        ?mute @Someone 1d"""
        role = discord.utils.get(ctx.guild.roles, name="Jailed")
        await member.add_roles(role)
        await ctx.send(("Muted {} for {}s" if time else "Muted {}").format(member, time))
        if time:
            await asyncio.sleep(time)
            await member.remove_roles(role)

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            pass
        if isinstance(error, commands.BadArgument):
            await ctx.send(error)
        else:
            error = getattr(error, 'original', error)
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    
    @commands.has_role(758408309383757894)
    @commands.command(aliases=["l","lc"])
    async def lock(self, ctx, chnnel: discord.TextChannel = None):
        try:
            everyone = ctx.guild.default_role
            if chnnel is None:
                if ctx.channel.overwrites_for(everyone).send_messages in [None,True]:
                    currentperms = ctx.channel.overwrites_for(everyone)
                    currentperms.send_messages = False
                    await ctx.channel.set_permissions(everyone, overwrite=currentperms,reason=(f"Channel lock by {str(ctx.author)}"))
                    await ctx.channel.send(f"🔒 `#{ctx.channel.name} was locked`")
                    return
                elif ctx.channel.overwrites_for(everyone).send_messages in [False]:
                    newperms = ctx.channel.overwrites_for(everyone)
                    newperms.send_messages = None
                    await ctx.channel.set_permissions(everyone, overwrite=newperms,reason=(f"Channel lock by {str(ctx.author)}"))
                    await ctx.channel.send(f"🔒 `#{ctx.channel.name} was unlocked`")
                    return
            else:
                if chnnel.overwrites_for(everyone).send_messages in [None,True]:
                    currentperms = chnnel.overwrites_for(everyone)
                    currentperms.send_messages = False
                    await chnnel.set_permissions(everyone, overwrite=currentperms,reason=(f"Channel unlock by {str(ctx.author)}"))
                    await chnnel.send(f"🔓 `#{chnnel.name} was unlocked`")
                    return
                elif chnnel.overwrites_for(everyone).send_messages in [False]:
                    newperms = chnnel.overwrites_for(everyone)
                    newperms.send_messages = None
                    await chnnel.set_permissions(everyone, overwrite=newperms,reason=(f"Channel unlock by {str(ctx.author)}"))
                    await chnnel.send(f"🔓 `#{chnnel.name} was unlocked`")
                    return
        except Exception as e:
            await ctx.send(f"`Something went wrong: {e}`")

    @commands.command(aliases=["sl"])
    @commands.has_permissions(manage_guild=True)
    async def serverlock(self, ctx):
        try:
            everyone = ctx.guild.default_role
            await ctx.send("`Locking... Do note, it locks at an interval of 1 channel/0.5s`")
            currentperms = ctx.channel.overwrites_for(everyone)
            for c in ctx.guild.channels:
                if c.category_id in CATEGORIES_TO_IGNORE:
                    pass
                elif c.overwrites_for(everyone).send_messages in [False]:
                    pass
                else:
                    currentperms.send_messages = False
                    await c.set_permissions(overwrite=currentperms,reason=f"Server lock by {str(ctx.author)}")
                    await asyncio.sleep(0.5)
        except Exception as e:
            await ctx.send(f"`Something went wrong:` ```\n{e}\n```")
            
    @commands.command(aliases=["sul"])
    @commands.has_permissions(manage_guild=True)
    async def serverunlock(self, ctx):
        try:
            everyone = ctx.guild.default_role
            await ctx.send("`Locking... Do note, it locks at an interval of 1 channel/0.5s`")
            currentperms = ctx.channel.overwrites_for(everyone)
            for c in ctx.guild.channels:
                if c.category_id in CATEGORIES_TO_IGNORE or c.id in CHANNELS_TO_IGNORE:
                    pass
                elif c.overwrites_for(everyone).send_messages in [None,True]:
                    pass
                else:
                    currentperms.send_messages = None
                    await c.set_permissions(overwrite=currentperms,reason=f"Server lock by {str(ctx.author)}")
                    await asyncio.sleep(0.5)
        except Exception as e:
            await ctx.send(f"`Something went wrong:` ```\n{e}\n```")
    
    @commands.command()
    async def cleanup(self, ctx, user: discord.Member = None, amount = 10):
        """
        Cleans up an users messages (or my own messages, if no user is specified.)
        """
        if user is None:
            user = self.bot.user
        def is_user(m):
            return m.author == user
        if amount > 100:
            await ctx.send("Thats too many messages to purge.")

        deleted = await ctx.channel.purge(limit=amount, check=is_user)
        await ctx.channel.send(f"Deleted {len(deleted)} messages from {str(user)}")
            
def setup(bot):
    bot.add_cog(mod(bot))