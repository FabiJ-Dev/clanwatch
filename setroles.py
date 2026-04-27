# Usage: /setroles (level) (role)
# Purpose: Set the roles and levels that we will need for the bot. 
# Level 1 - Member; Level 2 - Officer; Level 3 - Admin; Level 4 - OPs

# Essential:
import discord, os, json
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from permission import has_permission

# Load the guild ID and token
load_dotenv()
GUILD_ID = int(os.getenv('GUILD_ID'))

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("RoleManager cog is ready!")

    # Command code starts here, requires level 4 (OP) to change the order of roles.
    @app_commands.command(name="setroles", description="Set the roles for each permission level.")
    @has_permission(4) 
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(level="Level 1: Member, Level 2: Officer, Level 3: Admin, Level 4: Owner", role="The Discord role to associate with this level")
    @app_commands.choices(level=[
        app_commands.Choice(name="Level 1 (Member)", value=1),
        app_commands.Choice(name="Level 2 (Officer)", value=2),
        app_commands.Choice(name="Level 3 (Admin)", value=3),
        app_commands.Choice(name="Level 4 (Owner)", value=4)
    ])

    # When command is sent, go here to write the role IDs into storage/roles.json, and apply changes.
    async def setroles(self, interaction: discord.Interaction, level: app_commands.Choice[int], role: discord.Role):
        # Save the Guild ID so we don't overwrite someone else's role permissions. 
        guild_id = str(interaction.guild_id)
        file_path = 'storage/roles.json'
        
        # Initialize data, but if it exists, grab that. 
        data = {}
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                try: data = json.load(file)
                except: pass

        # Ensure this server has a role mapping to make the json organized.
        if guild_id not in data:
            data[guild_id] = {"1": None, "2": None, "3": None, "4": None}

        # Update the level for this specific server
        data[guild_id][str(level.value)] = role.id
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

        # Success message - reach here means the operation was a success
        await interaction.response.send_message(f"Level {level.value} set to {role.mention}", ephemeral=True)

# Add the cog back into main.py so it can be used. 
async def setup(bot):
    await bot.add_cog(RoleManager(bot))