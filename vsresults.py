import discord, os, json
from discord.ext import commands
from discord import app_commands 
from dotenv import load_dotenv 
from permission import has_permission
from datetime import datetime

load_dotenv()
GUILD_ID = int(os.getenv('GUILD_ID'))

class VsGroup(app_commands.Group):
    def __init__(self, bot):
        super().__init__(name="vs", description="Manage the VS history.")
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

    def is_valid_date(self, date_str: str):
        try:
            datetime.strptime(date_str, "%d/%m/%y")
            return True
        except ValueError:
            return False

    def is_valid_score(self, score: str):
        parts = score.split(":")
        if len(parts) != 2: return False
        try:
            s1, s2 = int(parts[0].strip()), int(parts[1].strip())
            return 0 <= s1 <= 99 and 0 <= s2 <= 99
        except ValueError: return False

    def sort_matches(self, matches):
        return sorted(matches, key=lambda m: datetime.strptime(m["date"], "%d/%m/%y"))

    async def refresh_vs_message(self, interaction: discord.Interaction, guild_id: str):
        vs_data = self.load_json('storage/vshistory.json').get(guild_id, [])
        clan_info = self.load_json('storage/clansinfo.json').get(guild_id, {})
        msg_data = self.load_json('storage/messages.json').get(guild_id, {})
        channels_data = self.load_json('storage/channels.json').get(guild_id, {})

        # Use dynamic info from storage instead of hardcoded strings
        clan_tag = clan_info.get("CLAN_TAG", "UNK")
        clan_name = clan_info.get("CLAN_NAME", "Clan")

        content = f"# ⚔️ {clan_name} VS History\n```\n"
        wins = losses = draws = 0
        matches_count = len(vs_data)

        for index, match in enumerate(vs_data):
            s_parts = match["score"].split(":")
            our_s, opp_s = int(s_parts[0]), int(s_parts[1])

            res = "✅" if our_s > opp_s else "❌" if our_s < opp_s else "🟡"
            if res == "✅": wins += 1
            elif res == "❌": losses += 1
            else: draws += 1

            # Shifted ID is simply the current position in the sorted list
            match_id = f"{index + 1:02d}"
            content += f"{match_id} - {match['date']} | {clan_tag} {match['score']} {match['othertag']} | {res}\n"

        content += "```\n"
        wr = (wins / matches_count * 100) if matches_count > 0 else 0
        content += f"**Matches:** {matches_count} | **W:** {wins} **L:** {losses} **D:** {draws}\n**Win Rate:** {wr:.2f}%"

        chan_id = channels_data.get("RESULTS")
        m_id = msg_data.get("RESULTS")
        
        if chan_id and m_id:
            channel = self.bot.get_channel(int(chan_id))
            if channel:
                try:
                    msg = await channel.fetch_message(int(m_id))
                    await msg.edit(content=content)
                except: pass

    @app_commands.command(name="add", description="Add a result to history.")
    @has_permission(3)
    async def add(self, interaction: discord.Interaction, date: str, score: str, othertag: str):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)

        if not self.is_valid_date(date):
            return await interaction.followup.send("❌ Use `DD/MM/YY` format.")
        if not self.is_valid_score(score):
            return await interaction.followup.send("❌ Use `X:Y` format (Max 99).")
        
        # Enforce 3 letter cap and uppercase
        clean_tag = othertag[:3].upper()

        vs_db = self.load_json('storage/vshistory.json')
        if guild_id not in vs_db: vs_db[guild_id] = []

        vs_db[guild_id].append({"date": date, "score": score, "othertag": clean_tag})
        vs_db[guild_id] = self.sort_matches(vs_db[guild_id])
        
        self.save_json('storage/vshistory.json', vs_db)
        await self.refresh_vs_message(interaction, guild_id)
        await interaction.followup.send(f"✅ Added match vs **{clean_tag}**.")

    @app_commands.command(name="edit", description="Edit a match using its ID.")
    @has_permission(3)
    async def edit(self, interaction: discord.Interaction, id: int, date: str = None, score: str = None, othertag: str = None):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        vs_db = self.load_json('storage/vshistory.json')

        history = vs_db.get(guild_id, [])
        if not history or id < 1 or id > len(history):
            return await interaction.followup.send(f"❌ Match #{id:02d} not found.")

        idx = id - 1
        if date:
            if not self.is_valid_date(date): return await interaction.followup.send("❌ Invalid date.")
            history[idx]["date"] = date
        if score:
            if not self.is_valid_score(score): return await interaction.followup.send("❌ Invalid score.")
            history[idx]["score"] = score
        if othertag:
            history[idx]["othertag"] = othertag[:3].upper()

        vs_db[guild_id] = self.sort_matches(history)
        self.save_json('storage/vshistory.json', vs_db)
        await self.refresh_vs_message(interaction, guild_id)
        await interaction.followup.send(f"✅ Updated match #{id:02d}.")

    @app_commands.command(name="delete", description="Delete a match (IDs will shift).")
    @has_permission(3)
    async def delete(self, interaction: discord.Interaction, id: int):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        vs_db = self.load_json('storage/vshistory.json')

        history = vs_db.get(guild_id, [])
        if not history or id < 1 or id > len(history):
            return await interaction.followup.send("❌ Match not found.")

        history.pop(id - 1) # Pop by index
        vs_db[guild_id] = history # No need to re-sort after simple deletion

        self.save_json('storage/vshistory.json', vs_db)
        await self.refresh_vs_message(interaction, guild_id)
        await interaction.followup.send(f"🗑️ Deleted match #{id:02d}. Remaining IDs have shifted.")

class VsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(VsGroup(bot), guild=discord.Object(id=GUILD_ID))

async def setup(bot):
    await bot.add_cog(VsCog(bot))