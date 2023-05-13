import discord
import re

import config
from room import Room
from util import Singleton


class MissingChannelError(Exception):
	pass

@Singleton
class Rooms:
	def __init__(self):
		self.rooms = {}

	def add_channel(self, channel):
		if channel.id not in self.rooms:
			room = Room(channel.name, playing_role_in_channel(channel), channel)
			self.rooms[channel.id] = room
			room.sync_players()

def here(ctx):
	try:
		return Rooms.get().rooms[ctx.channel.id]
	except KeyError:
		print(f"Initializing {ctx.channel} in {ctx.channel.guild}")
		Rooms.get().add_channel(ctx.channel)
		raise MissingChannelError(f"Channel {ctx.channel} is not initialized. Probably just wait a few seconds...")

def playing_role_in_channel(channel):
	""" Returns the role for players in the given channel. May return None if no role is configured on the server or for this bot instance. """
	channel_name = channel.name

	# To extend the map like "shibboleth-game2" -> "Playing2", chop off a  numerical suffix.
	channel_name_split = re.match(r"(?P<prefix>[^0-9]*)(?P<suffix>.*)$", channel_name)

	channel_name_prefix = channel_name_split.group('prefix')
	suffix = channel_name_split.group('suffix')

	role_prefix = config.playing_roles_in_channels.get(channel_name_prefix, config.misc_playing_role)
	role_name = role_prefix + suffix

	role = discord.utils.get(channel.guild.roles, name=role_name) if role_name else None

	return role

def link_to_channel(channel):
	return f"<https://discord.com/channels/{channel.guild.id}/{channel.id}>"


