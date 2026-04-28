# Usage: /clan (create/edit/delete) and it opens up a Modal where you can enter name, tag, and description.
# Purpose 1: Create clans in the server. Only one clan can exist in a server at a time.
# Purpose 2: Edit clan information before printing your messages in case you made a mistake.
# Purpose 3: Delete the clan completely (requires Level 4 - Owner) and all data associated with it.

# Essential:
import discord, os, json
from discord.ext import commands
from discord import app_commands
from discord import ui
from dotenv import load_dotenv 
from permission import has_permission

# Load token and get the guild ID:
load_dotenv() 
GUILD_ID = int(os.getenv('GUILD_ID')) 

# Logic for the modal (popup with up to 5 pieces of information)
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

    # guild_id ensures all clan operations are scoped to the correct server
    # action will modify the title of the modal to be "Edit" or "Create" clan. 
    def __init__(self, action: str, guild_id: str):
        super().__init__(title=f'{action.title()} Clan')
        self.action = action
        self.guild_id = guild_id

    # When we submit the modal, pass to here so we can save the info to a file and continue the logic.
    async def on_submit(self, interaction: discord.Interaction):
        clan_name = self.name.value
        clan_tag = self.tag.value.upper() # Force uppercase for the tag.
        clan_desc = self.description.value

        # Load the filepath
        clansinfo_file = 'storage/clansinfo.json'
        data = {}
        if os.path.exists(clansinfo_file):
            with open(clansinfo_file, 'r') as file: #Open "clansinfo_file" to extract, and pass it as "file".
                try:
                    data = json.load(file) # Load clansinfo_file and plug it into data (dictionary with keys)
                except json.JSONDecodeError:
                    pass # Do NOT continue if we come here, it means something went wrong. 

        # Save clan info into the JSON under this specific format
        data[self.guild_id] = {
            "CLAN_NAME": clan_name,
            "CLAN_TAG": clan_tag,
            "CLAN_DESCRIPTION": clan_desc 
        }
        
        # Open up clansinfo_file, 'w' for WRITE, as file.
        with open (clansinfo_file, 'w') as file:
            json.dump(data, file, indent=4) 

        await interaction.response.send_message(f'✅ **Clan {self.action} operation was successful!**\n**Name:** {clan_name} \n**Tag:**[{clan_tag}]\n**Description:** {clan_desc}')

# Logic for the command's selection options and to check for data if we edit.
class ClansManager(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @app_commands.command(name="clan", description="Manage your clan settings")
    @has_permission(4) # Requires Level 4 to edit the clan or create it. Only server owner can delete clan.  
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(option="Choose an operation")
    @app_commands.choices(option=[
        app_commands.Choice(name="Create", value="create"),
        app_commands.Choice(name="Edit", value="edit"),
        app_commands.Choice(name="Delete", value="delete")
    ])

    async def clan(self, interaction: discord.Interaction, option: app_commands.Choice[str]):
        # Grab the Server ID as a string (JSON keys must be strings)
        guild_id = str(interaction.guild_id)
        
        # Load the file to check what currently exists
        clans_file = 'storage/clansinfo.json'
        data = {}
        if os.path.exists(clans_file):
            with open(clans_file, 'r') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    pass

        if option.value == "create":
            # If there is already a guild ID for the server, STOP the command and print the error.
            if guild_id in data:
                await interaction.response.send_message("❌ A clan already exists for this server! Use `/clan edit` instead to change information.", ephemeral=True)
                return
            
            # If there is no clan, open the create modal and let them type information. 
            modal = ClansModal(action=option.value, guild_id=guild_id)
            await interaction.response.send_modal(modal)

        elif option.value == "edit":
            # If the Guild ID is not present in the json, STOP and print the error
            if guild_id not in data:
                await interaction.response.send_message("❌ No clan exists yet! Use `/clan create` first.", ephemeral=True)
                return
            
            # Else, open the modal again with "Edit Clan" title (line 46-49 helps us rename it to Edit)
            modal = ClansModal(action=option.value, guild_id=guild_id)
            await interaction.response.send_modal(modal)

        elif option.value == "delete":
            # Delete ONLY this server's clan data.
            # NEW CHECK: Only works if the server owner uses it. 
            if interaction.user.id == interaction.guild.owner_id:
                if guild_id in data:
                    del data[guild_id] 
                    with open(clans_file, 'w') as file:
                        json.dump(data, file, indent=4)
                    await interaction.response.send_message("🗑️ Clan information has been deleted.")
                else:
                    await interaction.response.send_message("❌ No clan exists to delete.", ephemeral=True)
            else: 
                await interaction.response.send_message("Only the server owner can delete the clan. Contact the server owner.")

# Pass the bot's modal and cog into main.py, once it is ready to use. 
async def setup(bot):
    await bot.add_cog(ClansManager(bot))