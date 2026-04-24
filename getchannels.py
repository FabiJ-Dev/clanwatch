# Sole purpose: Print the channels that are already set from channels.json
# Usage: /getchannels (NO arguments)

import discord
from discord.ext import commands
from discord import app_commands
import os # For loading environment variables
from dotenv import load_dotenv # get the .env file and load the environment variables
import json # For storing channel information in a file

load_dotenv() # load the token
GUILD_ID=int(os.getenv('GUILD_ID')) # get the guild ID from the environment variable and convert it to an integer

class GetChannels(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    # Listener to print when the cog is ready.
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'GetChannels cog is ready!')
    
    # Command to set our channels.
    @app_commands.command(name="getchannels", description="Get the current channels listed from /setchannels.")
    @app_commands.guilds(discord.Object(id=GUILD_ID)) # Limit the command to a specific guild
    async def getchannels(self, interaction: discord.Interaction):
        # os.path.join will extract files from the directory of the bot.
        file_path = os.path.join("storage/channels.json")

        # Error handling 
        if not os.path.exists(file_path): # If the file does NOT exist at all.
            await interaction.response.send_message("No channels have been set yet. (File not found)", ephemeral=True)
            return
        with open(file_path, "r") as file:
            try: # Open. If it doesn't open for some reason, use the except.
                channels_data = json.load(file)
            except json.JSONDecodeError:
                await interaction.response.send_message("There was an error reading the channels file.", ephemeral=True)
                return
        if not channels_data: # Use if the file loads successfully but there's nothing there.
            await interaction.response.send_message("No channels are currently saved.", ephemeral=True)
            return
        
        # We are building a LIST of STRINGS. Therefore, need the brackets around that point.
        getchannels_msg = ["Your channels set are..."]

        for channel_name, channel_id in channels_data.items():
            if channel_id:
                getchannels_msg.append(f"{channel_name} -> <#{channel_id}>")
            else:
                getchannels_msg.append(f"{channel_name}: No channel found!")
        full_getchannels = "\n".join(getchannels_msg)
        await interaction.response.send_message(full_getchannels)

# Send to main.py to add this cog to the bot.
async def setup(bot):
    await bot.add_cog(GetChannels(bot))
