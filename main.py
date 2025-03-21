import discord.py
import os
import random
import wavelink
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
    return embed

@bot.tree.command(name= "support", description="Support Server")
async def ping(interaction: discord.Interacion):
    embed = create_support_embed()
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="play", description="Play a song in a voice channel")
async def play(interaction: discord.Interaction, search: str):
    if not interaction.user.voice:
        return await interaction.response.send_message("❌ You must be in a voice channel to use this command!", ephemeral=True)

    vc: wavelink.Player = interaction.guild.voice_client or await interaction.user.voice.channel.connect(cls=wavelink.Player)

    tracks = await wavelink.YouTubeTrack.search(search)
    if not tracks:
        return await interaction.response.send_message("❌ No results found.", ephemeral=True)

    track = tracks[0]
    await vc.play(track)

    embed = discord.Embed(
        title="🎶 Now Playing",
        description=f"[{track.title}]({track.uri})",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

    await interaction.response.send_message(embed=embed)

# Leave command
@bot.tree.command(name="leave", description="Disconnect the bot from the voice channel")
async def leave(interaction: discord.Interaction):
    if not interaction.guild.voice_client:
        return await interaction.response.send_message("❌ I'm not in a voice channel!", ephemeral=True)

    await interaction.guild.voice_client.disconnect()
    await interaction.response.send_message("✅ Disconnected!")

# 🔨 Warn Command
@bot.tree.command(name="warn", description="Warn a user")
@app_commands.describe(member="The user to warn", reason="Reason for the warning")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ You lack permission to warn members!", ephemeral=True)

    await interaction.response.send_message(f"⚠️ {member.mention} has been warned! Reason: {reason}")

    await log_action(interaction.guild, "⚠️ User Warned", f"**{member.mention}** was warned.\n**Reason:** {reason}")

# 🔨 Kick Command
@bot.tree.command(name="kick", description="Kick a user from the server")
@app_commands.describe(member="The user to kick", reason="Reason for the kick")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ You lack permission to kick members!", ephemeral=True)

    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member.mention} has been kicked! Reason: {reason}")

    await log_action(interaction.guild, "👢 User Kicked", f"**{member.mention}** was kicked.\n**Reason:** {reason}")

# 🔨 Ban Command
@bot.tree.command(name="ban", description="Ban a user from the server")
@app_commands.describe(member="The user to ban", reason="Reason for the ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ You lack permission to ban members!", ephemeral=True)

    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 {member.mention} has been banned! Reason: {reason}")

    await log_action(interaction.guild, "🔨 User Banned", f"**{member.mention}** was banned.\n**Reason:** {reason}")

# 🔨 Mute Command
@bot.tree.command(name="mute", description="Mute a user (requires a 'Muted' role)")
@app_commands.describe(member="The user to mute", reason="Reason for the mute")
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ You lack permission to mute members!", ephemeral=True)

    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not muted_role:
        return await interaction.response.send_message("❌ No 'Muted' role found! Please create one.", ephemeral=True)

    await member.add_roles(muted_role, reason=reason)
    await interaction.response.send_message(f"🔇 {member.mention} has been muted! Reason: {reason}")

    await log_action(interaction.guild, "🔇 User Muted", f"**{member.mention}** was muted.\n**Reason:** {reason}")

bot.run(TOKEN)
