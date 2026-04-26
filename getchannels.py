# Sole purpose: Print the channels that are already set from channels.json
# Usage: /getchannels (NO arguments)

import discord
from discord.ext import commands
from discord import app_commands
import os # For loading environment variables
from dotenv import load_dotenv # get the .env file and load the environment variables
import json # For storing channel information in a file
from permission import has_permission

load_dotenv() # load the token
GUILD_ID=int(os.getenv('GUILD_ID')) # get the guild ID from the environment variable and convert it to an integer

class GetChannels(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    # Listener to print when the cog is ready.
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'GetChannels cog is ready!')
    
# Command to get our channels.
    @app_commands.command(name="getchannels", description="Get the current channels listed from /setchannels.")
    @has_permission(2) # Give Officers (Level 2) and up access to see the config
    @app_commands.guilds(discord.Object(id=GUILD_ID)) 
    async def getchannels(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild_id)
        file_path = "storage/channels.json"

        if not os.path.exists(file_path):
            await interaction.response.send_message("No channels set yet.", ephemeral=True)
            return

        with open(file_path, "r") as file:
            data = json.load(file)

        server_data = data.get(guild_id)
        if not server_data:
            await interaction.response.send_message("No channels saved for this server.", ephemeral=True)
            return
        
        getchannels_msg = ["Your channels set are..."]
        for c_type, c_id in server_data.items():
            getchannels_msg.append(f"{c_type} -> <#{c_id}>" if c_id else f"{c_type}: Not set")
            
        await interaction.response.send_message("\n".join(getchannels_msg))
# Send to main.py to add this cog to the bot.
async def setup(bot):
    await bot.add_cog(GetChannels(bot))
