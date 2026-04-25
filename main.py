# Main starting bot logic. Whenever I run the bot from here, run the code in this file with all the imports coming after.
# Usage: Just hit the play button on VS Code (if on local machine).

import discord
from discord.ext import commands
from discord import app_commands 
import os # For loading environment variables
from dotenv import load_dotenv # get the .env file and load the environment variables
from setchannels import ChannelManager # import the ChannelManager cog from setchannels.py
from clan import ClansManager
from clan import ClansModal
from getchannels import GetChannels
from printchannels import PrintChannels

load_dotenv() # load the token 
token = os.getenv('DISCORD_TOKEN') # get the token (secret)
GUILD_ID = int(os.getenv('GUILD_ID')) # get the guild ID from the environment variable and convert it to an integer

# begin the bot 
class Client(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(ChannelManager(self)) # add the ChannelManager cog to the bot
        await self.add_cog(ClansManager(self))
        await self.add_cog(GetChannels(self))
        await self.add_cog(PrintChannels(self))
        print("Cogs loaded successfully!")

    async def on_ready(self):
        print(f'Logged in as {self.user}')

        try:
            guild = discord.Object(id=GUILD_ID)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} command(s) to the server.')
        except Exception as e:
            print(f"An error occurred while syncing commands: {e}")


# moved intents upwards to declare before the client. 
intents = discord.Intents.default() 
intents.message_content = True # Enable the message content intent
client = Client(command_prefix="!", intents=intents)

# slash command to play RPS 
# usage: /rps choice(rock/paper/scissors, limited to those options only
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
    elif (choice.value == "rock" and bot_choice == "scissors") or (choice.value == "paper" and bot_choice == "rock") or (choice.value == "scissors" and bot_choice == "paper"):
        result = "You win! 🥇"
    else:
        result = "You lose! 🙁"    

    # Print message to the channel with game result. 
    await interaction.response.send_message(f'You chose {choice.value}, \nI chose {bot_choice}. \n**{result}**') 

client.run(token) # use the secret token