import random

from name_utils import names_of, names_string_formatted


class GameActionError(Exception):
	pass

class GameInitializationError(Exception):
	pass

class Shibboleth:
	def __init__(self, players, num_words, include_veto_phase=True, team_guess_size=None, skew_chance=0.0):
		self.players = players
		try:
			self.player_names = names_of(players)
		except AttributeError:
			raise AttributeError("Player objects must have a display_name property")

		if len(set(players)) != len(players):
			raise GameInitializationError(f"Repeated players in {self.player_names}")

		self.entire_word_list = self.get_entire_word_list()
		self.include_veto_phase = include_veto_phase
		self.team_guess_size = team_guess_size

		self.vetoable_team_guess = None

		if not (2 <= num_words <= len(self.entire_word_list)):
			raise GameInitializationError(f"Invalid number of words {num_words}")
		self.num_words = num_words

		self.words = random.sample(self.entire_word_list, self.num_words)
		self.secret_words = random.sample(self.words, 2)
		# TODO(#7): Uniqueness should be enforced on entire word list instead. (Which will imply uniqueness of secret words.)
		num_distinct_secret_words = len(set(self.secret_words))
		if num_distinct_secret_words != 2:
			raise GameInitializationError(f"Number of secret words should be 2, but is {num_distinct_secret_words}. The corpus contained repeats.")

		num_players = len(players)

		self.skew_chance = skew_chance
		self.might_skew = skew_chance > 0

		if self.might_skew:
			if team_guess_size is not None:
				# This is theoretically possible (the team_guess_size must be at most the smaller of the skewed team
				# sizes, as enforced below), but like, why would you want to?
				raise GameInitializationError("Cannot make game with both skew chance and max_guess active.")
			if num_players < 2:
				raise GameInitializationError("Cannot make game with skew chance and <2 players.")

		skew = random.random() < skew_chance
		self.team_sizes = [num_players//2 - skew, (num_players+1)//2 + skew]
		assert sum(self.team_sizes) == num_players, "Sum of team sizes doesn't match number of players"

		min_possible_team_size = num_players // 2 - self.might_skew
		max_possible_team_size = (num_players+1)//2 + self.might_skew

		self.possible_team_sizes = list(range(min_possible_team_size, max_possible_team_size + 1))

		if (team_guess_size is not None) and (team_guess_size > min(self.possible_team_sizes)):
			raise GameInitializationError(f"Team guess size {team_guess_size} is too large for {len(players)} players.")

		secret_words_list = [word for (word, team_size) in zip(self.secret_words, self.team_sizes) for _ in range(team_size)]
		random.shuffle(secret_words_list)
		assert len(secret_words_list) == num_players, "Failure in assigning secret words"
		self.player_words = dict(zip(players, secret_words_list))

		self.winning_word = None

	def __repr__(self):
		return self.status_string

	@classmethod
	def get_entire_word_list(cls):
		# TODO(#7): Uniqueness should be asserted here, or can just return a set.
		with open("wordlists/wordlist2000.txt", "r") as f:
			words = [line.strip() for line in f.readlines()]
			return words

	def get_secret_word(self, player):
		assert player in self.players, "Player not in player list"
		return self.player_words[player]

	@property
	def word_list_string(self):
		return "\n".join(self.words)

	def word_list_string_columns(self, num_columns=2, column_space=20):
		word_list = self.words
		lines = []
		assert num_columns >= 1, "Invalid number of columns"

		while word_list:
			column_words = word_list[:num_columns]
			lines.append("".join(word.ljust(column_space) for word in column_words[:-1]) + column_words[-1])
			word_list = word_list[num_columns:]

		return "\n".join(lines)

	def players_with_word(self, word):
		assert word in self.secret_words, "Nobody has this secret word"
		return [player for player in self.players if self.get_secret_word(player) == word]

	@property
	def teams(self):
		return {word: self.players_with_word(word) for word in self.secret_words}

	def opposing_word(self, word):
		assert word in self.secret_words, "Nobody has this secret word"
		[other_word] = set(self.secret_words) - {word}
		return other_word

	def declare_winner(self, guesser, correct):
		""" Sets the winning word (and ends the game) based on the guesser and correctness of the game-ending guess. """
		guesser_word = self.get_secret_word(guesser)
		opposing_word = self.opposing_word(guesser_word)
		self.winning_word = guesser_word if correct else opposing_word

	def check_word_guess(self, player, word):
		if player not in self.players:
			raise GameActionError("Player not in player list")

		if word not in self.words:
			raise GameActionError(f"{repr(word)} not on word list. Check spelling and capitalization.")

		if word == self.get_secret_word(player):
			raise GameActionError("Cannot guess own word")

		return word == self.opposing_word(self.get_secret_word(player))

	def resolve_word_guess(self, player, guessed_word):
		if not self.game_ongoing:
			raise GameActionError("Cannot guess after game is done.")

		correct = self.check_word_guess(player, guessed_word)
		self.declare_winner(player, correct)
		return correct

	@property
	def valid_team_guess_sizes(self):
		if self.team_guess_size is not None:
			return [self.team_guess_size]
		else:
			return self.possible_team_sizes

	@property
	def valid_guess_sizes_string(self):
		return " or ".join(str(num) for num in sorted(set(self.valid_team_guess_sizes)))

	def check_team_guess(self, player, guessed_team):
		if player not in self.players:
			raise GameActionError("Player not in player list")

		guessed_team_set = set(guessed_team)

		if len(guessed_team_set) != len(guessed_team):
			raise GameActionError("Duplicate players guessed")
		if not (guessed_team_set <= set(self.players)):
			extra_players = guessed_team_set - set(self.players)
			extra_player_names = names_string_formatted(extra_players)
			raise GameActionError(f"Non-players guessed in {extra_player_names}")
		if player not in guessed_team_set:
			raise GameActionError("Player guessed a team without themselves")

		if len(guessed_team_set) not in self.valid_team_guess_sizes:
			raise GameActionError(f"Invalid guessed team size {len(guessed_team_set)}. Must be {self.valid_guess_sizes_string}.")

		actual_team_set = set(self.players_with_word(self.get_secret_word(player)))

		if self.team_guess_size is not None:
			return guessed_team_set <= actual_team_set
		else:
			return guessed_team_set == actual_team_set

	def resolve_team_guess(self, player, team, veto_timeout_override=False):
		""" Called when a team has been guessed, or when a veto phase times out. """
		if not self.game_ongoing:
			raise GameActionError("Cannot guess after game is done")
		if self.in_veto_phase and not veto_timeout_override:
			raise GameActionError("Cannot guess team during veto phase")
		if veto_timeout_override and not self.in_veto_phase:
			raise GameActionError("No active veto phase, veto timeout invalid")
		if veto_timeout_override and (player, team) != self.vetoable_team_guess:
			raise GameActionError("Cannot resolve team guess differing from the initial guess")

		correct = self.check_team_guess(player, team)

		if self.include_veto_phase and (not self.in_veto_phase):
			self.vetoable_team_guess = (player, team)
		else:
			self.declare_winner(player, correct)

		return correct

	@property
	def in_veto_phase(self):
		return self.vetoable_team_guess is not None

	@property
	def game_ongoing(self):
		return self.winning_word is None

	@property
	def phase(self):
		if not self.game_ongoing:
			return "over"
		elif self.in_veto_phase:
			return "veto"
		else:
			return "main"

	@property
	def player_name_string(self):
		player_names = names_string_formatted(self.players)
		return f"Players ({len(self.players)}): {player_names}"

	@property
	def info_strings(self):
		info_strings = []
		wordlist_abbreviated = ", ".join(self.words[:2] + ["..."])
		info_strings.append(self.player_name_string)
		info_strings.append(f"Words: {wordlist_abbreviated} ")
		info_strings.append(f"Phase: {self.phase}")

		if self.phase == "over":
			info_strings.append(f"Winner: {self.winning_word}")
		if self.phase == "veto":
			veto_player, veto_team = self.vetoable_team_guess
			info_strings.append(f"\tVetoable guess: {veto_player.display_name} guessing {names_string_formatted(veto_team)}")

		return info_strings

	@property
	def status_string(self):
		return "\n".join(self.info_strings)
