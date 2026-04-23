import discord
from discord.ext import commands
from discord import app_commands
import os # For loading environment variables
from dotenv import load_dotenv # get the .env file and load the environment variables

load_dotenv() # load the token 
token = os.getenv('DISCORD_TOKEN') # get the token (secret)
GUILD_ID = 740300637970890843 # replace with your server's ID

class Client(discord.Client):
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
# usage: /rps choice(rock/paper/scissors)
@client.tree.command(name="rps", description="Play rock paper scissors with the bot!")
async def rps(interaction: discord.Interaction, choice: str):
    import random
    choices = ["rock", "paper", "scissors"]
    bot_choice = random.choice(choices)

    if choice == bot_choice:
        result = "It's a tie!"
    elif (choice == "rock" and bot_choice == "scissors") or (choice == "paper" and bot_choice == "rock") or (choice == "scissors" and bot_choice == "paper"):
        result = "You win!"
    else:
        result = "You lose!"

intents = discord.Intents.default()
intents.message_content = True # Enable the message content intent

client.run(token) # use the secret token to run the bot