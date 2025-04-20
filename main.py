import discord
import os
import random
import yt_dlp
from discord import app_commands, embeds
from discord.ext import commands
import ffmpeg
import asyncio
import requests
import sqlite3




class Utility(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.afk_users = {}

TOKEN = (os.environ['TOKEN'])

def create_db():
	conn = sqlite3.connect('bad_words.db')
	c = conn.cursor()

	c.execute('''CREATE TABLE IF NOT EXISTS bad_words (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					word TEXT UNIQUE)''')

	c.execute('''CREATE TABLE IF NOT EXISTS user_warnings (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					user_id INTEGER,
					warning_count INTEGER)''')

	conn.commit()
	conn.close()


create_db()
conn = sqlite3.connect("bad_words.db")
cursor = conn.cursor()

def initialize_database():
	conn = sqlite3.connect('bad_words.db')  # Use your actual database file
	cursor = conn.cursor()



cursor.execute('''
	CREATE TABLE IF NOT EXISTS bad_words (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		word TEXT UNIQUE NOT NULL
	)
''')

conn.commit()
conn.close()


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guild_messages = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
music_queue = {}

CAT_API_KEY = "api_key=live_0iCbFhsdtY8IQbE8bVZOvtWzQCa4sq5A4qSIXp9VFFpqLukFEuW0Zk5TigtmSm4B"
WAIFU_API_KEY = "https://api.waifu.im/search"
NEWS_API_KEY = "2bb3b7f351804db985f8ad91e943c748"
NEWS_API_URL = "https://newsapi.org/v2/top-headlines?language=en"


def fetch_data(url, headers=None):
	try:
		response = requests.get(url, headers=headers)
		return response.json()
	except Exception:
		return None


def create_ping_embed():
	embed = discord.Embed(title="Pong! 🏓",
							description="The bot is responsive!",
							color=discord.Color.blue())
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
	latency = round(bot.latency * 1000)  # Convert to milliseconds
	embed = discord.Embed(
		title="Pong! 🏓",
		description=f"Bot Latency: {latency}ms",
		color=discord.Color.blue()
	)
	await interaction.response.send_message(embed=embed)


def create_support_embed():
	embed = discord.Embed(title="Support Server Link 👉",
							description="https://discord.gg/Z3QEVV7VRb",
							color=discord.Color.red())
	return embed


@bot.tree.command(name="support", description="Support Server")
async def xdlol(interaction: discord.Interaction):
	embed = create_support_embed()
	await interaction.response.send_message(embed=embed)


# Replace with your NewsAPI key
NEWS_API_KEY = "YOUR_NEWS_API_KEY"
NEWS_API_URL = "https://newsapi.org/v2/top-headlines?language=en"


@bot.tree.command(name="globalnews", description="Get the latest global news")
async def globalnews(interaction: discord.Interaction):
	headers = {"Authorization": f"Bearer {NEWS_API_KEY}"}

	try:
		response = requests.get(NEWS_API_URL, headers=headers).json()

		if response["status"] == "ok" and response["articles"]:
			embed = discord.Embed(
				title="Top Global News",
				description="Here are the top global news articles:",
				color=discord.Color.blue())

			# Limit the number of articles to display (e.g., top 5 articles)
			for article in response["articles"][:5]:
				embed.add_field(
					name=article["title"],
					value=
					f"{article.get('description', 'No description available.')}\n[Read more]({article['url']})",
					inline=False)

			await interaction.response.send_message(embed=embed)

		else:
			await interaction.response.send_message("❌ No global news found!",
													ephemeral=True)

	except requests.exceptions.RequestException as e:
		await interaction.response.send_message(
			f"❌ Error fetching global news: {str(e)}", ephemeral=True)

@bot.tree.command(name="poll", description="Create a poll with up to 10 options.")
async def poll(self, interaction: discord.Interaction, question: str, options: str):
		options_list = options.split(",")[:10]  # Limit to 10 options
		if len(options_list) < 2:
				await interaction.response.send_message("❌ You need at least two options!", ephemeral=True)
				return
		embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.blue())
		reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
		poll_message = await interaction.channel.send(embed=embed)
		for i, option in enumerate(options_list):
				embed.add_field(name=f"{reactions[i]} {option}", value="​", inline=False)
		await poll_message.edit(embed=embed)
		for i in range(len(options_list)):
				await poll_message.add_reaction(reactions[i])
		await interaction.response.send_message("✅ Poll created! Vote with reactions.", ephemeral=True)


