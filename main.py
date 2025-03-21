import discord.py
import os
import random
import youtube-dl
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

def create_ping_embed():
    embed = discord.Embed(
        title="Pong! 🏓",
        description="The bot is responsive!",
        color=discord.Color.blue()
    )
    return embed
  
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    embed = create_ping_embed()
    await interaction.response.send_message(embed=embed)
    
def create_support_embed()
    embed = discord.Embed(
        title="Support Server Link 👉"
        description = "https://discord.gg/Z3QEVV7VRb"
        color= discord.Color.red()
    )

bot.run(TOKEN)
