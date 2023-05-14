import typing

import discord
from discord.ext import commands

from check import no_dm_predicate
from rooms import here, Rooms


class Lobby(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def cog_check(self, ctx):
		return no_dm_predicate(ctx)

	@commands.command(
		brief="Mark yourself or others as playing",
		description="Mark yourself as playing. Or, call with one or more usernames space-separated to mark them as playing. Joining a game doesn't automatically unjoin you from other games; you have to unjoin there yourself.",
		aliases=["j"],
	)
	async def join(self, ctx, *members: discord.Member):
		if not members:
			members = (ctx.author,)

		room = here(ctx)

		for member in members:
			current_players = room.room_players

			if member.bot:
				await ctx.send(f"{ctx.author.mention} {member.display_name} is a bot.")
			elif room.in_round and (member in room.queued_leavers):
				room.remove_member_from_leaver_queue(member)
				await ctx.send(f"{member.mention} will no longer leave after this round.")
			elif member in current_players:
				await ctx.send(f"{ctx.author.mention} {member.display_name} was already playing.")
			elif room.in_round:
				await ctx.send(f"{member.mention} will join and be pinged after this round ends.")
				room.add_member_to_joiner_queue(member)
			else:
				room.add_player(member)
				if room.playing_role is not None:
					try:
						await member.add_roles(room.playing_role)
					except discord.errors.Forbidden:
						pass
				await ctx.send(f"{member.mention} is now playing")

				# Automatically unjoin other channels one is joined in or queued in.
				# Currently a player can join another channel while in an ongoing game, and only be queued to leave. Maybe should change to disallow joining in that circumstance.
				await self.unjoin_other_rooms_in_server(member, ctx)

	@commands.command(
		brief="Mark yourself or others as not playing",
		description="Mark yourself as not playing. Or, call with one or more usernames space-separated to mark them as not playing. Call with this room's @Playing role to remove all players.",
		aliases=["uj"],
	)
	async def unjoin(self, ctx, *members: typing.Union[discord.Member, discord.Role]):
		if not members:
			members = (ctx.author,)

		playing_role = here(ctx).playing_role

		for member_or_role in members:
			if isinstance(member_or_role, discord.Role):
				if member_or_role == playing_role:
					players_here = list(here(ctx).room_players)
					for player in players_here:
						await self.remove_player(ctx, player)
				else:
					raise commands.CheckFailure(f"Cannot remove `{member_or_role.name}`. Must be the current room's player role `{playing_role.name}`.")
			elif isinstance(member_or_role, discord.Member):
				await self.remove_player(ctx, member_or_role)
			else:
				raise commands.CheckFailure(f"`{member_or_role}` is neither a member not a role.")

	async def remove_player(self, ctx, member, reason=None):
		room = here(ctx)
		playing_role = here(ctx).playing_role

		if reason is not None:
			reason_str = f" ({reason})"
		else:
			reason_str = ""

		if room.in_round and (member in room.game.players):
			await ctx.send(f"{member.display_name} will leave after this round finishes{reason_str}.")
			room.add_member_to_leaver_queue(member)
		elif room.in_round and (member in room.queued_joiners):
			room.remove_member_from_joiner_queue(member)
			await ctx.send(f"{member.display_name} will no longer join after this round{reason_str}.")
		elif member in room.room_players:
			room.remove_player(member)
			await ctx.send(f"{member.display_name} is no longer playing{reason_str}.")

			if playing_role:
				try:
					await member.remove_roles(room.playing_role)
				except discord.errors.Forbidden:
					pass
		else:
			await ctx.send(f"{ctx.author.mention} {member.display_name} was already not playing.")

	async def unjoin_other_rooms_in_server(self, player, ctx):
		my_channel = ctx.channel
		my_guild = ctx.guild

		for channel in my_guild.channels:
			if channel == my_channel:
				continue

			try:
				other_room = Rooms.get().get_channel(channel)
			except KeyError:
				continue

			other_channel = other_room.channel
			if (player in other_room.room_players) or (player in other_room.queued_joiners):
				# Mutating ctx, be careful
				ctx.channel = other_channel
				await self.remove_player(ctx, player, f"joined {my_channel.mention}")

	@commands.command(
		brief="Start a new round with the joined players",
		description="Start a new round with the players who joined. Any players who were in last game will be included unless they have unjoined.",
		aliases=["s"],
	)
	async def start(self, ctx):
		await self.bot.get_cog("Round").start_round(ctx)

	async def resolve_joiner_queue(self, ctx):
		room = here(ctx)
		if room.queued_joiners:
			await self.join(ctx, *room.queued_joiners)

	async def resolve_leaver_queue(self, ctx):
		room = here(ctx)
		if room.queued_leavers:
			await self.unjoin(ctx, *room.queued_leavers)
