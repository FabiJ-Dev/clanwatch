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

    def __init__(self, action: str, guild_id: str):
        super().__init__(title=f'{action.title()} Clan')
        self.action = action
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        clan_name = self.name.value
        clan_tag = self.tag.value.upper() # Force uppercase for the tag.
        clan_desc = self.description.value

        clansinfo_file = 'storage/clansinfo.json'
        data = {}
        if os.path.exists(clansinfo_file):
            with open(clansinfo_file, 'r') as file:
                try: data = json.load(file) 
                except json.JSONDecodeError: pass 

        data[self.guild_id] = {
            "CLAN_NAME": clan_name,
            "CLAN_TAG": clan_tag,
            "CLAN_DESCRIPTION": clan_desc 
        }
        
        with open (clansinfo_file, 'w') as file:
            json.dump(data, file, indent=4) 

        await interaction.response.send_message(f'✅ **Clan {self.action} operation was successful!**\n**Name:** {clan_name} \n**Tag:** [{clan_tag}]\n**Description:** {clan_desc}')


# Logic for the command's selection options
class ClansManager(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    # Helper methods for cleaner file operations during mass-deletion
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

    @app_commands.command(name="clan", description="Manage your clan settings")
    @has_permission(4)
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.describe(option="Choose an operation")
    @app_commands.choices(option=[
        app_commands.Choice(name="Create", value="create"),
        app_commands.Choice(name="Edit", value="edit"),
        app_commands.Choice(name="Delete", value="delete")
    ])
    async def clan(self, interaction: discord.Interaction, option: app_commands.Choice[str]):
        guild_id = str(interaction.guild_id)
        clans_file = 'storage/clansinfo.json'
        data = self.load_json(clans_file)

        if option.value == "create":
            if guild_id in data:
                return await interaction.response.send_message("❌ A clan already exists for this server! Use `/clan edit` instead.", ephemeral=True)
            
            modal = ClansModal(action=option.value, guild_id=guild_id)
            await interaction.response.send_modal(modal)

        elif option.value == "edit":
            if guild_id not in data:
                return await interaction.response.send_message("❌ No clan exists yet! Use `/clan create` first.", ephemeral=True)
            
            modal = ClansModal(action=option.value, guild_id=guild_id)
            await interaction.response.send_modal(modal)

        elif option.value == "delete":
            # Strict verification for Server Owner
            if interaction.user.id != interaction.guild.owner_id:
                return await interaction.response.send_message("⚠️ Only the server owner can delete the clan. Contact the server owner.", ephemeral=True)

            if guild_id not in data:
                return await interaction.response.send_message("❌ No clan exists to delete.", ephemeral=True)

            # Defer response because fetching and deleting messages takes time
            await interaction.response.defer()

            # 1. Delete Discord Messages (Roster, VS History, Kills)
            messages_db = self.load_json('storage/messages.json').get(guild_id, {})
            channels_db = self.load_json('storage/channels.json').get(guild_id, {})

            for msg_type in ["ROSTER", "RESULTS", "KILLS"]:
                chan_id = channels_db.get(msg_type)
                msg_id = messages_db.get(msg_type)
                
                if chan_id and msg_id:
                    channel = self.bot.get_channel(int(chan_id))
                    if channel:
                        try:
                            msg = await channel.fetch_message(int(msg_id))
                            await msg.delete()
                        except discord.NotFound:
                            pass # Message was already deleted manually
                        except discord.Forbidden:
                            print(f"Lacking permissions to delete {msg_type} message.")
                        except Exception as e:
                            print(f"Error deleting {msg_type} message: {e}")

            # 2. Wipe Guild Data from all interconnected JSON files
            files_to_clean = [
                'storage/clansinfo.json',
                'storage/roster.json',
                'storage/vshistory.json',
                'storage/kills.json',
                'storage/messages.json',
                'storage/channels.json',
            ]

            for filepath in files_to_clean:
                file_data = self.load_json(filepath)
                if guild_id in file_data:
                    del file_data[guild_id]
                    self.save_json(filepath, file_data)

            await interaction.followup.send("🗑️ **Clan Deleted.** All messages, rosters, histories, and data for this server have been completely wiped.")

async def setup(bot):
    await bot.add_cog(ClansManager(bot))