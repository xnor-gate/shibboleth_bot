import asyncio

import discord
from discord.ext import commands

from check import no_dm_predicate, during_round, by_player
from name_utils import names_list_string, names_string
from rooms import here


class Round(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def cog_check(self, ctx):
		return no_dm_predicate(ctx)

	async def start_round(self, ctx):
		here(ctx).start_round()

		await self.display_round_intro(ctx)
		await self.display_and_pin_wordlist(ctx)

		for player in here(ctx).game.players:
			await self.message_player_secret_word(ctx, player)

	async def display_round_intro(self, ctx):
		assert here(ctx).in_round, "Can't display intro with no round ongoing."

		player_mention_string = names_string(here(ctx).game.players)
		num_players = len(here(ctx).game.players)
		await ctx.send(f"**Round {here(ctx).round_num}**\nPlayers ({num_players}): {player_mention_string}")

		team_sizes_string = " or ".join([str(size) for size in sorted(set(here(ctx).game.team_sizes))])

		if here(ctx).game.team_guess_size is not None:
			team_guess_size_comment = f", of which you guess a subset of {here(ctx).game.team_guess_size} (counting yourself)"
		else:
			team_guess_size_comment = ""

		team_sizes_message = f"Teams are of size {team_sizes_string}{team_guess_size_comment}."
		await ctx.send(team_sizes_message)

		start_message = "You've been messaged your secret word. Use `!howguess` to show the commands to guess. Clue away!"
		await ctx.send(start_message)

	def wordlist_formatted_string(self, ctx):
		return f"```{here(ctx).game.word_list_string_columns()}```"

	async def reset_pins(self, ctx):
		pinned_messages = await ctx.channel.pins()
		for pinned_message in pinned_messages:
			if pinned_message.author.bot:
				await pinned_message.unpin()

	async def display_and_pin_wordlist(self, ctx):
		await self.reset_pins(ctx)
		msg = await ctx.send(self.wordlist_formatted_string(ctx))
		await msg.pin()

	async def message_player_secret_word(self, ctx, player):
		secret_word = here(ctx).game.get_secret_word(player)

		await player.send(f"Round {here(ctx).round_num}: Your secret word is **{secret_word}**")

	@commands.command(
		brief="Guess the opposing team's word",
		description="Guess the opposing team's word.",
		aliases=["gw"],
	)
	@by_player()
	@during_round()
	async def guessword(self, ctx, word: str):
		guesser = ctx.author

		if word not in here(ctx).game.words:
			raise commands.CheckFailure(f"`{word}` not in word list. Check spelling and capitalization. You can edit your message or enter a new one.")

		correct = here(ctx).resolve_word_guess(guesser, word)
		correct_string = {True: "right", False: "wrong"}[correct]
		await ctx.send(f"**{guesser.display_name}** (team **{here(ctx).game.get_secret_word(guesser)}**) guessed **{word}** for the opposing word, which is __{correct_string}__. Winning team: **{here(ctx).game.winning_word}**")

		# If this overrode a veto, say whether it would have succeeded
		if here(ctx).game.in_veto_phase:
			orig_guesser, orig_guessed_players = here(ctx).game.vetoable_team_guess

			orig_guessed_players_string = names_list_string(orig_guessed_players)

			correct = here(ctx).game.check_team_guess(orig_guesser, orig_guessed_players)
			correct_string = {True: "right", False: "wrong"}[correct]
			await ctx.send(f"(The original guess by **{orig_guesser.display_name}** (team **{here(ctx).game.get_secret_word(orig_guesser)}**) of {orig_guessed_players_string} would have been _{correct_string}_.)")

		await self.reveal_teams(ctx)
		await self.end_round_and_clean_up(ctx)

	@commands.command(
		brief="Guess the set of players on your team",
		description="Guess the full set of players who are on your team. For large games, you only guess a subset of them given by `!mg`. Write them as a space-separated list. You don't have to write yourself.",
		aliases=["gt"],
	)
	@by_player()
	@during_round()
	async def guessteam(self, ctx, *players: discord.Member):
		# Call the arg players to shorten it for the signature
		guessed_players = players
		guessed_players = list(guessed_players)

		guesser = ctx.author
		players_set = set(here(ctx).game.players)

		if not set(guessed_players) <= players_set:
			extra_players = list(set(guessed_players) - players_set)
			extra_player_names = [player.display_name for player in extra_players]
			extra_player_name_string = " and ".join(extra_player_names)
			phrase = {False: "is not a player", True: "are not players"}[len(extra_players) > 1]
			raise commands.CheckFailure(f"{extra_player_name_string} {phrase}. Use @ to autocomplete names to avoid typos. Names are case-sensitive. You can edit your message or enter a new one.")

		# As a convenience, include the guesser in their own team guess
		if guesser not in guessed_players:
			guessed_players = [guesser] + guessed_players

		await self.guess_team_helper(ctx, guesser, guessed_players)

	async def guess_team_helper(self, ctx, guesser, guessed_players, veto_timeout_override=False):

		here(ctx).resolve_team_guess(guesser, guessed_players, veto_timeout_override=veto_timeout_override)
		guessed_players_string = names_list_string(guessed_players)

		if (not here(ctx).game.include_veto_phase) or veto_timeout_override:
			# Full resolve
			correct = here(ctx).game.check_team_guess(guesser, guessed_players)
			correct_string = {True: "right", False: "wrong"}[correct]
			await ctx.send(f"**{guesser.display_name}** (team **{here(ctx).game.get_secret_word(guesser)}**) guessed {guessed_players_string} for the their team, which is __{correct_string}__.  Winning team: **{here(ctx).game.winning_word}**")
			await self.reveal_teams(ctx)
			await self.end_round_and_clean_up(ctx)

		else:
			# Enter veto phase
			await ctx.send(f"**{guesser.display_name}** guessed {guessed_players_string} for the their team. Entering veto phase.")
			await self.enter_veto_phase(ctx)

	async def enter_veto_phase(self, ctx):
		assert here(ctx).game.include_veto_phase

		veto_time = here(ctx).veto_duration
		await ctx.send(f"You have **{veto_time} seconds** to guess a word and override the preceding team guess, or it will resolve.")

		warning_time = 10

		# The below probably be better done with `bot.wait_for`.
		# We track if the same round is still ongoing by whether the round number hasn't changed.

		initial_round_num = here(ctx).round_num

		if veto_time > warning_time:
			await asyncio.sleep(veto_time - warning_time)

			if (here(ctx).game is not None) and (initial_round_num == here(ctx).round_num):
				await ctx.send(f"**{warning_time} seconds** to guess!")

		await asyncio.sleep(min(warning_time, veto_time))
		if (here(ctx).game is not None) and (initial_round_num == here(ctx).round_num):
			await self.end_veto_round(ctx)

	async def end_veto_round(self, ctx):
		await ctx.send("Veto phase over. Original guess goes through.")
		(guesser, guessed_players) = here(ctx).game.vetoable_team_guess
		await self.guess_team_helper(ctx, guesser, guessed_players, veto_timeout_override=True)

	async def reveal_teams(self, ctx):
		words = here(ctx).game.teams.keys()

		def is_winning_word(word):
			return word == here(ctx).game.winning_word

		words_with_winner_first = sorted(words, key=is_winning_word, reverse=True)
		team_strings = [f"**{word}**: {names_string(here(ctx).game.teams[word])}" for word in words_with_winner_first]
		await ctx.send("\n".join(team_strings))

	async def end_round_and_clean_up(self, ctx):
		here(ctx).end_round()
		lobby_cog = self.bot.get_cog("Lobby")
		await lobby_cog.resolve_joiner_queue(ctx)
		await lobby_cog.resolve_leaver_queue(ctx)

	@commands.command(
		brief="Pause the round, preventing guessing",
		description="Pause the round, preventing guessing. Use `!unpause` to resume.",
		aliases=["p"],
	)
	@during_round()
	async def pause(self, ctx):
		here(ctx).pause()
		await ctx.send(f"{ctx.author.mention} Paused the round. Use `!unpause` to resume.")

	@commands.command(
		brief="Unpause the round, allowing guessing once again",
		description="Unpause the round, allowing guessing once again.",
		aliases=["up"],
	)
	@during_round()
	async def unpause(self, ctx):
		here(ctx).unpause()
		await ctx.send(f"{ctx.author.mention} Resumed the round.")

	@commands.command(
		brief="End the round without a result",
		description="Terminate this round, ending it without a result.",
		aliases=["a"],
	)
	@during_round()
	async def abandon(self, ctx):
		message = f"Terminated Round {here(ctx).round_num}"
		await ctx.send(message)
		await self.end_round_and_clean_up(ctx)
