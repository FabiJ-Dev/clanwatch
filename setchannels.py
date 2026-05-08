# Essential:
import discord, os, json
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv 
from permission import has_permission

load_dotenv()
GUILD_ID=int(os.getenv('GUILD_ID'))

class ChannelManager(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'ChannelManager cog is ready!')
    
    # Combined Logic: Single set of decorators only
    @app_commands.command(name="setchannels", description="Set the channels for the bot to post in!")
    @has_permission(3)
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(
        channel_type="Choose the type of channel to set (Kills/Results/Roster)", 
        channel="Select the actual channel"
    )
    @app_commands.choices(channel_type=[
        app_commands.Choice(name="Kills", value="KILLS"),
        app_commands.Choice(name="Results", value="RESULTS"),
        app_commands.Choice(name="Roster", value="ROSTER")
    ])
    async def setchannels(self, interaction: discord.Interaction, channel_type: app_commands.Choice[str], channel: discord.TextChannel):
        guild_id = str(interaction.guild_id)
        
        # 1. PRE-CHECK: Does the clan exist?
        clans_file = 'storage/clansinfo.json'
        if not os.path.exists(clans_file):
            return await interaction.response.send_message("❌ No clan found. Use `/clan create` first.", ephemeral=True)
        
        with open(clans_file, 'r') as f:
            clans_data = json.load(f)
        
        if guild_id not in clans_data:
            return await interaction.response.send_message("❌ No clan registered for this server! Use `/clan create`.", ephemeral=True)

        # 2. Save the channel configuration
        file_path = 'storage/channels.json'
        os.makedirs('storage', exist_ok=True)
        channels_data = {}
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try: channels_data = json.load(f)
                except: pass

        if guild_id not in channels_data:
            channels_data[guild_id] = {"KILLS": None, "RESULTS": None, "ROSTER": None}

        channels_data[guild_id][channel_type.value] = channel.id
        with open(file_path, 'w') as f:
            json.dump(channels_data, f, indent=4)

        # 3. BUILD TEMPLATE WITH EXISTING DATA (IF ANY)
        clan = clans_data[guild_id]
        name, tag, desc = clan["CLAN_NAME"], clan["CLAN_TAG"], clan["CLAN_DESCRIPTION"]
        template_text = ""

        if channel_type.value == "ROSTER":
            roster_data = {}
            if os.path.exists('storage/roster.json'):
                with open('storage/roster.json', 'r') as f:
                    roster_data = json.load(f).get(guild_id, {})
            
            if not roster_data:
                template_text = f"# 🛡️ {name} [{tag}] Roster\n*{desc}*\n\n> *The roster is currently empty.*"
            else:
                categories = {4: [], 3: [], 2: [], 1: []}
                for user_id, details in roster_data.items():
                    categories[details.get("level", 1)].append(details)
                
                template_text = f"# 🛡️ {name} [{tag}] Roster\n*{desc}*\n\n"
                titles = {4: "👑 OWNERS", 3: "🛡️ ADMINS", 2: "⚔️ OFFICERS", 1: "👤 MEMBERS"}
                for level in [4, 3, 2, 1]:
                    if categories[level]:
                        template_text += f"**{titles[level]}**\n"
                        for p in categories[level]:
                            template_text += f"> {p['flag']} {tag} » {p['nickname']}\n"
                        template_text += "\n"
                template_text += f"**Total Members: {len(roster_data)}/15**"

        elif channel_type.value == "KILLS":
            kills_data = {}
            if os.path.exists('storage/kills.json'):
                with open('storage/kills.json', 'r') as f:
                    kills_data = json.load(f).get(guild_id, {})
            
            leaderboard = [{"nickname": d.get("nickname", "Unknown"), "flag": d.get("flag", "🏳️"), "kills": d.get("kills", 0)} for d in kills_data.values() if d.get("kills", 0) > 0]
            leaderboard.sort(key=lambda x: x['kills'], reverse=True)
            
            template_text = f"# ⚔️ {name.upper()} TOP KILLS:\n"
            if not leaderboard:
                template_text += "> *No recorded kills yet.*"
            else:
                for i, p in enumerate(leaderboard, 1):
                    template_text += f"{i}. {p['flag']} {p['nickname']} - {p['kills']} ☠\n"

        elif channel_type.value == "RESULTS":
            vs_data = []
            if os.path.exists('storage/vshistory.json'):
                with open('storage/vshistory.json', 'r') as f:
                    vs_data = json.load(f).get(guild_id, [])
            
            template_text = f"# ⚔️ {name} VS History\n```\n"
            wins = losses = draws = 0
            matches_count = len(vs_data)
            
            if matches_count == 0:
                template_text = f"# 🏆 {name} VS History\n\n> *No matches recorded.*"
            else:
                from datetime import datetime
                for index, match in enumerate(vs_data):
                    s_parts = match["score"].split(":")
                    our_s, opp_s = int(s_parts[0]), int(s_parts[1])
                    res = "✅" if our_s > opp_s else "❌" if our_s < opp_s else "🟡"
                    if res == "✅": wins += 1
                    elif res == "❌": losses += 1
                    else: draws += 1
                    
                    match_id = f"{index + 1:02d}"
                    template_text += f"{match_id} - {match['date']} | {tag} {match['score']} {match['othertag']} | {res}\n"
                
                template_text += "```\n"
                wr = (wins / matches_count * 100) if matches_count > 0 else 0
                template_text += f"**Matches:** {matches_count} | **W:** {wins} **L:** {losses} **D:** {draws}\n**Win Rate:** {wr:.2f}%"

        # Send the message to the newly set channel
        new_msg = await channel.send(template_text)

        # 4. Save the Message ID so other modules can find it to edit later
        msg_file = 'storage/messages.json'
        msg_data = {}
        if os.path.exists(msg_file):
            with open(msg_file, 'r') as f:
                try: msg_data = json.load(f)
                except: pass

        if guild_id not in msg_data:
            msg_data[guild_id] = {"KILLS": None, "RESULTS": None, "ROSTER": None}
        
        msg_data[guild_id][channel_type.value] = new_msg.id
        with open(msg_file, 'w') as f:
            json.dump(msg_data, f, indent=4)

        await interaction.response.send_message(f'✅ Success! **{channel_type.value}** set to {channel.mention} and message generated.', ephemeral=True)
async def setup(bot):
    await bot.add_cog(ChannelManager(bot))