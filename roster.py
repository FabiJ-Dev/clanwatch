# Essential: 
import discord, os, json
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from permission import has_permission
import countrylist 

# Load token, get Guild ID
load_dotenv()
GUILD_ID = int(os.getenv('GUILD_ID'))

# RosterGroup since we need to have a GROUP of commands, not just one. 
class RosterGroup(app_commands.Group):
    def __init__(self, bot):
        super().__init__(name="roster", description="Manage the clan roster.")
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

    # Nickname check helper: Check if the nickname in the roster already exists.
    # Rule: Two players on the roster cannot share the same nickname. 
    def nickname_exists(self, roster_data, nickname):
        for data in roster_data.values():
            if data['nickname'] == nickname:
                return True
        return False

    # This will automatically refresh the roster message each time.
    async def refresh_roster_message(self, interaction: discord.Interaction, guild_id: str):
        roster_data = self.load_json('storage/roster.json').get(guild_id, {})
        clan_info = self.load_json('storage/clansinfo.json').get(guild_id, {})
        msg_data = self.load_json('storage/messages.json').get(guild_id, {})
        channels_data = self.load_json('storage/channels.json').get(guild_id, {})

        clan_tag = clan_info.get("CLAN_TAG", "UNK")
        clan_name = clan_info.get("CLAN_NAME", "Unknown Clan")
        clan_desc = clan_info.get("CLAN_DESCRIPTION", "No description.")

        # Split users based on levels by collecting roster data and member data. 
        categories = {4: [], 3: [], 2: [], 1: []}
        for user_id, details in roster_data.items():
            lvl = details.get("level", 1)
            if lvl in categories:
                categories[lvl].append(details)

        content = f"# 🛡️ {clan_name} [{clan_tag}] Roster\n*{clan_desc}*\n\n"
        titles = {4: "👑 OWNERS", 3: "🛡️ ADMINS", 2: "⚔️ OFFICERS", 1: "👤 MEMBERS"}
        
        for level in [4, 3, 2, 1]:
            if categories[level]:
                content += f"**{titles[level]}**\n"
                for p in categories[level]:
                    content += f"> {p['flag']} {clan_tag} » {p['nickname']}\n"
                content += "\n"

        content += f"**Total Members: {len(roster_data)}/15**"

        # Print to the channel we had set earlier.
        channel_id = channels_data.get("ROSTER")
        msg_id = msg_data.get("ROSTER")
        if channel_id and msg_id:
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                try:
                    msg = await channel.fetch_message(int(msg_id))
                    await msg.edit(content=content)
                except: pass

    # COUNTRY - Split by first letter, THEN the country options themselves.
    LETTER_CHOICES = [app_commands.Choice(name=letter, value=letter) for letter in "ABCDEFGHIJKLMNOPQRSTUVWYZ"]

    async def country_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        selected_letter = interaction.namespace.letter 
        if not selected_letter: 
            return []
        possible_choices = countrylist.COUNTRIES.get(selected_letter, [])
        return [country for country in possible_choices if current.lower() in country.name.lower()][:25]

    # Usage: /roster add (nickname) (country-fl) (country) (@User if provided)
    @app_commands.command(name="add", description="Add a user to the roster.")
    @app_commands.choices(letter=LETTER_CHOICES)
    @app_commands.autocomplete(country=country_autocomplete)
    @has_permission(3)
    async def add(self, interaction: discord.Interaction, nickname: str, letter: app_commands.Choice[str], country: str, member: discord.Member = None):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        roster_db = self.load_json('storage/roster.json')
        roles_db = self.load_json('storage/roles.json').get(guild_id, {})
        
        if guild_id not in roster_db: roster_db[guild_id] = {}

        # Constraints: No long names and no dupe users.
        if len(nickname) > 12:
            return await interaction.followup.send("❌ **ERROR:** Nickname is too long! Max 12 characters.")
        if self.nickname_exists(roster_db[guild_id], nickname):
            return await interaction.followup.send(f"❌ **ERROR:** The nickname `{nickname}` is already on the roster!")
        if len(roster_db[guild_id]) >= 15:
            return await interaction.followup.send("❌ Clan is full (15/15).")
        if member and str(member.id) in roster_db[guild_id]:
            return await interaction.followup.send(f"❌ {member.mention} is already on the roster.")

        # Flag extraction
        flag = "🏳️" 
        # Changed 'country' to 'c' to avoid shadowing the argument
        for c in countrylist.COUNTRIES.get(letter.value, []):
            if c.value == country: # 'country' here refers to the command argument
                flag = c.name.split(" ")[0]
                break

        assigned_level = 1
        user_key = str(member.id) if member else f"GUEST_{nickname}"

        if member:
            if member.id == interaction.guild.owner_id:
                assigned_level = 4 # Server owners get instant Level 4 permissions.
            else:
                member_role_ids = [role.id for role in member.roles]
                for lvl_num in ["4", "3", "2", "1"]:
                    role_id = roles_db.get(lvl_num)
                    if role_id and int(role_id) in member_role_ids:
                        assigned_level = int(lvl_num)
                        break
                
                if assigned_level == 1:
                    lvl_1_id = roles_db.get("1")
                    if lvl_1_id:
                        target_role = interaction.guild.get_role(int(lvl_1_id))
                        if target_role and target_role not in member.roles:
                            try: await member.add_roles(target_role)
                            except: pass

        roster_db[guild_id][user_key] = {
            "nickname": nickname,
            "flag": flag,
            "level": assigned_level,
            "is_guest": member is None
        }
        
        self.save_json('storage/roster.json', roster_db)
        await self.refresh_roster_message(interaction, guild_id)
        
        status = f"External member **{nickname}**" if not member else member.mention
        await interaction.followup.send(f"✅ Added {status} to the roster!")

    # Edit command to change info about a player
    @app_commands.command(name="edit", description="Edit a roster entry.")
    @app_commands.choices(letter=LETTER_CHOICES)
    @app_commands.autocomplete(country=country_autocomplete)
    @has_permission(3)
    async def edit(self, interaction: discord.Interaction, letter: app_commands.Choice[str], country: str, new_nickname: str, member: discord.Member = None, old_nickname: str = None):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        roster_db = self.load_json('storage/roster.json')
        
        if guild_id not in roster_db: return await interaction.followup.send("❌ Roster is empty.")

        if len(new_nickname) > 12:
            return await interaction.followup.send("❌ **ERROR:** New nickname is too long! Max 12 characters.")

        target_key = None
        if member: target_key = str(member.id)
        elif old_nickname:
            for key, data in roster_db[guild_id].items():
                if data['nickname'] == old_nickname:
                    target_key = key
                    break
        
        if not target_key or target_key not in roster_db[guild_id]:
            return await interaction.followup.send("❌ Could not find that person on the roster.")

        if roster_db[guild_id][target_key]['nickname'] != new_nickname:
            if self.nickname_exists(roster_db[guild_id], new_nickname):
                return await interaction.followup.send(f"❌ The nickname `{new_nickname}` is already taken.")

        flag = "🏳️"
        # Changed 'country' to 'c' here as well
        for c in countrylist.COUNTRIES.get(letter.value, []):
            if c.value == country:
                flag = c.name.split(" ")[0]
                break

        roster_db[guild_id][target_key]['nickname'] = new_nickname
        roster_db[guild_id][target_key]['flag'] = flag
        
        self.save_json('storage/roster.json', roster_db)
        await self.refresh_roster_message(interaction, guild_id)
        await interaction.followup.send(f"✅ Updated roster entry for **{new_nickname}**!")

    @app_commands.command(name="remove", description="Remove a user from the roster and revoke their clan role.")
    @has_permission(3)
    async def remove(self, interaction: discord.Interaction, member: discord.Member = None, nickname: str = None):
        await interaction.response.defer(ephemeral=True)
        guild_id = str(interaction.guild_id)
        roster_db = self.load_json('storage/roster.json')
        roles_db = self.load_json('storage/roles.json').get(guild_id, {})

        if guild_id not in roster_db: 
            return await interaction.followup.send("❌ Roster is empty.")

        target_key = None
        if member:
            target_key = str(member.id)
        elif nickname:
            for key, data in roster_db[guild_id].items():
                if data['nickname'] == nickname:
                    target_key = key
                    break

        if not target_key or target_key not in roster_db[guild_id]:
            return await interaction.followup.send("❌ Target not found on the roster.")

        target_member = member
        if not target_member and target_key.isdigit():
            try:
                target_member = await interaction.guild.fetch_member(int(target_key))
            except:
                target_member = None

        if target_member:
            roles_to_remove = []
            for lvl_num in ["1", "2", "3", "4"]:
                role_id = roles_db.get(lvl_num)
                if role_id:
                    role_obj = interaction.guild.get_role(int(role_id))
                    if role_obj and role_obj in target_member.roles:
                        roles_to_remove.append(role_obj)
            
            if roles_to_remove:
                try:
                    await target_member.remove_roles(*roles_to_remove)
                except discord.Forbidden:
                    await interaction.followup.send("⚠️ Removed from roster, but I couldn't revoke roles (Bot role too low).", ephemeral=True)
                except Exception as e:
                    print(f"Error revoking roles: {e}")

        removed_name = roster_db[guild_id][target_key]['nickname']
        del roster_db[guild_id][target_key]

        self.save_json('storage/roster.json', roster_db)
        await self.refresh_roster_message(interaction, guild_id)
        await interaction.followup.send(f"🗑️ Removed **{removed_name}** from the roster and revoked their clan roles.")

class RosterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(RosterGroup(bot), guild=discord.Object(id=GUILD_ID))

async def setup(bot):
    await bot.add_cog(RosterCog(bot))