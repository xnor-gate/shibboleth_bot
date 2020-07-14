import typing

import discord
from discord.ext import commands

from check import no_dm_predicate
from rooms import here


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
				if room.playing_role:
					await member.add_roles(room.playing_role)
				await ctx.send(f"{member.mention} is now playing")

	@commands.command(
		brief="Mark yourself or others as not playing",
		description="Mark yourself as not playing. Or, call with one or more usernames space-separated to mark them as not playing. Call with this room's @Playing role to remove all players.",
		aliases=["uj"],
	)
	async def unjoin(self, ctx, *members: typing.Union[discord.Member, discord.Role]):
		if not members:
			members = (ctx.author,)

		playing_role = here(ctx).playing_role

		async def remove_player(member):
			room = here(ctx)
			if room.in_round and (member in room.game.players):
				await ctx.send(f"{member.mention} will leave after this round finishes.")
				room.add_member_to_leaver_queue(member)
			elif room.in_round and (member in room.queued_joiners):
				room.remove_member_from_joiner_queue(member)
				await ctx.send(f"{member.mention} will no longer join after this round.")
			elif member in room.room_players:
				room.remove_player(member)
				await ctx.send(f"{member.display_name} is no longer playing.")
				if playing_role:
					await member.remove_roles(playing_role)
			else:
				await ctx.send(f"{ctx.author.mention} {member.display_name} was already not playing.")

		for member_or_role in members:
			if isinstance(member_or_role, discord.Role):
				if member_or_role == playing_role:
					for player in here(ctx).room_players:
						await remove_player(player)
				else:
					raise commands.CheckFailure(f"Cannot remove `{member_or_role.name}`. Must be the current room's player role `{playing_role.name}`.")
			else:
				await remove_player(member_or_role)

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
