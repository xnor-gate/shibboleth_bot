import re
import traceback

import discord
from discord.ext.commands import Bot

import config
from help import Help
from help_command import CommandError
from lobby import Lobby
from options import Options
from room import RoomError
from rooms import MissingChannelError, Rooms
from round import Round
from server import Server
from shibboleth import GameActionError, GameInitializationError
from status import Status

from datetime import datetime

from sys import stderr

class MyBot(Bot):
	"""
	Creates a custom bot (client) with custom event listeners.
	"""
	def __init__(self):
		command_prefix = discord.ext.commands.when_mentioned_or(config.bot_prefix)
		activity = discord.Game(name="Shibboleth (!h for help)")

		intents = discord.Intents.default()

		# Be able to read messages to process commands
		intents.message_content = True

		# The members intent is used solely in sync_players when the bot starts to mark everyone with the playing role as playing. This is useful is the bot restarts in the middle of some games.
		intents.members = True

		Bot.__init__(self, command_prefix=command_prefix, help_command=None, activity=activity, case_insensitive=True, intents=intents)

		# Make all commands not silently truncate up to the last valid argument
		for command in self.walk_commands():
			command.ignore_extra = False

	# Logs commands for debugging. TODO: actually log.
	async def on_command(self, ctx):
		now = datetime.now()
		dt_string = now.strftime("%Y %b %d %H:%M:%S")

		guild = ctx.guild
		guild_name = guild.name if (guild is not None) else None
		channel_name = ctx.channel.name
		author_name = ctx.author.name
		message = f"{dt_string}: Command \"{ctx.command}\" run in guild {guild_name}, channel {channel_name} by {author_name} (message: {ctx.message.content})."
		print(message)

	# When a command fails, display information about the error in the Discord channel
	async def on_command_error(self, ctx, exception):
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

		await ctx.send(error_message)

		if (orig_exception is not None) and not isinstance(orig_exception, (GameActionError, RoomError, GameInitializationError)):
			extended_error_message = f"{ctx.author.name} in guild {ctx.guild.name}, channel {ctx.channel.name}\nFailed{command_info}: {exception}"
			print(extended_error_message, file=stderr)
			traceback.print_exception(type(orig_exception), orig_exception, orig_exception.__traceback__)

	# Make the bot pick up on commands in edited messages
	async def on_message_edit(self, _before, after):
		await self.on_message(after)

	# Do additional processing on messages before scanning them for commands
	async def on_message(self, message):
		# Ignore messages sent by this bot or any other bot
		if message.author.bot:
			return

		def remove_parenthetical_asides(text):
			"""Remove parts inside parens, including the parens themselves, matching minimally. For example, 'a(bc)de(f)g' goes to 'adeg'. Then, remove leading and trailing whitespace."""
			return re.sub(r'\([^\)]*\)', '', text).strip()

		message.content = remove_parenthetical_asides(message.content)

		# Ignore commands that consist solely of exclamation or contain a question mark
		if (set(message.content) <= {"!"}) or ("?" in message.content):
			return

		await self.process_commands(message)

	async def on_ready(self):
		print(f"Logged in as {self.user.name}")
		for cog_class in [Lobby, Round, Help, Status, Options, Server]:
			await self.add_cog(cog_class(self))

		await self.initialize_all_channels()
		print("\nInitialization complete\n")

	async def initialize_channels_in_guild(self, guild):
		for channel in guild.text_channels:
			# Skip over any channel the bot can't read, since we're getting these channels too
			if not channel.permissions_for(channel.guild.me).read_messages:
				continue

			Rooms.get().add_channel(channel)

	async def initialize_all_channels(self):
		for guild in self.guilds:
			print(f"Initializing {guild.name} ({guild.id})")
			await self.initialize_channels_in_guild(guild)

	async def on_guild_channel_delete(self, channel):
		Rooms.get().remove_channel(channel)
