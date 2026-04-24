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
    @app_commands.describe(channel_type="Choose the type of channel to set (Kills/Results/Roster)", channel="Select the actual channel")
    
    @app_commands.choices(channel_type=[
        app_commands.Choice(name="Kills", value="KILLS"),
        app_commands.Choice(name="Results", value="RESULTS"),
        app_commands.Choice(name="Roster", value="ROSTER")
    ])
    # Logic to set the channels based on the type and name provided by the user.
    async def setchannels(self, interaction: discord.Interaction, channel_type: app_commands.Choice[str], channel: discord.TextChannel):
        file_path = 'storage/channels.json'
        os.makedirs('storage', exist_ok=True)

        data = {
            "KILLS": None,
            "RESULTS": None,
            "ROSTER": None
        }

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f) # Load the old saves into 'data'
                except json.JSONDecodeError:
                    pass # If the file is corrupted or empty, just ignore and use the blank slate

        data[channel_type.value] = channel.id
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

        await interaction.response.send_message(f'Success! Set **{channel_type.value}** to {channel.mention}.', ephemeral=True)

# Send to main.py to add this cog to the bot.
async def setup(bot):
    await bot.add_cog(ChannelManager(bot))