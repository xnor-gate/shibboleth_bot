import discord
import re

from room import Room


class MissingChannelError(Exception):
	pass

class Rooms:
	def __init__(self):
		self.rooms = {}

	def add_channel(self, channel):
		if channel.id not in self.rooms:
			room = Room(channel.name, playing_role_in_channel(channel), channel)
			self.rooms[channel.id] = room
			room.sync_players()

ROOMS = Rooms()

def get_id(ctx):
	return ctx.channel.id

def here(ctx):
	try:
		return ROOMS.rooms[ctx.channel.id]
	except KeyError:
		raise MissingChannelError(f"Channel {ctx.channel} is not initialized. Probably just wait a few seconds...")

PLAYING_ROLES_IN_CHANNELS = {
	"shibboleth-game": "Playing",
	"shibboleth-pictures": "PlayingPics",
	"bot-testing": "Testing",
}

def playing_role_in_channel(channel):
	channel_name = channel.name

	channel_name_split = re.match(r"(?P<prefix>[^0-9]*)(?P<suffix>.*)$", channel_name)

	channel_name_prefix = channel_name_split.group('prefix')
	suffix = channel_name_split.group('suffix')

	role_prefix = PLAYING_ROLES_IN_CHANNELS.get(channel_name_prefix, "Shibboleth")
	role_name = role_prefix + suffix

	role = discord.utils.get(channel.guild.roles, name=role_name)

	assert role is not None, f"Can't find role {role_name} for channel {channel}. If needed, make a role with that name, or modify the PLAYING_ROLES_IN_CHANNELS dictionary in the code."
	return role