@bot.tree.command(name="afk", description="Set your AFK status.")
async def afk(self, interaction: discord.Interaction, reason: str = "AFK"):
		self.afk_users[interaction.user.id] = reason
		await interaction.response.send_message(f"✅ {interaction.user.mention} is now AFK: {reason}", ephemeral=True)

@commands.Cog.listener()
async def on_message(self, message):
		if message.author.bot:
				return
		if message.mentions:
				for user in message.mentions:
						if user.id in self.afk_users:
								await message.channel.send(f"💤 {user.mention} is AFK: {self.afk_users[user.id]}")
		if message.author.id in self.afk_users:
				del self.afk_users[message.author.id]
				await message.channel.send(f"✅ {message.author.mention}, you are no longer AFK.")

def setup(bot):
		bot.add_cog(Utility(bot))


@bot.tree.command(
	name="weather",
	description="Get the weather of any city (No API key required)")
@app_commands.describe(city="Enter the city name")
async def weather(interaction: discord.Interaction, city: str):
	url = f"https://wttr.in/{city}?format=%C+%t"
	response = requests.get(url)
	if response.status_code == 200:
		weather_data = response.text.split()
		condition = weather_data[0]
		temperature = weather_data[1]
		embed = discord.Embed(
			title=f"🌦️ Weather in {city.capitalize()}",
			description=f"**{condition}**\nTemperature: {temperature}",
			color=discord.Color.blue())
		await interaction.response.send_message(embed=embed)
	else:
		await interaction.response.send_message("❌ City not found!",
												ephemeral=True)


# 🔨 Warn Command
@bot.tree.command(name="warn", description="Warn a user")
@app_commands.describe(member="The user to warn",
						 reason="Reason for the warning")
async def warn(interaction: discord.Interaction,
				 member: discord.Member,
				 reason: str = "No reason provided"):
	if not interaction.user.guild_permissions.manage_messages:
		return await interaction.response.send_message(
			"❌ You lack permission to warn members!", ephemeral=True)

	await interaction.response.send_message(
		f"⚠️ {member.mention} has been warned! Reason: {reason}")

	await log_action(
		interaction.guild, "⚠️ User Warned",
		f"**{member.mention}** was warned.\n**Reason:** {reason}")


# 🔨 Kick Command
@bot.tree.command(name="kick", description="Kick a user from the server")
@app_commands.describe(member="The user to kick", reason="Reason for the kick")
async def kick(interaction: discord.Interaction,
				 member: discord.Member,
				 reason: str = "No reason provided"):
	if not interaction.user.guild_permissions.kick_members:
		return await interaction.response.send_message(
			"❌ You lack permission to kick members!", ephemeral=True)

	await member.kick(reason=reason)
	await interaction.response.send_message(
		f"👢 {member.mention} has been kicked! Reason: {reason}")

	await log_action(
		interaction.guild, "👢 User Kicked",
		f"**{member.mention}** was kicked.\n**Reason:** {reason}")


# 🔨 Ban Command
@bot.tree.command(name="ban", description="Ban a user from the server")
@app_commands.describe(member="The user to ban", reason="Reason for the ban")
async def ban(interaction: discord.Interaction,
				member: discord.Member,
				reason: str = "No reason provided"):
	if not interaction.user.guild_permissions.ban_members:
		return await interaction.response.send_message(
			"❌ You lack permission to ban members!", ephemeral=True)

	await member.ban(reason=reason)
	await interaction.response.send_message(
		f"🔨 {member.mention} has been banned! Reason: {reason}")

	await log_action(
		interaction.guild, "🔨 User Banned",
		f"**{member.mention}** was banned.\n**Reason:** {reason}")



