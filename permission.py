# Helper function to check permissions for each command in the bot.
# Use roles.json to check the roles in the server, split across four access levels
# Level 1 = Member. Level 2 = Officer. Level 3 = Admin. Level 4 = Owners
import discord
from discord import app_commands
import json
import os

def has_permission(required_level: int):
    async def predicate(interaction: discord.Interaction) -> bool:
        # If the user IS the serevr owner, all permissions are granted regardless. This prevents us from getting stuck.
        if interaction.user.id == interaction.guild.owner_id:
            return True
        # Server ID is logged as a string to go onto the JSONs.
        guild_id = str(interaction.guild_id)
        if not os.path.exists('storage/roles.json'):
            return False 

        # Try to open the roles file and get the roles for the specific server ID defined earlier.
        try:
            with open('storage/roles.json', 'r') as f:
                all_roles_data = json.load(f)
                role_map = all_roles_data.get(guild_id, {})
        except (json.JSONDecodeError, FileNotFoundError):
            role_map = {}

        # Check the user's role if they match the levels.
        user_role_ids = [role.id for role in interaction.user.roles]
        
        # Cumulative check: Required level up to 4
        for level in range(required_level, 5): 
            saved_role_id = role_map.get(str(level))
            if saved_role_id in user_role_ids:
                return True
        
        return False

    # This returns the check to the slash command
    return app_commands.check(predicate)