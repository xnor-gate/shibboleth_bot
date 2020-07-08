import traceback

import discord
from discord.ext.commands import Bot

from help import Help
from lobby import Lobby
from options import Options
from room import RoomError
from rooms import ROOMS, MissingChannelError
from round import Round
from server import Server
from shibboleth import GameActionError, GameInitializationError
from status import Status
from help_command import CommandError

BOT_PREFIX = "!"  # Hardcoded in many user-facing strings, so if you change this you'll want to change those too
bot = Bot(command_prefix=BOT_PREFIX, case_insensitive=True, help_command=None)

COGS = [Lobby(bot), Round(bot), Help(bot), Status(bot), Options(bot), Server(bot)]

for cog in COGS:
	bot.add_cog(cog)

for command in bot.walk_commands():
	command.ignore_extra = False

@bot.event
async def on_command_error(ctx, exception):
	orig_exception = exception.__cause__
	message = ctx.message.content

	if "<@" in message:
		command_info = ""
	else:
		command_info = f" on `{ctx.message.content}`"

	if isinstance(orig_exception, (GameActionError, RoomError, GameInitializationError, MissingChannelError)):
		exception_name = type(orig_exception).__name__
		error_message = f"{ctx.author.mention} {exception_name}{command_info}: {orig_exception}"
	elif isinstance(orig_exception, CommandError):
		error_message = f"{ctx.author.mention} Failed{command_info}: {orig_exception}"
	else:
		error_message = f"{ctx.author.mention} Failed{command_info}: {exception}"

	if orig_exception is not None:
		traceback.print_exception(type(orig_exception), orig_exception, orig_exception.__traceback__)
	await ctx.send(error_message)

@bot.event
async def on_message_edit(_before, after):
	await bot.process_commands(after)

async def initialize_channel(channel):
	assert channel is not None, "None channel"
	print(f"Initializing {channel} in {channel.guild}")

	ROOMS.add_channel(channel)


@bot.event
async def on_ready():
	print(f"Logged in as {bot.user.name}")
	await bot.change_presence(activity=discord.Activity(name="Shibboleth (!h for help)", type=1, url="https://github.com/xnor-gate/shibboleth_bot/blob/master/README.md"))

	for channel in bot.get_all_channels():
		# Since we're also getting channels the bot can't actually read, skip over these.
		bot_member = channel.guild.me
		bot_can_read = channel.permissions_for(bot_member).read_messages
		if not bot_can_read:
			continue

		if channel.type == discord.ChannelType.text:
			await initialize_channel(channel)

def read_token():
	"""Reads the token from a file that's not committed on GitHub for security."""
	with open("config/token.txt", "r") as f:
		return f.readline()

if __name__ == "__main__":
	print("Starting up bot...")
	bot.run(read_token())