# 🔨 Mute Command
@bot.tree.command(name="mute",
					description="Mute a user (requires a 'Muted' role)")
@app_commands.describe(member="The user to mute", reason="Reason for the mute")
async def mute(interaction: discord.Interaction,
				 member: discord.Member,
				 reason: str = "No reason provided"):
	if not interaction.user.guild_permissions.manage_roles:
		return await interaction.response.send_message(
			"❌ You lack permission to mute members!", ephemeral=True)

	muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
	if not muted_role:
		return await interaction.response.send_message(
			"❌ No 'Muted' role found! Please create one.", ephemeral=True)

	await member.add_roles(muted_role, reason=reason)
	await interaction.response.send_message(
		f"🔇 {member.mention} has been muted! Reason: {reason}")

	await log_action(interaction.guild, "🔇 User Muted",
					 f"**{member.mention}** was muted.\n**Reason:** {reason}")


@bot.tree.command(name="invite", description="Invite the bot to your server")
async def invite(interaction: discord.Interaction):
	embed = discord.Embed(
		title="Invite Link  👉",
		description=
		"https://discord.com/oauth2/authorize?client_id=1352194041311137792",
		color=discord.Color.og_blurple())
	await interaction.response.send_message(embed=embed)


@bot.tree.command(
	name="clear",
	description="Delete a certain number of messages in the channel")
@app_commands.describe(amount="Number of messages to delete (max 100)")
async def clear(interaction: discord.Interaction, amount: int):
	# Ensure the command is used in a server
	if not interaction.guild:
		return await interaction.response.send_message(
			"❌ This command can only be used in a server!", ephemeral=True)

	# Ensure the user has permission to manage messages
	if not interaction.user.guild_permissions.manage_messages:
		return await interaction.response.send_message(
			"❌ You do not have permission to manage messages!", ephemeral=True)

	# Ensure the bot has permission to manage messages
	if not interaction.guild.me.guild_permissions.manage_messages:
		return await interaction.response.send_message(
			"❌ I do not have permission to manage messages!", ephemeral=True)

	# Ensure the amount is between 1 and 100
	if amount < 1 or amount > 100:
		return await interaction.response.send_message(
			"❌ Please enter a number between 1 and 100.", ephemeral=True)

	# Defer the response so it's not deleted
	await interaction.response.defer()

	# Delete messages
	deleted = await interaction.channel.purge(limit=amount)

	# Send confirmation message after purge
	embed = discord.Embed(
		title="🧹 Messages Cleared",
		description=
		f"Deleted **{len(deleted)}** messages in {interaction.channel.mention}",
		color=discord.Color.green())
	await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="pokemon",
					description="Get complete details about a Pokémon by name")
@app_commands.describe(name="Enter the Pokémon name")
async def pokemon(interaction: discord.Interaction, name: str):
	url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
	response = requests.get(url)

	if response.status_code == 200:
		data = response.json()

		# Extract info
		pokemon_name = data["name"].capitalize()
		pokemon_id = data["id"]
		types = ", ".join(
			[t["type"]["name"].capitalize() for t in data["types"]])
		abilities = ", ".join([
			a["ability"]["name"].replace('-', ' ').capitalize()
			for a in data["abilities"]
		])
		height = data["height"] / 10  # Convert to meters
		weight = data["weight"] / 10  # Convert to kg
		base_experience = data["base_experience"]

		# Base Stats
		stats = {
			s["stat"]["name"].capitalize(): s["base_stat"]
			for s in data["stats"]
		}

		# Sprites
		sprite_url = data["sprites"]["front_default"]
		shiny_sprite_url = data["sprites"]["front_shiny"]

		# Create Embed
		embed = discord.Embed(
			title=f"🐉 Pokémon: {pokemon_name} (#{pokemon_id})",
			color=discord.Color.blue())
		embed.set_thumbnail(url=sprite_url)

		embed.add_field(name="Type(s)", value=types, inline=True)
		embed.add_field(name="Abilities", value=abilities, inline=True)
		embed.add_field(name="Height", value=f"{height} m", inline=True)
		embed.add_field(name="Weight", value=f"{weight} kg", inline=True)
		embed.add_field(name="Base XP",
						value=str(base_experience),
						inline=True)

		# Add Stats
		stats_text = "\n".join(
			[f"**{stat}:** {value}" for stat, value in stats.items()])
		embed.add_field(name="Base Stats", value=stats_text, inline=False)

		# Shiny Sprite
		embed.set_image(url=shiny_sprite_url)

		await interaction.response.send_message(embed=embed)

	else:
		await interaction.response.send_message(
			"❌ Pokémon not found! Please check the name.", ephemeral=True)


