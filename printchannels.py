# Usage: /printchannels (no arguments)
# Purpose: print the blank templates for the roster, the kills leaderboard, and the results.

# Essential:
import discord, os, json
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv 
from permission import has_permission

load_dotenv() 
GUILD_ID=int(os.getenv('GUILD_ID')) 

class PrintChannels(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'PrintChannels cog is ready!')
    
    # Begin command logic, requires Level 3 (Admin) to print new messages.
    @app_commands.command(name="printchannels", description="Print the BLANK templates for the channels.")
    @has_permission(3)
    @app_commands.guilds(discord.Object(id=GUILD_ID)) 
    async def printchannels(self, interaction: discord.Interaction):
        # Defer will trigger the "ClanWatch is Thinking" since we get only 4 seconds to respond to commands, else it fails.
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)

        # Load and extract channel IDs that need a message to be printed into. 
        channels_file = "storage/channels.json"
        if not os.path.exists(channels_file): # First check - channels don't exist anymore (deleted?)
            await interaction.followup.send("Some or all channels were not found.", ephemeral=True)
            return
        with open(channels_file, "r") as file:
            try:
                all_channels = json.load(file)
            except json.JSONDecodeError:
                all_channels = {}
        
        server_channels = all_channels.get(guild_id)
        if not server_channels: # Second check - channels were never set at all.
            await interaction.followup.send("❌ Channels not set for this server. Use `/setchannels`.", ephemeral=True)
            return

        # Load the clan information.
        clans_file = "storage/clansinfo.json"
        if not os.path.exists(clans_file):
            await interaction.followup.send("No clan found. Use `/clan create`.")
            return
        
        with open (clans_file, "r") as file:
            try:
                all_clans = json.load(file)
            except json.JSONDecodeError:
                all_clans = {}

        server_clan = all_clans.get(guild_id)
        if not server_clan:
            await interaction.followup.send("❌ No clan registered for this server! Use `/clan create`.")
            return

        clanName = server_clan.get("CLAN_NAME", "Unknown Clan")
        clanTag = server_clan.get("CLAN_TAG", "UNK")
        clanDesc = server_clan.get("CLAN_DESCRIPTION", "No description.")

        # Handle message tracking.
        msg_file = "storage/messages.json"
        all_msg_data = {}
        if os.path.exists(msg_file):
            with open (msg_file, "r") as file:
                try:
                    all_msg_data = json.load(file)
                except json.JSONDecodeError:
                    pass
        
        # Initialize this server's message entry if it doesn't exist
        if guild_id not in all_msg_data:
            all_msg_data[guild_id] = {"ROSTER": None, "KILLS": None, "RESULTS": None}
        
        server_msgs = all_msg_data[guild_id]

        async def fetch_ch(cid):
            if not cid: return None
            channel = self.bot.get_channel(int(cid))
            if not channel:
                try:
                    channel = await self.bot.fetch_channel(int(cid))
                except:
                    return None
            return channel

        async def checkmsg(channel, channelkey, text):  
            saved_msgid = server_msgs.get(channelkey)  
            
            if saved_msgid:
                try:
                    # Try to fetch the message to confirm it still exists
                    await channel.fetch_message(saved_msgid)
                    
                    # If it exists, send a specific alert for this channel
                    await interaction.followup.send(
                        f"ℹ️ The **{channelkey}** message already exists in {channel.mention}.", 
                        ephemeral=True
                    )
                    return # Exit the function so we don't send a duplicate
                except discord.NotFound:
                    pass 

            # If we reached this point, the message doesn't exist. Send it now.
            new_msg = await channel.send(text)
            server_msgs[channelkey] = new_msg.id

        # Roster
        roster_ch = await fetch_ch(server_channels.get("ROSTER"))
        if roster_ch:
            roster_msg = f"# 🛡️ {clanName} [{clanTag}] Roster\n*{clanDesc}*\n\n> *The roster is currently empty. Use `/roster add` to add members!*"
            await checkmsg(roster_ch, "ROSTER", roster_msg)

        # Kills
        kills_ch = await fetch_ch(server_channels.get("KILLS"))
        if kills_ch:
            kills_msg = f"# ⚔️ {clanName} Top Kills\n\n> *No kills logged yet. Use `/kills add` to update the leaderboard!*"
            await checkmsg(kills_ch, "KILLS", kills_msg)

        # Results
        results_ch = await fetch_ch(server_channels.get("RESULTS"))
        if results_ch:
            results_msg = f"# 🏆 {clanName} VS History\n\n> *No matches recorded. Use `/vs add` to log a match!*"
            await checkmsg(results_ch, "RESULTS", results_msg)

        # Save data. 
        all_msg_data[guild_id] = server_msgs
        with open(msg_file, "w") as file:
            json.dump(all_msg_data, file, indent=4)

        await interaction.followup.send("✅ The channels now have messages printed!")

async def setup(bot):
    await bot.add_cog(PrintChannels(bot))