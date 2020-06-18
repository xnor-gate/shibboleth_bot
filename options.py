from discord.ext import commands

from check import no_dm_predicate
from rooms import here


class Options(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def cog_check(self, ctx):
		return no_dm_predicate(ctx)

	async def message_in_round(self, ctx):
		if here(ctx).in_round:
			await ctx.send("(This change will take effect next round.)")

	@commands.command(
		brief="Set or show number of words (0 for twice the player count)",
		description="Set the number of words. Or, call without a number to show the current value. A value of 0 means twice as many words as players (min 8, max 16). Changes during a round only affect later round.",
		aliases=["nw"],
	)
	async def numwords(self, ctx, *, num: int = None):
		if num is not None:
			if not ((2 <= num <= 100) or (num == 0)):
				raise commands.CheckFailure(f"Invalid number of words {num}.")
			here(ctx).num_words = num
			await self.message_in_round(ctx)

		num = here(ctx).num_words

		if num == 0:
			await ctx.send(f"Number of words: 0 (automatically double the number of players)")
		else:
			await ctx.send(f"Number of words: {num}")

	@commands.command(
		brief="Set or show team guess size for large games",
		description="Set or show maximum team guess size. In games where a team size exceeds this value, instead of guessing your whole team, you only guess a subset of this many players. Call without a number to show the current value.",
		aliases=["mg"],
	)
	async def maxguess(self, ctx, *, size: int = None):
		if size is not None:
			if not 1 <= size <= 99:
				raise commands.CheckFailure(f"Invalid team guess size {size}.")
			here(ctx).max_guess = size
			await self.message_in_round(ctx)

		size = here(ctx).max_guess
		await ctx.send(f"Guess team subset of size {size} (counting yourself) in games with {2*size + 1}+ players.")

	@commands.command(
		brief="Set or show veto round duration",
		description="Set the veto round duration in seconds. Zero means no veto round. Call without a number to show the current value.",
		aliases=["vd"],
	)
	async def vetodur(self, ctx, *, duration: int = None):
		if duration is not None:
			if not 0 <= duration <= 999:
				raise commands.CheckFailure(f"Invalid duration {duration}.")
			here(ctx).veto_duration = duration
			await self.message_in_round(ctx)

		duration = here(ctx).veto_duration

		if duration == 0:
			description = "0 (no veto round)"
		else:
			description = f"{duration} seconds"

		await ctx.send(f"Veto duration: {description}")

	@commands.command(
		brief="Set or show chance of more uneven teams",
		description="Set or show the chance of having more uneven teams, meant for smaller games. The chance is a float from 0.0 to 1.0. Skewed teams are like 3v1 or 4v1, imbalanced by one extra player. Call without a number to show the current value.",
		aliases=["sk"],
	)
	async def skew(self, ctx, *, skew_chance: float = None):
		if skew_chance is not None:
			if not 0.0 <= skew_chance <= 1.0:
				raise commands.CheckFailure(f"Invalid chance {skew_chance}.")
			here(ctx).skew_chance = skew_chance
			await self.message_in_round(ctx)

		skew_chance = here(ctx).skew_chance

		if skew_chance == 0.0:
			description = "0 (never skew)"
		else:
			description = f"{skew_chance:.1%}"

		await ctx.send(f"Skew chance: {description}")