# 🐱 Cat Image
@bot.tree.command(name="cat", description="Get a random cat image")
async def cat(interaction: discord.Interaction):
	headers = {"x-api-key": CAT_API_KEY}
	data = fetch_data("https://api.thecatapi.com/v1/images/search",
						headers=headers)

	if data:
		embed = discord.Embed(title="🐱 Meow!", color=discord.Color.orange())
		embed.set_image(url=data[0]["url"])
		await interaction.response.send_message(embed=embed)
	else:
		await interaction.response.send_message(
			"❌ Could not fetch a cat image!", ephemeral=True)


# 🖼 Meme Command
@bot.tree.command(name="meme", description="Get a random meme")
async def meme(interaction: discord.Interaction):
	data = fetch_data("https://meme-api.com/gimme")

	if data:
		embed = discord.Embed(title=data["title"],
								color=discord.Color.random())
		embed.set_image(url=data["url"])
		await interaction.response.send_message(embed=embed)
	else:
		await interaction.response.send_message("❌ Could not fetch a meme!",
												ephemeral=True)


# 🐶 Dog Image
@bot.tree.command(name="dog", description="Get a random dog image")
async def dog(interaction: discord.Interaction):
	data = fetch_data("https://dog.ceo/api/breeds/image/random")

	if data:
		embed = discord.Embed(title="🐶 Woof!", color=discord.Color.green())
		embed.set_image(url=data["message"])
		await interaction.response.send_message(embed=embed)
	else:
		await interaction.response.send_message(
			"❌ Could not fetch a dog image!", ephemeral=True)


# 🦊 Fox Image
@bot.tree.command(name="fox", description="Get a random fox image")
async def fox(interaction: discord.Interaction):
	data = fetch_data("https://randomfox.ca/floof/")

	if data:
		embed = discord.Embed(title="🦊 Here's a cute fox!",
								color=discord.Color.red())
		embed.set_image(url=data["image"])
		await interaction.response.send_message(embed=embed)
	else:
		await interaction.response.send_message(
			"❌ Could not fetch a fox image!", ephemeral=True)


# 🎭 Random Advice
@bot.tree.command(name="advice", description="Get a random life advice")
async def advice(interaction: discord.Interaction):
	data = fetch_data("https://api.adviceslip.com/advice")

	if data:
		embed = discord.Embed(title="💡 Life Advice",
								description=data["slip"]["advice"],
								color=discord.Color.teal())
		await interaction.response.send_message(embed=embed)
	else:
		await interaction.response.send_message("❌ Could not fetch advice!",
												ephemeral=True)


# 🤓 Fun Fact
@bot.tree.command(name="fact", description="Get a random fun fact")
async def fact(interaction: discord.Interaction):
	data = fetch_data("https://uselessfacts.jsph.pl/random.json?language=en")

	if data:
		embed = discord.Embed(title="🧠 Fun Fact",
								description=data["text"],
								color=discord.Color.purple())
		await interaction.response.send_message(embed=embed)
	else:
		await interaction.response.send_message("❌ Could not fetch a fact!",
												ephemeral=True)


# 🔥 Funny Insult
@bot.tree.command(name="insult",
					description="Roast someone with a funny insult")
