# Main starting bot logic. Whenever I run the bot from here, run the code in this file with all the imports coming after.
# Usage: Just hit the play button on VS Code (if on local machine). You need the .env in the directory, with the token.

# Essential:
import discord, os
from discord.ext import commands
from discord import app_commands 
from dotenv import load_dotenv 

# Cogs to be used from other .py files across the project directory:
from setchannels import ChannelManager 
from clan import ClansManager
from clan import ClansModal
from getchannels import GetChannels
from printchannels import PrintChannels
from setroles import RoleManager
from roster import RosterCog

load_dotenv() # load the token 
token = os.getenv('DISCORD_TOKEN') # get the token (secret), so we can run the bot.
GUILD_ID = int(os.getenv('GUILD_ID')) # get the guild ID from the environment variable and convert it to an integer

# Start the bot, import all the cogs, and get ready.
class Client(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(ChannelManager(self))
        await self.add_cog(ClansManager(self))
        await self.add_cog(GetChannels(self))
        await self.add_cog(PrintChannels(self))
        await self.add_cog(RoleManager(self))
        await self.add_cog(RosterCog(self))
        print("Cogs loaded successfully!") 

        self.tree.on_error = self.on_app_command_error

# Sync commands and print the "Ready" message.
    async def on_ready(self):
        print(f'Logged in as {self.user}')

        try:
            guild = discord.Object(id=GUILD_ID)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} command(s) to the server.')
        except Exception as e:
            print(f"An error occurred while syncing commands: {e}")

# This prints the error if there permission < permission required, exception otherwise.
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            # If the command failed because of our has_permission gate:
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        else:
            # If it's a different kind of error, print in terminal instead.
            print(f"Ignoring exception in command '{interaction.command.name}': {error}")

# Moved intents to be declared before the client.
intents = discord.Intents.default() 
intents.message_content = True # Enable the message content intent
client = Client(command_prefix="!", intents=intents)

# Slash command to play rock-paper-scissors, can be used by anyone
# Usage: /rps choice(rock/paper/scissors)
@client.tree.command(name="rps", description="Play rock paper scissors with the bot!",guild=discord.Object(id=GUILD_ID))
@app_commands.describe(choice="Choose rock, paper, or scissors")
@app_commands.choices(choice=[
    app_commands.Choice(name="rock 🪨", value="rock"),
    app_commands.Choice(name="paper 📄", value="paper"),
    app_commands.Choice(name="scissors ✂️", value="scissors")
])
# Logic for bot to choose the options and determine the winner. Toy command, no further purpose. 
async def rps(interaction: discord.Interaction, choice: app_commands.Choice[str]):
    import random
    options = ["rock", "paper", "scissors"]
    bot_choice = random.choice(options)

    if choice.value == bot_choice:
        result = "It's a tie!"
    
    # Win conditions
    elif (choice.value == "rock" and bot_choice == "scissors") or (choice.value == "paper" and bot_choice == "rock") or (choice.value == "scissors" and bot_choice == "paper"):
        result = "You win! 🥇"
    else:
        result = "You lose! 🙁"    

    # Print message to the channel with game result. 
    await interaction.response.send_message(f'You chose {choice.value}, \nI chose {bot_choice}. \n**{result}**') 

client.run(token) # use the secret token to run the bot.