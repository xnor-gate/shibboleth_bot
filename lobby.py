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
		description="Mark yourself as playing. Or, call with one or more usernames space-separated to mark them as playing.",
		aliases=["j"],
	)
	async def join(self, ctx, *members: discord.Member):
		if not members:
			members = (ctx.author,)

		for member in members:
			current_players = here(ctx).room_players

			if member.bot:
				await ctx.send(f"{ctx.author.mention} {member.display_name} is a bot.")
			elif member in current_players:
				await ctx.send(f"{ctx.author.mention} {member.display_name} was already playing.")
			elif here(ctx).in_round:
				await ctx.send(f"{ctx.author.mention} {member.display_name} will join and be pinged after this round ends.")
				here(ctx).add_member_to_player_queue(member)
			else:
				here(ctx).add_player(member)
				await member.add_roles(here(ctx).playing_role)
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
				await ctx.send(f"{ctx.author.mention} {member.display_name} cannot leave while playing in current round.")
			elif room.in_round and (member in room.queued_players):
				room.remove_member_from_player_queue(member)
				await ctx.send(f"{ctx.author.mention} {member.display_name} will no longer join after this round.")
			elif member in room.room_players:
				room.remove_player(member)
				await ctx.send(f"{member.display_name} is no longer playing.")
				await member.remove_roles(playing_role)
			else:
				await ctx.send(f"{ctx.author.mention} {member.display_name} was already not playing.")

		for member_or_role in members:
			if isinstance(member_or_role, discord.Role):
				if member_or_role == here(ctx).playing_role:
					for player in here(ctx).room_players:
						await remove_player(player)
				else:
					raise commands.CheckFailure(f"Cannot remove `{member_or_role.name}`. Must be the current room's player role `{playing_role}`.")
				for player in here(ctx).room_players:
					await remove_player(player)
			else:
				await remove_player(member_or_role)

	@commands.command(
		brief="Start a new round with the players currently joined",
		description="Start a new round with the players who joined.",
		aliases=["s"],
	)
	async def start(self, ctx):
		await self.bot.get_cog("Round").start_round(ctx)

	async def resolve_player_queue(self, ctx):
		room = here(ctx)
		for player in room.queued_players:
			await self.join(ctx, player)
		room.queued_players = []