@app_commands.describe(user="Who do you want to roast?")
async def insult(interaction: discord.Interaction, user: discord.Member):
	data = fetch_data(
		"https://evilinsult.com/generate_insult.php?lang=en&type=json")

	if data:
		embed = discord.Embed(title="🔥 Roast Cooking!",
								description=f"{user.mention}, {data['insult']}",
								color=discord.Color.red())
		await interaction.response.send_message(embed=embed)
	else:
		await interaction.response.send_message("❌ Could not fetch an insult!",
												ephemeral=True)


# 💖 Random Waifu
@bot.tree.command(name="waifu", description="Get a random anime waifu image")
async def waifu(interaction: discord.Interaction):
	headers = {"x-api-key": WAIFU_API_KEY}
	data = fetch_data("https://api.waifu.pics/sfw/waifu", headers=headers)

	if data:
		embed = discord.Embed(title="💖 Here is your waifu degenerate!",
								color=discord.Color.pink())
		embed.set_image(url=data["url"])
		await interaction.response.send_message(embed=embed)
	else:
		await interaction.response.send_message(
			"❌ Could not fetch a waifu image!", ephemeral=True)

	@bot.tree.command(
		name="define",
		description="Get the meaning of a word from Urban Dictionary")
	@app_commands.describe(word="Enter the word to search")
	async def define(interaction: discord.Interaction, word: str):
		url = f"https://api.urbandictionary.com/v0/define?term={word}"
		response = requests.get(url).json()

		if response["list"]:
			definition = response["list"][0]["definition"]
			embed = discord.Embed(title=f"📖 Definition of {word}",
									description=definition,
									color=discord.Color.blue())
			await interaction.response.send_message(embed=embed)
		else:
			await interaction.response.send_message("❌ No definition found!",
													ephemeral=True)


@bot.tree.command(name="joke", description="Get a random joke")
async def joke(interaction: discord.Interaction):
	url = "https://official-joke-api.appspot.com/jokes/random"
	response = requests.get(url).json()
	joke_text = f"{response['setup']}\n\n**{response['punchline']}**"

	embed = discord.Embed(title="😂 Random Joke",
							description=joke_text,
							color=discord.Color.gold())
	await interaction.response.send_message(embed=embed)


@bot.tree.command(name="quote", description="Get an inspirational quote")
async def quote(interaction: discord.Interaction):
	url = "https://api.quotable.io/random"
	response = requests.get(url).json()
	quote_text = f"_{response['content']}_\n- **{response['author']}**"

	embed = discord.Embed(title="🌟 Inspirational Quote",
							description=quote_text,
							color=discord.Color.green())
	await interaction.response.send_message(embed=embed)


@bot.tree.command(name="news",
					description="Get the latest tech news (No API key required)")
async def news(interaction: discord.Interaction):
	url = "https://hacker-news.firebaseio.com/v0/topstories.json"

	try:
		story_ids = requests.get(url).json()[:1]  # Get the top 1 news ID
		if not story_ids:
			await interaction.response.send_message("❌ No news found!",
													ephemeral=True)
			return

		story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_ids[0]}.json"
		story = requests.get(story_url).json()

		embed = discord.Embed(title=story.get("title", "No Title Available"),
								url=story.get("url",
											"https://news.ycombinator.com"),
								color=discord.Color.orange())

		await interaction.response.send_message(embed=embed)

	except requests.exceptions.RequestException as e:
		await interaction.response.send_message(
			f"❌ Error fetching news: {str(e)}", ephemeral=True)


CRYPTO_API_URL = "https://api.coingecko.com/api/v3/simple/price"


@bot.tree.command(name="crypto",
					description="Get the current price of a cryptocurrency")
@app_commands.describe(
	symbol="Enter the cryptocurrency symbol (e.g., Bitcoin, litecoint, etc.)")
async def crypto(interaction: discord.Interaction, symbol: str):
	try:
		symbol = symbol.lower(
		)  # Convert to lowercase (API uses lowercase symbols)
		params = {"ids": symbol, "vs_currencies": "usd"}
		response = requests.get(CRYPTO_API_URL, params=params)
		data = response.json()

		if symbol not in data:
			await interaction.response.send_message(
				"❌ Invalid cryptocurrency symbol!", ephemeral=True)
			return

		price = data[symbol]["usd"]
		embed = discord.Embed(title=f"💰 Cryptocurrency Price",
								color=discord.Color.gold())
		embed.add_field(name="Symbol", value=symbol.upper(), inline=True)
		embed.add_field(name="Price (USD)",
						value=f"${price:,.2f}",
						inline=True)

		await interaction.response.send_message(embed=embed)

	except Exception as e:
		await interaction.response.send_message(
			f"❌ Error fetching data: {str(e)}", ephemeral=True)


