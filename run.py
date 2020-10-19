import argparse
import config
import discord

from my_bot import MyBot

if __name__ == "__main__":
	print(f"Running discord.py version {discord.__version__}")

	parser = argparse.ArgumentParser(description='Run the Shibboleth Discord bot.')
	parser.add_argument('--config', dest="config", default="shib",
		help="yaml configuration file to use, e.g. --config=dev uses ./config/dev.yaml (default: shib)")
	args = parser.parse_args()

	config.init(args.config)

	print("Making bot...")
	bot = MyBot()

	# Reads the token from a file that's not committed on GitHub for security.
	with open("config/token.txt", "r") as f:
		token = f.readline()

	print("Initializing bot...")
	bot.run(token)
	print("Bot is ready")
