# Helper function to check permissions for each command in the bot.
# Use roles.json to check the roles in the server, split across four access levels
# Level 1 = Member. Level 2 = Officer. Level 3 = Admin. Level 4 = Owners

# Essential:
import discord, json, os
from discord import app_commands

def has_permission(required_level: int):
    async def predicate(interaction: discord.Interaction) -> bool:
        # If the user IS the server owner, all permissions are granted regardless. This prevents us from getting stuck on first-time setup.
        if interaction.user.id == interaction.guild.owner_id:
            return True
        # Server ID is logged as a string to go onto the roles.json, which contains role IDs for each level per server.
        guild_id = str(interaction.guild_id)

        # Try to open the roles file and get the roles for the specific server ID defined earlier.
        try:
            with open('storage/roles.json', 'r') as file:
                roles_data = json.load(file)
                role_map = roles_data.get(guild_id, {})
        except (json.JSONDecodeError, FileNotFoundError):
            role_map = {}

        # Check the user's role if they match the levels.
        user_roles = [role.id for role in interaction.user.roles]
        
        # Allow access if user has required level or higher for a command. 
        for level in range(required_level, 5): 
            role_id = role_map.get(str(level))
            if role_id and role_id in user_roles:
                return True
        return False

    # This returns the check to the slash command
    return app_commands.check(predicate)