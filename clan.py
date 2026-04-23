# Purpose 1: CREATE the clan (Name, 3-letter tag), and description. Will be posted in the ROSTER channel.
# Purpose 2: MODIFY the clan (Change name, change tag, change description). 
# Purpose 3: DELETE the clan. Will remove the clan info. 
# Usage: /clan (create/edit/delete) and it opens up a MENU.

import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
import os # For loading environment variables
from dotenv import load_dotenv # get the .env file and load the environment variables
import json # For storing clan information in the file. 

load_dotenv() # load the token
GUILD_ID=int(os.getenv('GUILD_ID')) # get the guild ID from the environment variable and convert it to an integer

class ClansModal(discord.ui.Modal):
# Each is a box on the modal.
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
        max_length=500
    )

    def __init__(self, action_type: str):
        # We can change the title based on whether they are creating or editing
        super().__init__(title=f'{action_type.title()} Clan')
        self.action_type = action_type

    # Responses from modal sent here.
    async def on_submit(self, interaction: discord.Interaction):
        clan_name = self.name.value
        clan_tag = self.tag.value.upper()
        clan_desc = self.description.value

        json_data = {
            "CLAN_NAME": clan_name,
            "CLAN_TAG": clan_tag,
            "CLAN_DESCRIPTION": clan_desc 
        }
        
        # Store in JSON for storage
        with open ('storage/clansinfo.json', 'w') as f:
            json.dump(json_data, f, indent=4)

        await interaction.response.send_message(
            f'✅ **Clan {self.action_type}:**\n**Name:** {clan_name} [{clan_tag}]\n**Desc:** {clan_desc}')

class ClansManager(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @app_commands.command(name="clan", description="Manage your clan settings")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(option="Choose an operation")
    @app_commands.choices(option=[
        app_commands.Choice(name="Create", value="CREATE"),
        app_commands.Choice(name="Edit", value="EDIT"),
        app_commands.Choice(name="Delete", value="DELETE")
    ])
    async def clan(self, interaction: discord.Interaction, option: app_commands.Choice[str]):

        if option.value == "DELETE":
            with open('storage/clansinfo.json', 'w') as f:
                json.dump({}, f, indent=4)
            await interaction.response.send_message("🗑️ Clan information has been deleted.")
        else:
            modal = ClansModal(action_type=option.value)
            await interaction.response.send_modal(modal)

# Send to main.py:
async def setup(bot):
    await bot.add_cog(ClansManager(bot))


    