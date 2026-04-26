#USAGE: /setroles (level) (role)

import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from dotenv import load_dotenv
from permission import has_permission

load_dotenv()
GUILD_ID = int(os.getenv('GUILD_ID'))

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("RoleManager cog is ready!")

    @app_commands.command(name="setroles", description="Set the roles for each permission level.")
    @has_permission(4) 
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(
        level="Level 1: Member, Level 2: Officer, Level 3: Admin, Level 4: Owner",
        role="The Discord role to associate with this level"
    )
    @app_commands.choices(level=[
        app_commands.Choice(name="Level 1 (Member)", value=1),
        app_commands.Choice(name="Level 2 (Officer)", value=2),
        app_commands.Choice(name="Level 3 (Admin)", value=3),
        app_commands.Choice(name="Level 4 (Owner)", value=4)
    ])
    async def setroles(self, interaction: discord.Interaction, level: app_commands.Choice[int], role: discord.Role):
        guild_id = str(interaction.guild_id)
        file_path = 'storage/roles.json'
        
        data = {}
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try: data = json.load(f)
                except: pass

        # Ensure this server has a role mapping
        if guild_id not in data:
            data[guild_id] = {"1": None, "2": None, "3": None, "4": None}

        # Update the level for this specific server
        data[guild_id][str(level.value)] = role.id

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

        await interaction.response.send_message(f"Level {level.value} set to {role.mention}", ephemeral=True)
async def setup(bot):
    await bot.add_cog(RoleManager(bot))