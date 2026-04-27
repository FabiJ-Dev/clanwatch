# Usage: /getchannels (NO arguments)
# Purpose: print the channels that are set from /setchannels 

# Essential:
import discord, os, json
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv 
from permission import has_permission

load_dotenv() 
GUILD_ID=int(os.getenv('GUILD_ID'))

class GetChannels(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'GetChannels cog is ready!')
    
# Command to get our channels that have been saved from channels.json (the file where it's stored)
    @app_commands.command(name="getchannels", description="Get the current channels listed from /setchannels.")
    @has_permission(2) # Running the commnand requires Level 2 - Officers or higher.
    @app_commands.guilds(discord.Object(id=GUILD_ID)) 
    async def getchannels(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild_id)
        channels_file = "storage/channels.json"

        # Could also write 'if os.path.exists(channels_file) == False', but we're writing it this way for readability. 
        if not os.path.exists(channels_file):
            await interaction.response.send_message("No system data exists, creating...", ephemeral=True)
            return
        with open(channels_file, "r") as file:
            data = json.load(file)

        server_data = data.get(guild_id)
        if not server_data:
            await interaction.response.send_message("No channels saved for this server, use `/setchannels` to save a channel to a category.", ephemeral=True)
            return
        
        lines = ["**Your channels are set as:**"]
        for channel_type, channel_id in server_data.items():
            if channel_id: # Print the channel ID and append if there is a channel existing for that category.
                lines.append(f"**{channel_type}** → <#{channel_id}>")
            else: # If NO channel is found (either it's deleted or was never set up in the first place)
                lines.append(f"**{channel_type}** → Not set")

        # Once the message is completely done (appended with the channel info), send it. 
        await interaction.response.send_message("\n".join(lines))

# Send to main.py to add this cog to the bot.
async def setup(bot):
    await bot.add_cog(GetChannels(bot))
