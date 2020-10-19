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


class MyBot(Bot):
	"""
	Creates a custom bot (client) with custom event listeners.
	"""
	def __init__(self):
		Bot.__init__(self, command_prefix=config.bot_prefix, help_command=None)

		for cog_class in [Lobby, Round, Help, Status, Options, Server]:
			self.add_cog(cog_class(self))

		# Make all commands not silently truncate up to the last valid argument
		for command in self.walk_commands():
			command.ignore_extra = False

		# Make commands case-insensitive
		self.case_insensitive = True

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

		if orig_exception is not None:
			traceback.print_exception(type(orig_exception), orig_exception, orig_exception.__traceback__)
		await ctx.send(error_message)

	# Make the bot pick up on commands in edited messages
	async def on_message_edit(self, _before, after):
		await self.on_message(after)

	# Do additional processing on messages before scanning them for commands
	async def on_message(self, message):
		# Ignore messages sent by the bot itself
		if message.author == self.user:
			return

		def remove_parenthetical_asides(text):
			"""Remove parts inside parens, including the parens themselves, matching minimally. For example, 'a(bc)de(f)g' goes to 'adeg'. Then, remove leading and trailing whitespace."""
			return re.sub(r'\([^\)]*\)', '', text).strip()

		message.content = remove_parenthetical_asides(message.content)
		await self.process_commands(message)

	async def on_ready(self):
		print(f"Logged in as {self.user.name}")
		await self.change_presence(activity=discord.Game(name="Shibboleth (!h for help)"))
		await self.initialize_all_channels()
		print("Initialization complete\n")

	async def initialize_channels_in_guild(self, guild):
		for channel in guild.channels:
			# Skip over any channel the bot can't read, since we're getting these channels too
			if not channel.permissions_for(channel.guild.me).read_messages:
				continue

			# Skip over non-text channels. These include voice channels and DM channels.
			if channel.type != discord.ChannelType.text:
				continue

			Rooms.get().add_channel(channel)

	async def initialize_all_channels(self):
		for guild in self.guilds:
			print(f"Initializizing {guild.name}")
			await self.initialize_channels_in_guild(guild)

	async def on_guild_channel_delete(self, channel):
		Rooms.get().remove_channel(channel)