@bot.tree.command(name="anime",
					description="Get a random anime recommendation")
async def anime(interaction: discord.Interaction):
	url = "https://api.jikan.moe/v4/random/anime"
	response = requests.get(url).json()

	title = response["data"]["title"]
	synopsis = response["data"]["synopsis"][:500] + "..."  # Limit text length
	image = response["data"]["images"]["jpg"]["image_url"]
	url = response["data"]["url"]

	embed = discord.Embed(title=f"🎥 {title}",
							description=synopsis,
							url=url,
							color=discord.Color.orange())
	embed.set_image(url=image)
	await interaction.response.send_message(embed=embed)


@bot.tree.command(name="translate",
					description="Translate text to a different language")
@app_commands.describe(
	text="The text to translate",
	target_language="Language to translate to (e.g., en, es, fr)")
async def translate(interaction: discord.Interaction, text: str,
					target_language: str):
	try:
		# Detect source language
		detected_lang = translator.detect(text).lang

		# Translate the text
		translated_text = translator.translate(text, dest=target_language).text

		# Create an embed response
		embed = discord.Embed(title="Translation", color=discord.Color.blue())
		embed.add_field(name="Original Text", value=text, inline=False)
		embed.add_field(name="Detected Language",
						value=detected_lang,
						inline=True)
		embed.add_field(name="Translated Text",
						value=translated_text,
						inline=False)
		embed.add_field(name="Target Language",
						value=target_language,
						inline=True)

		await interaction.response.send_message(embed=embed)

	except Exception as e:
		await interaction.response.send_message(
			f"❌ Error translating text: {str(e)}", ephemeral=True)


@bot.tree.command(name="movie", description="Get information about a movie")
@app_commands.describe(name="Enter the movie name")
async def movie(interaction: discord.Interaction, name: str):
	url = f"http://www.omdbapi.com/?t={name}&apikey=6d8436f1"
	response = requests.get(url).json()

	if response["Response"] == "True":
		embed = discord.Embed(title=response["Title"],
								description=response["Plot"],
								color=discord.Color.blue())
		embed.set_thumbnail(url=response["Poster"])
		embed.add_field(name="🎬 Genre", value=response["Genre"], inline=True)
		embed.add_field(name="⭐ IMDb Rating",
						value=response["imdbRating"],
						inline=True)
		embed.add_field(name="🎭 Actors",
						value=response["Actors"],
						inline=False)
		await interaction.response.send_message(embed=embed)
	else:
		await interaction.response.send_message("❌ Movie not found!",
												ephemeral=True)


@bot.tree.command(name="reddit", description="Get a top post from a subreddit")
@app_commands.describe(subreddit="Enter the subreddit name")
async def reddit(interaction: discord.Interaction, subreddit: str):
	url = f"https://meme-api.com/gimme/{subreddit}"
	response = requests.get(url).json()

	if "url" in response:
		embed = discord.Embed(title=response["title"],
								url=response["postLink"],
								color=discord.Color.red())
		embed.set_image(url=response["url"])
		await interaction.response.send_message(embed=embed)
	else:
		await interaction.response.send_message("❌ Subreddit not found!",
												ephemeral=True)


