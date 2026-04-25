import discord
from discord.ext import commands
from discord import app_commands
import os # For loading environment variables
from dotenv import load_dotenv # get the .env file and load the environment variables
import json # For storing channel information in a file

load_dotenv() # load the token
GUILD_ID=int(os.getenv('GUILD_ID')) # get the guild ID from the environment variable and convert it to an integer

class PrintChannels(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    # Listener to print when the cog is ready.
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'PrintChannels cog is ready!')
    
    # Command to set our channels.
    @app_commands.command(name="printchannels", description="Print the BLANK templates for the channels.")
    @app_commands.guilds(discord.Object(id=GUILD_ID)) # Limit the command to a specific guild
    async def printchannels(self, interaction: discord.Interaction):
        # os.path.join will extract files from the directory of the bot.
        channels_file = "storage/channels.json"
        if not os.path.exists(channels_file):
            await interaction.response.send_message("Not found.")
            return
    
        with open(channels_file, "r") as file:
            try:
                channels_data = json.load(file)
            except json.JSONDecodeError:
                channels_data={}

        clans_file = "storage/clansinfo.json"
        if not os.path.exists(clans_file):
            await interaction.response.send_message("Not found")
            return
        
        with open (clans_file, "r") as file:
            try:
                clan_data = json.load(file)
            except json.JSONDecodeError:
                clan_data = {}

        # Obtain clan info
        clanName = clan_data.get("CLAN_NAME")
        clanTag = clan_data.get("CLAN_TAG")
        clanDesc = clan_data.get("CLAN_DESCRIPTION")

        # CREATE new files 
        clan_storageFiles = ["storage/roster.json", "storage/kills.json", "storage/results.json"]
        for new in clan_storageFiles:
                    if not os.path.exists(new):
                        with open(new, 'w') as f:
                            json.dump({}, f, indent=4) 

        async def fetch_ch(cid):
            if not cid: return None
            channels = self.bot.get_channel(int(cid))
            if not channels:
                try:
                    channels = await self.bot.fetch_channel(int(cid))
                except:
                    return None
            return channels
        
        # Roster Template
        roster_ch = await fetch_ch(channels_data.get("ROSTER"))
        if roster_ch:
            roster_msg = f"# 🛡️ {clanName} [{clanTag}] Roster\n*{clanDesc}*\n\n> *The roster is currently empty. Use `/roster add` to add members!*"
            await roster_ch.send(roster_msg)

        # Kills Template
        kills_ch = await fetch_ch(channels_data.get("KILLS"))
        if kills_ch:
            kills_msg = f"# ⚔️ {clanName} Top Kills\n\n> *No kills logged yet. Use `/kills add` to update the leaderboard!*"
            await kills_ch.send(kills_msg)

        # Results Template
        results_ch = await fetch_ch(channels_data.get("RESULTS"))
        if results_ch:
            results_msg = f"# 🏆 {clanName} VS History\n\n> *No matches recorded. Use `/vs add` to log a match!*"
            await results_ch.send(results_msg)

        await interaction.response.send_message(f'Success.')

async def setup(bot):
    await bot.add_cog(PrintChannels(bot))

