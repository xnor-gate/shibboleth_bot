import discord
from discord.ext import commands

from check import no_dm_predicate, during_round
from name_utils import names_string_formatted
from rooms import here


class Status(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def cog_check(self, ctx):
		return no_dm_predicate(ctx)

	async def show_team_sizes_message(self, ctx):
		room = here(ctx)
		game = room.game

		team_sizes_string = " or ".join([str(size) for size in sorted(set(game.possible_team_sizes))])

		if game.team_guess_size is not None:
			team_guess_size_comment = f", of which you guess a subset of {game.team_guess_size} (counting yourself)"
		else:
			team_guess_size_comment = ". Guess your whole team exactly"

		if game.might_skew:
			skew_comment = f" ({game.skew_chance:.1%} chance skewed)"
		else:
			skew_comment = ""

		team_sizes_message = f"Teams are of **size {team_sizes_string}**{skew_comment}{team_guess_size_comment}."
		await ctx.send(team_sizes_message)

	@commands.command(
		brief="Show list of players",
		description="Display a list of players.",
		aliases=["p", "pl"],
	)
	async def players(self, ctx):
		room = here(ctx)

		if room.in_round:
			game = room.game
			players = game.players

			player_mention_string = names_string_formatted(players)
			num_players = len(players)
			await ctx.send(f"__Players__ ({num_players}): {player_mention_string}")

			await self.show_team_sizes_message(ctx)

		else:
			players = room.room_players
			player_mention_string = names_string_formatted(players)
			num_players = len(players)
			await ctx.send(f"Players ({num_players}): {player_mention_string}")

	@commands.command(
		brief="Show public wordlist for this round",
		description="Show the public list of words for this round. If users are specified, this list will be messaged to them instead.",
		aliases=["w"],
	)
	@during_round()
	async def words(self, ctx, *members: discord.Member):

		wordlist_string = self.bot.get_cog("Round").wordlist_formatted_string(ctx)

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