@bot.tree.command(name="unban", description="Unban a member from the server")
@app_commands.describe(user="The user to unban (provide their ID)")
async def unban(interaction: discord.Interaction, user: int):
	# Ensure the user has the necessary permissions to unban
	if not interaction.user.guild_permissions.ban_members:
		await interaction.response.send_message(
			"❌ You do not have permission to unban members.", ephemeral=True)
		return

	# Attempt to unban the user
	try:
		banned_users = await interaction.guild.bans()
		user_to_unban = discord.utils.get(banned_users, user_id=user)

		if user_to_unban:
			await interaction.guild.unban(user_to_unban.user)
			await interaction.response.send_message(
				f"✅ Successfully unbanned {user_to_unban.user.name}#{user_to_unban.user.discriminator}."
			)
		else:
			await interaction.response.send_message(
				f"❌ No user found with ID {user}.", ephemeral=True)

	except discord.DiscordException as e:
		await interaction.response.send_message(f"❌ Error: {str(e)}",
												ephemeral=True)


@bot.tree.command(name="addbadword", description="Add a bad word to the list")
@app_commands.describe(word="The bad word to add to the list")
async def addbadword(interaction: discord.Interaction, word: str):
	conn = sqlite3.connect('bad_words.db')
	c = conn.cursor()

	try:
		c.execute("INSERT INTO bad_words (word) VALUES (?)", (word, ))
		conn.commit()
		await interaction.response.send_message(
			f"✅ '{word}' has been added to the list of bad words.",
			ephemeral=True)
	except sqlite3.IntegrityError:
		await interaction.response.send_message(
			f"❌ '{word}' is already in the list.", ephemeral=True)
	finally:
		conn.close()

# Create the SQLite database

# Command to add bad words


# Listener to check for bad words and issue warnings
@bot.event
async def on_message(message):
	if message.author.bot:
		return

	conn = sqlite3.connect('bad_words.db')
	c = conn.cursor()

	c.execute("SELECT word FROM bad_words")
	bad_words = [row[0] for row in c.fetchall()]

	for word in bad_words:
		if word.lower() in message.content.lower():
			c.execute(
				"SELECT warning_count FROM user_warnings WHERE user_id = ?",
				(message.author.id, ))
			result = c.fetchone()

			if result:
				warning_count = result[0] + 1
				c.execute(
					"UPDATE user_warnings SET warning_count = ? WHERE user_id = ?",
					(warning_count, message.author.id))
			else:
				warning_count = 1
				c.execute(
					"INSERT INTO user_warnings (user_id, warning_count) VALUES (?, ?)",
					(message.author.id, warning_count))

			conn.commit()
			await message.channel.send(
				f"{message.author.mention} has been warned for using a bad word. Warning #{warning_count}"
			)
			break

	conn.close()
	await bot.process_commands(message)


# Command to view a user's warnings
@bot.tree.command(name="warns", description="View the warnings of a user")
@app_commands.describe(user="The user to check warnings for")
async def warns(interaction: discord.Interaction, user: discord.User):
	conn = sqlite3.connect('bad_words.db')
	c = conn.cursor()

	c.execute("SELECT warning_count FROM user_warnings WHERE user_id = ?",
				(user.id, ))
	result = c.fetchone()

	if result:
		await interaction.response.send_message(
			f"{user.mention} has {result[0]} warnings.", ephemeral=True)
	else:
		await interaction.response.send_message(
			f"{user.mention} has no warnings.", ephemeral=True)

	conn.close()


	# Command for moderators/admins to manually issue warnings
@bot.tree.command(name="issuewarning",
					description="Manually issue a warning to a user")
@app_commands.describe(user="The user to warn")
async def issuewarning(interaction: discord.Interaction, user: discord.User):
	# Check if the user has the required permissions (e.g., 'ban_members' permission)
	if not interaction.user.guild_permissions.ban_members:
		await interaction.response.send_message(
			"❌ You don't have the required permissions to issue warnings.",
			ephemeral=True)
		return

	conn = sqlite3.connect('bad_words.db')
	c = conn.cursor()

	c.execute("SELECT warning_count FROM user_warnings WHERE user_id = ?",
				(user.id, ))
	result = c.fetchone()

	if result:
		warning_count = result[0] + 1
		c.execute(
			"UPDATE user_warnings SET warning_count = ? WHERE user_id = ?",
			(warning_count, user.id))
	else:
		warning_count = 1
		c.execute(
			"INSERT INTO user_warnings (user_id, warning_count) VALUES (?, ?)",
			(user.id, warning_count))

	conn.commit()
	await interaction.response.send_message(
		f"✅ {user.mention} has been warned. Current warning count: {warning_count}",
		ephemeral=True)

	conn.close()


