import discord, os, json
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from permission import has_permission

load_dotenv()
GUILD_ID = int(os.getenv('GUILD_ID'))

class KillsGroup(app_commands.Group):
    def __init__(self, bot):
        super().__init__(name="kills", description="Manage player kill counts.")
        self.bot = bot

    def load_json(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                try: return json.load(file)
                except: return {}
        return {}

    def save_json(self, filepath, data):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)

    def get_roster_key(self, roster_data, member: discord.Member = None, nickname: str = None):
        if member:
            key = str(member.id)
            if key in roster_data: return key
        if nickname:
            for key, data in roster_data.items():
                if data.get('nickname').lower() == nickname.lower():
                    return key
        return None

    async def refresh_kills_message(self, interaction: discord.Interaction, guild_id: str):
        kills_db = self.load_json('storage/kills.json').get(guild_id, {})
        clan_info = self.load_json('storage/clansinfo.json').get(guild_id, {})
        msg_data = self.load_json('storage/messages.json').get(guild_id, {})
        channels_data = self.load_json('storage/channels.json').get(guild_id, {})

        clan_name = clan_info.get("CLAN_NAME", "Clan").upper()
        
        # Pull data directly from kills_db, not the roster
        leaderboard = []
        for user_key, data in kills_db.items():
            count = data.get("kills", 0)
            # 1. Check: If kills are 0, do NOT appear.
            if count > 0:
                leaderboard.append({
                    "nickname": data.get("nickname", "Unknown"),
                    "flag": data.get("flag", "🏳️"),
                    "kills": count
                })

        # Sort by kills descending
        leaderboard.sort(key=lambda x: x['kills'], reverse=True)

        content = f"# TOP KILLS FOR {clan_name}:\n"
        if not leaderboard:
            content += "*No recorded kills yet.*"
        else:
            for i, p in enumerate(leaderboard, 1):
                content += f"{i}. {p['flag']} {p['nickname']} - {p['kills']} ☠\n"

        channel_id = channels_data.get("KILLS")
        msg_id = msg_data.get("KILLS")
        
        if channel_id and msg_id:
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                try:
                    msg = await channel.fetch_message(int(msg_id))
                    await msg.edit(content=content)
                except: pass

    @app_commands.command(name="add", description="Add kills to a player.")
    @has_permission(3)
    async def add(self, interaction: discord.Interaction, count: int, member: discord.Member = None, nickname: str = None):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        
        roster_db = self.load_json('storage/roster.json').get(guild_id, {})
        kills_db = self.load_json('storage/kills.json')
        if guild_id not in kills_db: kills_db[guild_id] = {}

        # Look for existing data in kills_db first (for removed members) or roster
        target_key = self.get_roster_key(roster_db, member, nickname)
        
        # If not in roster, check if they already exist in the kills_db (persistent data)
        if not target_key:
            for k, v in kills_db[guild_id].items():
                if nickname and v.get('nickname', '').lower() == nickname.lower():
                    target_key = k
                    break

        if not target_key:
            return await interaction.followup.send("❌ Player not found in roster or history.")

        # Update persistent data with current roster info if they still exist there
        if target_key in roster_db:
            kills_db[guild_id][target_key] = {
                "nickname": roster_db[target_key]["nickname"],
                "flag": roster_db[target_key]["flag"],
                "kills": kills_db[guild_id].get(target_key, {}).get("kills", 0) + count
            }
        else:
            # Player is removed from roster but stays in kills history
            kills_db[guild_id][target_key]["kills"] += count
        
        self.save_json('storage/kills.json', kills_db)
        await self.refresh_kills_message(interaction, guild_id)
        await interaction.followup.send(f"✅ Added {count} kills.")

    @app_commands.command(name="remove", description="Remove kills.")
    @has_permission(3)
    async def remove(self, interaction: discord.Interaction, count: int, member: discord.Member = None, nickname: str = None):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        kills_db = self.load_json('storage/kills.json')

        # Find key in the kills database specifically
        target_key = None
        if guild_id in kills_db:
            if member: target_key = str(member.id)
            elif nickname:
                for k, v in kills_db[guild_id].items():
                    if v.get('nickname', '').lower() == nickname.lower():
                        target_key = k
                        break

        if not target_key or target_key not in kills_db[guild_id]:
            return await interaction.followup.send("❌ Player has no kill data.")

        current = kills_db[guild_id][target_key]["kills"]
        kills_db[guild_id][target_key]["kills"] = max(0, current - count)

        self.save_json('storage/kills.json', kills_db)
        await self.refresh_kills_message(interaction, guild_id)
        await interaction.followup.send(f"✅ Removed {count} kills.")

    @app_commands.command(name="set", description="Set exact kill count.")
    @has_permission(3)
    async def set(self, interaction: discord.Interaction, count: int, member: discord.Member = None, nickname: str = None):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        roster_db = self.load_json('storage/roster.json').get(guild_id, {})
        kills_db = self.load_json('storage/kills.json')
        if guild_id not in kills_db: kills_db[guild_id] = {}

        target_key = self.get_roster_key(roster_db, member, nickname)
        
        if not target_key and guild_id in kills_db:
            for k, v in kills_db[guild_id].items():
                if nickname and v.get('nickname', '').lower() == nickname.lower():
                    target_key = k
                    break

        if not target_key:
            return await interaction.followup.send("❌ Player not found.")

        # Ensure snapshot info is maintained
        if target_key in roster_db:
            kills_db[guild_id][target_key] = {
                "nickname": roster_db[target_key]["nickname"],
                "flag": roster_db[target_key]["flag"],
                "kills": max(0, count)
            }
        else:
            kills_db[guild_id][target_key]["kills"] = max(0, count)

        self.save_json('storage/kills.json', kills_db)
        await self.refresh_kills_message(interaction, guild_id)
        await interaction.followup.send(f"✅ Set kills to {count}.")

    @app_commands.command(name="clear", description="Wipe player from leaderboard entirely.")
    @has_permission(3)
    async def clear(self, interaction: discord.Interaction, member: discord.Member = None, nickname: str = None):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        kills_db = self.load_json('storage/kills.json')

        if guild_id not in kills_db:
            return await interaction.followup.send("❌ No data found.")

        target_key = None
        if member: target_key = str(member.id)
        elif nickname:
            for k, v in kills_db[guild_id].items():
                if v.get('nickname', '').lower() == nickname.lower():
                    target_key = k
                    break

        if target_key and target_key in kills_db[guild_id]:
            # Completely remove the entry to satisfy the "not 0" and "permanent removal" rules
            del kills_db[guild_id][target_key]
            self.save_json('storage/kills.json', kills_db)
            await self.refresh_kills_message(interaction, guild_id)
            return await interaction.followup.send("🧹 Player removed from the leaderboard.")
        
        await interaction.followup.send("❌ Player not found on the leaderboard.")

class KillsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(KillsGroup(bot), guild=discord.Object(id=GUILD_ID))

async def setup(bot):
    await bot.add_cog(KillsCog(bot))