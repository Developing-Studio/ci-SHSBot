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
from collections import OrderedDict, deque, Counter
from .utils import time, formats
OWNER_ID = 267410788996743168

def tick(label=None):
    lookup = {
        True: '<:greenTick:788836089996509215>',
        False: '<:redTick:788836103305297980>',
        None: '<:greyTick:788836277986394192>',
    }
    emoji = lookup.get(label, '<:redTick:788836103305297980>')
    if label is not None:
        return f'{emoji}'
    return emoji

class misc(commands.Cog):
    """
    Misc commands. These dont really fall under any other category.
    """
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def sha256(self, ctx, *, text):
        """
        Encodes a message in sha256.
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

        m = await ctx.send(embed=e)
        await self.bot.add_trash_can(m, 60)
        
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
        if data is None: return await ctx.send("There is no Pittdar entries.")
        e = discord.Embed(title=f"Pittdar Entry #{data[0]}",description=data[1],color=discord.Color.random())
        try:
            await ctx.reply(embed=e)
            return
        except:
            await ctx.send(embed=e)
            return
        
    @pittdar.command(aliases=["set"],description="Makes a new entry in the Pittdar database. Avaliable to only Pitt himself (and the developer).")
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
        
    @commands.command()
    async def avatar(self, ctx, *, user: discord.Member = None):
        """Shows an user's enlarged avatar (if possible)."""
        embed = discord.Embed(color=discord.Color.random())
        user = user or ctx.author
        avatar = user.avatar_url_as(static_format='png')
        embed.set_author(name=str(user), url=avatar)
        embed.set_image(url=avatar)
        await ctx.send(embed=embed)
        
    @commands.command(aliases=['guildinfo'], usage='')
    @commands.guild_only()
    async def serverinfo(self, ctx, *, guild_id: int = None):
        """Shows the guild/servers information."""
        if guild_id is not None and await self.bot.is_owner(ctx.author):
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                return await ctx.send(f'Invalid Guild ID given.')
        else:
            guild = ctx.guild

        roles = [role.name.replace('@', '@\u200b') for role in guild.roles]

        if not guild.chunked:
            async with ctx.typing():
                await guild.chunk(cache=True)

        # figure out what channels are 'secret'
        everyone = guild.default_role
        everyone_perms = everyone.permissions.value
        secret = Counter()
        totals = Counter()
        for channel in guild.channels:
            allow, deny = channel.overwrites_for(everyone).pair()
            perms = discord.Permissions((everyone_perms & ~deny.value) | allow.value)
            channel_type = type(channel)
            totals[channel_type] += 1
            if not perms.read_messages:
                secret[channel_type] += 1
            elif isinstance(channel, discord.VoiceChannel) and (not perms.connect or not perms.speak):
                secret[channel_type] += 1

        e = discord.Embed(color=discord.Color.random())
        e.title = guild.name
        e.description = f'**ID**: {guild.id}\n**Owner**: {guild.owner}'
        if guild.icon:
            e.set_thumbnail(url=guild.icon_url)

        channel_info = []
        key_to_emoji = {
            discord.TextChannel: '<:text_channel:788843534815461397>',
            discord.VoiceChannel: '<:voice_channel:788843570090082305>',
        }
        for key, total in totals.items():
            secrets = secret[key]
            try:
                emoji = key_to_emoji[key]
            except KeyError:
                continue

            if secrets:
                channel_info.append(f'{emoji} {total} ({secrets} locked)')
            else:
                channel_info.append(f'{emoji} {total}')

        info = []
        features = set(guild.features)
        all_features = {
            'PARTNERED': 'Partnered',
            'VERIFIED': 'Verified',
            'DISCOVERABLE': 'Server Discovery',
            'COMMUNITY': 'Community Server',
            'FEATURABLE': 'Featured',
            'WELCOME_SCREEN_ENABLED': 'Welcome Screen',
            'INVITE_SPLASH': 'Invite Splash',
            'VIP_REGIONS': 'VIP Voice Servers',
            'VANITY_URL': 'Vanity Invite',
            'COMMERCE': 'Commerce',
            'LURKABLE': 'Lurkable',
            'NEWS': 'News Channels',
            'ANIMATED_ICON': 'Animated Icon',
            'BANNER': 'Banner'
        }

        for feature, label in all_features.items():
            if feature in features:
                info.append(f'{tick(True)}: {label}')

        if info:
            e.add_field(name='Features', value='\n'.join(info))

        e.add_field(name='Channels', value='\n'.join(channel_info))

        if guild.premium_tier != 0:
            boosts = f'Level {guild.premium_tier}\n{guild.premium_subscription_count} boosts'
            last_boost = max(guild.members, key=lambda m: m.premium_since or guild.created_at)
            if last_boost.premium_since is not None:
                boosts = f'{boosts}\nLast Boost: {last_boost} ({time.human_timedelta(last_boost.premium_since, accuracy=2)})'
            e.add_field(name='Boosts', value=boosts, inline=False)

        bots = sum(m.bot for m in guild.members)
        fmt = f'Total: {guild.member_count} ({formats.plural(bots):bot})'

        e.add_field(name='Members', value=fmt, inline=False)
        e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')

        emoji_stats = Counter()
        for emoji in guild.emojis:
            if emoji.animated:
                emoji_stats['animated'] += 1
                emoji_stats['animated_disabled'] += not emoji.available
            else:
                emoji_stats['regular'] += 1
                emoji_stats['disabled'] += not emoji.available

        fmt = f'Regular: {emoji_stats["regular"]}/{guild.emoji_limit}\n' \
              f'Animated: {emoji_stats["animated"]}/{guild.emoji_limit}\n' \

        if emoji_stats['disabled'] or emoji_stats['animated_disabled']:
            fmt = f'{fmt}Disabled: {emoji_stats["disabled"]} regular, {emoji_stats["animated_disabled"]} animated\n'

        fmt = f'{fmt}Total Emoji: {len(guild.emojis)}/{guild.emoji_limit*2}'
        e.add_field(name='Emoji', value=fmt, inline=False)
        e.set_footer(text='Created').timestamp = guild.created_at
        await ctx.send(embed=e)
        
        
        
def setup(bot):
    bot.add_cog(misc(bot))