@bot.tree.command(name="warnings", description="View the warnings of a user")
@app_commands.describe(user="The user to check warnings for")
async def warnings(interaction: discord.Interaction, user: discord.User):
	conn = sqlite3.connect('bad_words.db')
	c = conn.cursor()

	# Fetch the user's warning count
	c.execute("SELECT warning_count FROM user_warnings WHERE user_id = ?",
				(user.id, ))
	result = c.fetchone()

	if result:
		await interaction.response.send_message(
			f"{user.mention} has {result[0]} warnings.", ephemeral=True)
	else:
		await interaction.response.send_message(
			f"{user.mention} has no warnings.", ephemeral=True)

	conn.close()


@bot.tree.command(name="clearwarnings",
					description="Clear all warnings for a user")
@app_commands.describe(user="The user whose warnings you want to clear")
async def clearwarnings(interaction: discord.Interaction, user: discord.User):
	# Check if the command user has moderator permissions
	if not interaction.user.guild_permissions.ban_members:
		await interaction.response.send_message(
			"❌ You don't have permission to clear warnings.", ephemeral=True)
		return

	conn = sqlite3.connect('bad_words.db')
	c = conn.cursor()

	# Check if the user has warnings
	c.execute("SELECT warning_count FROM user_warnings WHERE user_id = ?",
				(user.id, ))
	result = c.fetchone()

	if result:
		# Delete the warnings
		c.execute("DELETE FROM user_warnings WHERE user_id = ?", (user.id, ))
		conn.commit()
		await interaction.response.send_message(
			f"✅ All warnings for {user.mention} have been cleared.",
			ephemeral=True)
	else:
		await interaction.response.send_message(
			f"ℹ️ {user.mention} has no warnings.", ephemeral=True)

	conn.close()


DATABASE = "moderation.db"


# Function to get all bad words
def get_bad_words():
	conn = sqlite3.connect(DATABASE)
	cursor = conn.cursor()
	cursor.execute("SELECT word FROM bad_words")
	words = [row[0] for row in cursor.fetchall()]
	conn.close()
	return words


# Function to remove a bad word
def remove_bad_word(word):
	conn = sqlite3.connect(DATABASE)
	cursor = conn.cursor()
	cursor.execute("DELETE FROM bad_words WHERE word = ?", (word, ))
	conn.commit()
	deleted = cursor.rowcount  # Check if a row was deleted
	conn.close()
	return deleted > 0


# Command to list all bad words
@bot.tree.command(name="listbadwords",
					description="Shows all bad words stored in the database")
async def list_badwords(interaction: discord.Interaction):
	bad_words = get_bad_words()

	if not bad_words:
		await interaction.response.send_message("✅ No bad words are stored!",
												ephemeral=True)
		return

	embed = discord.Embed(title="🚨 Blocked Words",
							description="\n".join(bad_words),
							color=discord.Color.red())
	await interaction.response.send_message(embed=embed)


# Command to remove a bad word
@bot.tree.command(name="removebadword",
					description="Removes a bad word from the database")
@app_commands.describe(
	word="The word you want to remove from the bad words list")
async def remove_badword(interaction: discord.Interaction, word: str):
	if remove_bad_word(word):
		await interaction.response.send_message(
			f"✅ Removed `{word}` from the bad words list.", ephemeral=True)
	else:
		await interaction.response.send_message(
			f"❌ `{word}` was not found in the bad words list.", ephemeral=True)






	bot.add_cog(Utility(bot))


@bot.command()
async def sync(ctx):
	await bot.tree.sync()
	await ctx.send("✅ Slash commands synced!")



@bot.event
async def on_ready():
	try:
		await bot.tree.sync()
		print("✅ Slash commands synced!")
	except Exception as e:
		print(f"❌ Error syncing commands: {e}")

bot.run(TOKEN)
