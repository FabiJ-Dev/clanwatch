# Purpose 1: CREATE the clan (Name, 3-letter tag), and description. Will be posted in the ROSTER channel.
# Purpose 2: MODIFY the clan (Change name, change tag, change description). 
# Purpose 3: DELETE the clan. Will remove the clan info from the specified server. 
# Usage: /clan (create/edit/delete) and it opens up a Modal.

import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
import os 
from dotenv import load_dotenv 
import json 
from permission import has_permission

load_dotenv() 
GUILD_ID = int(os.getenv('GUILD_ID')) 

class ClansModal(discord.ui.Modal):
    name = ui.TextInput(
        label='Clan Name',
        placeholder='Enter your clan name.',
        min_length=2,
        max_length=25,
        required=True
    )
    
    tag = ui.TextInput(
        label='Clan Tag',
        placeholder='e.g. ABC',
        min_length=1,
        max_length=3,
        required=True
    )

    description = ui.TextInput(
        label='Clan Description',
        style=discord.TextStyle.paragraph,
        placeholder='Describe your clan.',
        required=False,
        max_length=100
    )

    # NEW: We now require the guild_id to be passed into the modal
    def __init__(self, action_type: str, guild_id: str):
        super().__init__(title=f'{action_type.title()} Clan')
        self.action_type = action_type
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        clan_name = self.name.value
        clan_tag = self.tag.value.upper()
        clan_desc = self.description.value

        # 1. Load the existing multi-server data first so we don't overwrite other servers!
        file_path = 'storage/clansinfo.json'
        data = {}
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    pass

        # 2. Save THIS server's info under its specific Guild ID
        data[self.guild_id] = {
            "CLAN_NAME": clan_name,
            "CLAN_TAG": clan_tag,
            "CLAN_DESCRIPTION": clan_desc 
        }
        
        # 3. Write it all back
        with open (file_path, 'w') as f:
            json.dump(data, f, indent=4)

        await interaction.response.send_message(
            f'✅ **Clan {self.action_type} has been created!**\n**Name:** {clan_name} [{clan_tag}]\n**Description:** {clan_desc}')


class ClansManager(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @app_commands.command(name="clan", description="Manage your clan settings")
    @has_permission(4)
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(option="Choose an operation")
    @app_commands.choices(option=[
        app_commands.Choice(name="Create", value="CREATE"),
        app_commands.Choice(name="Edit", value="EDIT"),
        app_commands.Choice(name="Delete", value="DELETE")
    ])
    async def clan(self, interaction: discord.Interaction, option: app_commands.Choice[str]):
        
        # Grab the Server ID as a string (JSON keys must be strings)
        guild_id = str(interaction.guild_id)
        
        # Load the file to check what currently exists
        file_path = 'storage/clansinfo.json'
        data = {}
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    pass

        # --- THE PRE-CHECKS ---
        
        if option.value == "CREATE":
            # If the Guild ID is already in the JSON, stop them!
            if guild_id in data:
                await interaction.response.send_message("❌ A clan already exists for this server! Use `/clan edit` instead.", ephemeral=True)
                return
            
            # If not, let them proceed. Pass the guild_id to the Modal.
            modal = ClansModal(action_type=option.value, guild_id=guild_id)
            await interaction.response.send_modal(modal)

        elif option.value == "EDIT":
            # If the Guild ID is NOT in the JSON, stop them!
            if guild_id not in data:
                await interaction.response.send_message("❌ No clan exists yet! Use `/clan create` first.", ephemeral=True)
                return
            
            modal = ClansModal(action_type=option.value, guild_id=guild_id)
            await interaction.response.send_modal(modal)

        elif option.value == "DELETE":
            # Delete ONLY this server's clan data
            if guild_id in data:
                del data[guild_id] 
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)
                await interaction.response.send_message("🗑️ Clan information has been deleted.")
            else:
                await interaction.response.send_message("❌ No clan exists to delete.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ClansManager(bot))