import discord

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

def playing_role_in_channel(channel):
	channel_name = channel.name
	if "shibboleth-game" in channel_name:
		suffix = channel_name[len("shibboleth-game"):]
		role_name = "Playing" + suffix
	elif "shibboleth-pictures" in channel_name:
		suffix = channel_name[len("shibboleth-pictures"):]
		role_name = "PlayingPics" + suffix
	elif "bot-testing" in channel_name:
		suffix = channel_name[len("bot-testing"):]
		role_name = "Testing" + suffix
	else:
		role_name = "Misc"

	role = discord.utils.get(channel.guild.roles, name=role_name)

	assert role is not None, f"Can't find role {role_name} for channel {channel}"
	return role
