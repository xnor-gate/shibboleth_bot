import discord
from discord.ext import commands

from check import no_dm_predicate, during_round
from rooms import here


class Status(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def cog_check(self, ctx):
		return no_dm_predicate(ctx)

	@commands.command(
		brief="Show list of players",
		description="Display a list of players.",
		aliases=["pl"],
	)
	async def players(self, ctx):
		room = here(ctx)
		if room.in_round:
			await ctx.send(room.game.player_name_string)
		else:
			await ctx.send(room.player_name_string)

	@commands.command(
		brief="Show public wordlist for this round",
		description="Show the public list of words for this round. If users are specified, this list will be messaged to them instead.",
		aliases=["w"],
	)
	@during_round()
	async def words(self, ctx, *members: discord.Member):

		wordlist_string = self.bot.get_cog("Round").wordlist_formatted_string

		# By default, send to the whole channel
		if not members:
			await ctx.send(wordlist_string)
		else:
			for member in members:
				await member.send(wordlist_string)

	@commands.command(
		brief="Show round number",
		description="Show the current round number. Increments automatically each round.",
		aliases=["rn"],
	)
	async def roundnum(self, ctx):
		await ctx.send(f"Round: {here(ctx).round_num}")

	@commands.command(
		brief="Show public gamestate and other info",
		description="Show game state and other info for debugging.",
		aliases=["st"],
	)
	async def status(self, ctx):
		await ctx.send(here(ctx).status_string)
