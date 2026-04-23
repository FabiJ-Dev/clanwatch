# usage: /setchannels (KILLS or RESULTS or ROSTER) (channelname)
# This file is for setting the channels for the bot to post in.
# The bot will only post in the channels that are set using this command. It will NOT post anything inside those channels.
# Store these channels in json or something so that we can access them later when we want to post updates.

import discord
from discord.ext import commands
from discord import app_commands
import os # For loading environment variables
from dotenv import load_dotenv # get the .env file and load the environment variables
import json # For storing channel information in a file

load_dotenv() # load the token
GUILD_ID=int(os.getenv('GUILD_ID')) # get the guild ID from the environment variable and convert it to an integer

# ChannelManager class is a cog that will handle the channel management commands and listeners.
class ChannelManager(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    # Listener to print when the cog is ready.
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'ChannelManager cog is ready!')
    
    # Command to set our channels.
    @app_commands.command(name="setchannels", description="Set the channels for the bot to post in!")
    @app_commands.guilds(discord.Object(id=GUILD_ID)) # Limit the command to a specific guild
    @app_commands.describe(channel_type="Choose the type of channel to set (Kills/Results/Roster)", channel_name="The name of the channel to set")
    @app_commands.choices(channel_type=[
        app_commands.Choice(name="Kills", value="KILLS"),
        app_commands.Choice(name="Results", value="RESULTS"),
        app_commands.Choice(name="Roster", value="ROSTER")
    ])
    # Logic to set the channels based on the type and name provided by the user.
    async def setchannels(self, interaction: discord.Interaction, channel_type: app_commands.Choice[str], channel_name: str):
        await interaction.response.send_message(f'Set {channel_type.value} channel to {channel_name}!', ephemeral=True) 
        json_data = {
            "KILLS": channel_name if channel_type.value == "KILLS" else None,
            "RESULTS": channel_name if channel_type.value == "RESULTS" else None,
            "ROSTER": channel_name if channel_type.value == "ROSTER" else None
        }
        # File is in storage/channels.json. If the file doesn't exist, it will be created. If it does exist, it will be overwritten with the new channel information.
        with open('storage/channels.json', 'w') as f:
            json.dump(json_data, f, indent=4)

    # Get the channels that are stored.
    @app_commands.command(name="getchannels", description="Get the channels that are set for the bot to post in!")
    @app_commands.guilds(discord.Object(id=GUILD_ID)) # Limit the command
    async def getchannels(self, interaction: discord.Interaction):
        with open('storage/channels.json', 'r') as f:
            channels = json.load(f)
        await interaction.response.send_message(f'Current channels:\nKills: {channels["KILLS"]}\nResults: {channels["RESULTS"]}\nRoster: {channels["ROSTER"]}', ephemeral=True)

# Send to main.py to add this cog to the bot.
async def setup(bot):
    await bot.add_cog(ChannelManager(bot))

