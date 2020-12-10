import discord
import platform
import time, re, sys
import traceback
import asyncio
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import CheckFailure, check
OWNER_ID = 267410788996743168
FRESHMAN_ROLE = 456231985279664169
SOPHOMORE_ROLE = 327494386621612032
JUNIOR_ROLE = 327494386625675276
SENIOR_ROLE = 327494393063931904
ALUMNI_ROLE = 327494394527744001
TEACHER_ROLE = 355475682517843969
BAND_ROLE = 327623947434590211
CHORUS_ROLE = 327630206195990539
FRENCH_ROLE = 327627308838158337
SPANISH_ROLE = 327627345135665162
LATIN_ROLE = 327627378207621120
SUPPORT_ROLE = 360175025762074624
CLAW_ROLE = 755808735263457370
DEBATE_ROLE = 695091939111862313
VISITOR_ROLE = 756261157198889080
CC_ROLE = 756582278435700776
TEN_Y_ROLE = 328205870825734154
TEN_Z_ROLE = 328205870825734154
TEN_M_ROLE = 481134577675403285
NINE_A_ROLE = 328205866513858560
NINE_B_ROLE = 328205867797446678
NINE_M_ROLE = 481134651310735370
#probably temporary
IN_PERSON_ROLE = 750761174223814737
ONLINE_ROLE = 750760516212883579



class welcome(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 327493540429037568:
            new_member_role = member.guild.get_role(717238978423554099)
            await member.add_roles(new_member_role, reason="New member join")
            
            welcome_channel = await self.bot.fetch_channel(385053314892693505)
            await welcome_channel.send(f"{member.mention} **Welcome to the SHS Discord! Please ping an admin with the following information:**\n- Your grade (if applicable)\n- Your team (eg. 9a, 10z)(if applicable)\n- Are you online or remote?\n- Are you community council?\n- Would you like a support role that gives access to support channels e.g. #math-help?\n- Are you in band/chorus?\n- Do you take a language? If so, which?")
     
     
    #Reaction Roles
      
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.guild_id == 327493540429037568:
            
            # Grade & Faculty
            if payload.message_id == 784213970193743883:
                if payload.emoji == "\U0001f7eb":
                    member = self.bot.get_guild(payload.guild_id).get_member(payload.member_id)
                
        

def setup(bot):
    bot.add_cog(welcome(bot))