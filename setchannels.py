# Usage: /setchannels (KILLS or RESULTS or ROSTER) (channelname)
# Purpose: This command is for setting the channels for the bot to post in.
# The bot will only post in the channels that are set using this command. It will NOT post anything inside those channels.
# Store these channels in json or something so that we can access them later when we want to post updates.

# Essential:
import discord, os, json
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv 
from permission import has_permission

load_dotenv()
GUILD_ID=int(os.getenv('GUILD_ID'))

# ChannelManager class is a cog that will handle the channel management commands and listeners.
class ChannelManager(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    # Listener to print when the cog is ready.
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'ChannelManager cog is ready!')
    
    # Begin command logic, limit it to Admin+, tie it to the guild.
    @app_commands.command(name="setchannels", description="Set the channels for the bot to post in!")
    @has_permission(3)
    @app_commands.guilds(discord.Object(id=GUILD_ID)) # Limit the command to a specific guild
    @app_commands.describe(channel_type="Choose the type of channel to set (Kills/Results/Roster)", channel="Select the actual channel")
    
    @app_commands.choices(channel_type=[
        app_commands.Choice(name="Kills", value="KILLS"),
        app_commands.Choice(name="Results", value="RESULTS"),
        app_commands.Choice(name="Roster", value="ROSTER")
    ])

    # Logic to set the channels based on the type and name provided by the user.
    async def setchannels(self, interaction: discord.Interaction, channel_type: app_commands.Choice[str], channel: discord.TextChannel):
        guild_id = str(interaction.guild_id)
        file_path = 'storage/channels.json'
        os.makedirs('storage', exist_ok=True)

        data = {}
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try: data = json.load(f)
                except: pass

        # Ensure THIS server has a spot in the file
        if guild_id not in data:
            data[guild_id] = {"KILLS": None, "RESULTS": None, "ROSTER": None}

        # Update specific channel for this server
        data[guild_id][channel_type.value] = channel.id

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

        await interaction.response.send_message(f'Success! Set **{channel_type.value}** to {channel.mention}.', ephemeral=True)
        
# Send to main.py to add this cog to the bot.
async def setup(bot):
    await bot.add_cog(ChannelManager(bot))