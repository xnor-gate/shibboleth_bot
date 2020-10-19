import unittest
from unittest.mock import MagicMock, patch

from collections import namedtuple
from enum import Enum, auto
from itertools import combinations, permutations

from shibboleth import Shibboleth, GameActionError, GameInitializationError


# Mocks/helpers

def mock_players(name_spec):
	""" Returns list of objects with a display_name property. """
	names = range(name_spec) if isinstance(name_spec, int) else name_spec  # Accept a count of names, for convenience.
	return [MagicMock(name="Player", display_name=str(i)) for i in names]


def unique_words(n):
	return [str(i) for i in range(n)]


def provide_corpus(corpus):
	""" Injects a corpusinto the managed context. """
	return patch.object(Shibboleth, "get_corpus", MagicMock(return_value=corpus), spec=True)


def deterministic_sample():
	""" Patches random.sample() to always return first k elements. """
	return patch('random.sample', spec=True, new=lambda population, k: population[:k])


def deterministic_shuffle():
	""" Patches random.shuffle() to be a no-op. """
	return patch('random.shuffle', spec=True, new=lambda *args: None)


def provide_random(r):
	""" Injects a deterministic value for random.random() """
	return patch('random.random', spec=True, return_value=r)


# noinspection PyPep8,PyPep8
class TestShibboleth(unittest.TestCase):

	# Initialization tests

	def test_init_players(self):
		""" Test initializing player list. """
		for player_list in (
				[],  # Empty player list permitted
				range(1),
				range(2),
				range(5),
				["a"] * 10,  # Repeated player names permitted
		):
			s = Shibboleth(mock_players(player_list), 16)
			self.assertIsNotNone(s)
			self.assertEqual(len(player_list), len(s.players))

		# Repeated player objects not permitted
		with self.assertRaises(GameInitializationError):
			dup_players = mock_players(2)
			_s = Shibboleth(dup_players + dup_players, 16)

	def test_init_corpus(self):
		""" Test loading corpus. """
		for size in range(2, 10):
			with self.subTest(corpus_size=size):
				l = unique_words(size)
				with provide_corpus(l):
					s = Shibboleth(mock_players(2), 2)
					self.assertIsNotNone(s)
					self.assertEqual(l, s.corpus)
					for w in s.words: self.assertIn(w, s.corpus)
					for w in s.secret_words: self.assertIn(w, s.corpus)

	def test_init_corpus_fail(self):
		""" Test error conditions for loading corpus. """
		for num_words in range(2, 5):
			for l in (
					["a"] * num_words,  # Results in repeated secret words
					[],  # Not enough words for 2 teams
					unique_words(num_words - 1),  # Not enough words to choose desired number of in-game words
			):
				with self.subTest(num_words=num_words, corpus=l):
					with self.assertRaises(GameInitializationError):
						with provide_corpus(l):
							_ = Shibboleth(mock_players(2), num_words)

	@deterministic_sample()
	@provide_corpus(unique_words(10))
	def test_init_secret_words(self):
		""" Test generating secret words. """
		for num_words in range(2, 10 + 1):
			s = Shibboleth(mock_players(2), num_words)
			self.assertEqual(unique_words(num_words), s.words)
			self.assertEqual(unique_words(2), s.secret_words)
			for w in s.secret_words:
				self.assertIn(w, s.words)
				self.assertIn(w, s.corpus)

	@deterministic_sample()
	def test_init_secret_words_fail(self):
		""" Test error conditions for generating secret words. """
		for l in (
				["a"] * 4,
				["a", "a"] + unique_words(2),
				["a", "a"] + unique_words(10),
		):
			with self.subTest(corpus=l):
				with self.assertRaises(GameInitializationError):
					with provide_corpus(l):
						_ = Shibboleth(mock_players(2), 4)

	def test_init_team_sizes_no_skew(self):
		""" Test computation of team sizes with no skew. """
		for num_players in range(10):
			with self.subTest(num_players=num_players):
				s = Shibboleth(mock_players(range(num_players)), 16)
				self.assertEqual(0.0, s.skew_chance)
				self.assertFalse(s.might_skew)
				half_floor = num_players // 2
				if num_players % 2 == 0:
					self.assertEqual([half_floor, half_floor], s.team_sizes)
					self.assertEqual([half_floor], s.possible_team_sizes)
				else:
					self.assertEqual([half_floor, half_floor + 1], s.team_sizes)
					self.assertEqual([half_floor, half_floor + 1], s.possible_team_sizes)
				self.assertEqual(num_players, sum(s.team_sizes))
				self.assertEqual(2, len(s.team_sizes))
				for size in s.team_sizes: self.assertIn(size, s.possible_team_sizes)

	def test_init_team_sizes_skew(self):
		""" Test computation of team sizes with skew. """
		for num_players in range(2, 10):
			for skew_chance in (0.2, 0.5, 0.75, 1.0):
				will_skew = skew_chance / 2
				will_not_skew = (skew_chance + 1.0) / 2
				with self.subTest(skew_chance=skew_chance, num_players=num_players):
					may_not_skew = Shibboleth(mock_players(range(num_players)), 16)
					with provide_random(will_skew):
						did_skew = Shibboleth(mock_players(range(num_players)), 16, skew_chance=skew_chance)
					with provide_random(will_not_skew):
						did_not_skew = Shibboleth(mock_players(range(num_players)), 16, skew_chance=skew_chance)

					for s in (did_skew, did_not_skew):
						self.assertEqual(skew_chance, s.skew_chance)
						self.assertTrue(s.might_skew)
						self.assertEqual(num_players, sum(s.team_sizes))
						self.assertEqual(2, len(s.team_sizes))
						for size in s.team_sizes: self.assertIn(size, s.possible_team_sizes)
						self.assertEqual(list(range(may_not_skew.team_sizes[0] - 1, may_not_skew.team_sizes[1] + 2)), s.possible_team_sizes)

					self.assertEqual(may_not_skew.team_sizes, did_not_skew.team_sizes)
					self.assertEqual([may_not_skew.team_sizes[0] - 1, may_not_skew.team_sizes[1] + 1], did_skew.team_sizes)

	def test_init_team_sizes_skew_fail(self):
		""" Test error conditions with skew_chance. """
		with self.assertRaises(GameInitializationError):
			# Too few players
			_s = Shibboleth(mock_players(1), 16, skew_chance=0.5)
		with self.assertRaises(GameInitializationError):
			# team_guess_size is also defined
			_s = Shibboleth(mock_players(8), 16, team_guess_size=3, skew_chance=0.5)

	@deterministic_sample()
	@deterministic_shuffle()
	@provide_corpus(unique_words(16))
	def test_init_player_words(self):
		""" Test assigning players to words. """
		for num_players in range(10):
			with self.subTest(num_players=num_players):
				players = mock_players(range(num_players))
				s = Shibboleth(players, 16)
				self.assertEqual(num_players, len(s.player_words))
				self.assertEqual(min(num_players, 2), len(set(s.player_words.values())))
				for w in s.player_words.values(): self.assertIn(w, unique_words(2))
				self.assertEqual(dict(zip(players, (["0"] * s.team_sizes[0]) + (["1"] * s.team_sizes[1]))), s.player_words)

	def test_init_player_words_random(self):
		""" Test construction with real randomness. """
		s = Shibboleth(mock_players(6), 16)
		self.assertEqual(2, len(set(s.player_words.values())))
		for w in s.player_words.values():
			self.assertIn(w, s.words)
			self.assertIn(w, s.corpus)

	# Functional tests

	@deterministic_sample()
	@deterministic_shuffle()
	@provide_corpus(unique_words(16))
	def test_teams_players_words(self):
		""" Test accessors for team/player/word mappings. """
		players = mock_players(6)
		s = Shibboleth(players, 16)
		self.assertEqual(["0", "1"], s.secret_words)
		self.assertEqual(dict(zip(players, (["0"] * 3) + (["1"] * 3))), s.player_words)
		for p in players[:3]: self.assertEqual("0", s.get_secret_word(p))
		for p in players[3:]: self.assertEqual("1", s.get_secret_word(p))
		self.assertEqual(players[:3], s.players_with_word("0"))
		self.assertEqual(players[3:], s.players_with_word("1"))
		self.assertEqual({"0": players[:3], "1": players[3:]}, s.teams)
		self.assertEqual("1", s.opposing_word("0"))
		self.assertEqual("0", s.opposing_word("1"))

	@deterministic_sample()
	@deterministic_shuffle()
	@provide_corpus(unique_words(16))
	def test_declare_winner(self):
		""" Test declare_winner(). """
		players = mock_players(6)
		s = Shibboleth(players, 16)
		self.assertEqual(["0", "1"], s.secret_words)
		self.assertEqual(dict(zip(players, (["0"] * 3) + (["1"] * 3))), s.player_words)

		for player in players[:3]:
			s.declare_winner(player, True)
			self.assertEqual("0", s.winning_word)
			s.declare_winner(player, False)
			self.assertEqual("1", s.winning_word)
		for player in players[3:]:
			s.declare_winner(player, True)
			self.assertEqual("1", s.winning_word)
			s.declare_winner(player, False)
			self.assertEqual("0", s.winning_word)

	@deterministic_sample()
	@deterministic_shuffle()
	@provide_corpus(unique_words(16))
	def test_check_word_guess(self):
		""" Test check_word_guess(). """
		# Well-formed guesses
		players = mock_players(6)
		s = Shibboleth(players, 16)
		for wrong_word in unique_words(16)[2:]:
			for player in players:
				self.assertFalse(s.check_word_guess(player, wrong_word))
		for player in players[:3]:
			self.assertTrue(s.check_word_guess(player, "1"))
		for player in players[3:]:
			self.assertTrue(s.check_word_guess(player, "0"))

		# Invalid guesses
		for guesser, word in (
				(players[0], "0"),
				(players[0], "1234"),
				(mock_players(["not in game"])[0], "0"),
		):
			with self.assertRaises(GameActionError):
				s.check_word_guess(guesser, word)

	@deterministic_sample()
	@deterministic_shuffle()
	@provide_corpus(unique_words(16))
	def test_check_team_guess_max_guess(self):
		""" Test check_team_guess() for a game requiring guessing a specific number of players. """
		players = mock_players(9)
		s = Shibboleth(players, 16, team_guess_size=3)
		self.assertEqual(3, s.team_guess_size)

		# noinspection PyShadowingNames
		def team_guesses(guesser, players, team, guess_size, correct):
			""" Returns set of (in)correct guesses (sets) that the guesser could have made. """
			other_teammates = set(team) - guesser
			correct_callins = combinations(other_teammates, guess_size - 1)
			correct_teams = set(set(callin + (guesser,)) for callin in correct_callins)
			if correct: return correct_teams
			other_players = set(players) - guesser
			possible_callins = combinations(other_players, guess_size - 1)
			possible_teams = set(set(callin + (guesser,)) for callin in possible_callins)
			incorrect_teams = list(possible_teams - correct_teams)
			return incorrect_teams

		# Well-formed guesses
		for i in range(9):
			player = players[i]
			team = players[:4] if i < 4 else players[4:]
			for correct_team in team_guesses(player, team, players, 3, True):
				for permutation in permutations(correct_team):
					self.assertTrue(s.check_team_guess(player, permutation))
			for incorrect_team in team_guesses(player, team, players, 3, False):
				for permutation in permutations(incorrect_team):
					self.assertTrue(s.check_team_guess(player, permutation))

		# Invalid guesses
		for guesser, guess in (
				(mock_players(["not in game"])[0], players[:3]),
				(players[0], players[:2]),
				(players[0], players[:4]),
				(players[0], [players[0], players[1], players[1]]),
				(players[0], players[1:4]),
		):
			for permutation in permutations(guess):
				with self.assertRaises(GameActionError):
					s.check_team_guess(guesser, permutation)

	@deterministic_sample()
	@deterministic_shuffle()
	@provide_corpus(unique_words(16))
	def test_check_team_guess_whole_team_guess(self):
		""" Test check_team_guess() for a game requiring guessing the whole team. """
		players = mock_players(5)
		s = Shibboleth(players, 16)
		self.assertIsNone(s.team_guess_size)
		# Players' words: ["0", "0", "1", "1", "1"]
		self.assertEqual([2, 3], s.possible_team_sizes)

		# Well-formed guesses
		for i in range(5):
			player = players[i]
			team = players[:2] if i < 2 else players[2:]
			team_subset_or_superset = players[:3] if i < 2 else players[2:4] if i == 2 else players[3:]
			wrong_team_size3 = [players[i]] + players[3:] if i < 2 else players[:2] + [players[i]]
			wrong_team_size2 = [players[i], players[-1]] if i < 2 else [players[1], players[i]]
			for guessed_team in (team, team_subset_or_superset, wrong_team_size3, wrong_team_size2):
				with self.subTest(guesser=player, guessed_team=guessed_team):
					for permutation in permutations(guessed_team):
						self.assertEqual(guessed_team == team, s.check_team_guess(player, permutation))

		# Invalid guesses
		for guesser, guess in (
				(mock_players(["not in game"])[0], players[:2]),
				(players[0], players[:4]),
				(players[0], players[:1]),
				(players[0], [players[0], players[0]]),
				(players[0], [players[0], players[1], players[1]]),
				(players[0], [players[0], players[0], players[1]]),
				(players[2], players[3:]),
		):
			for permutation in permutations(guess):
				with self.assertRaises(GameActionError):
					s.check_team_guess(guesser, permutation)

	@deterministic_sample()
	@deterministic_shuffle()
	@provide_corpus(unique_words(16))
	def test_state_machine(self):
		""" Test all game states and paths for games with and without veto phase. """

		class State(Enum):
			PLAYING = auto()
			TEAM_GUESSED = auto()
			TEAM_GUESSED_VETOABLE = auto()
			WORD_GUESSED = auto()
			VETO_PHASE_OVER = auto()
			ERROR = auto()

		Step = namedtuple("Step", ["from_state", "to_state", "action"])
		Test = namedtuple("Test", ["desc", "include_veto_phase", "steps", "win"])

		# The setup is 2 teams with words "0" and "1", with 3 players on each team:
		# players' words are ["0", "0", "0", "1", "1", "1"].
		# The parameter |win| is the team that wins. For paths that end in State.ERROR, it is None.
		# We assume all guesses are syntatically correct (right number of players, word is
		# actually in-game, etc.), as those error conditions are tested elsewhere.

		PLAYERS = mock_players(6)

		def assert_game_over(s, had_veto_phase):
			self.assertEqual("over", s.phase)
			self.assertFalse(s.game_ongoing)
			# The vetoable_team_guess field is not cleared after veto phase is over.
			self.assertEqual(had_veto_phase, s.in_veto_phase)
			self.assertEqual(had_veto_phase, s.vetoable_team_guess is not None)

		def verify(s, state):
			""" Check attributes' consistency with game state. """
			assert state is not State.ERROR

			if state == State.PLAYING:
				self.assertEqual("main", s.phase)
				self.assertTrue(s.game_ongoing)
				self.assertFalse(s.in_veto_phase)

			if state == State.TEAM_GUESSED:
				self.assertFalse(s.include_veto_phase)
				assert_game_over(s, had_veto_phase=False)

			if state == State.TEAM_GUESSED_VETOABLE:
				self.assertTrue(s.include_veto_phase)
				self.assertEqual("veto", s.phase)
				self.assertTrue(s.game_ongoing)
				self.assertTrue(s.in_veto_phase)

			if state == State.WORD_GUESSED:
				assert_game_over(s, had_veto_phase=False)

			if state == State.VETO_PHASE_OVER:
				self.assertTrue(s.include_veto_phase)
				assert_game_over(s, had_veto_phase=True)

		def run_test(test):
			s = Shibboleth(PLAYERS, 16, include_veto_phase=test.include_veto_phase)
			for step in test.steps:
				verify(s, step.from_state)
				if step.to_state == State.ERROR:
					with self.assertRaises(GameActionError):
						step.action(s)
					self.assertIsNone(test.win)
					return
				else:
					step.action(s)
					verify(s, step.to_state)
			self.assertEqual("over", s.phase)
			self.assertFalse(s.game_ongoing)
			self.assertIn(s.winning_word, s.secret_words)
			self.assertEqual(test.win, s.winning_word)

		# Actions that trigger various state transitions.
		def do_for_player(i):
			guesser = PLAYERS[i]
			team = PLAYERS[:3] if i in range(3) else PLAYERS[3:]
			opposing_word = "1" if i in range(3) else "0"
			wrong_team = {PLAYERS[0], PLAYERS[3], guesser}
			if len(wrong_team) < 3: wrong_team.add(PLAYERS[i + 1])
			return {
				"correct_team_guess": lambda s: s.resolve_team_guess(guesser, team),
				"incorrect_team_guess": lambda s: s.resolve_team_guess(guesser, wrong_team),
				"correct_word_guess": lambda s: s.resolve_word_guess(guesser, opposing_word),
				"incorrect_word_guess": lambda s: s.resolve_word_guess(guesser, "2"),
			}

		# Attempt a veto timeout call, which may or may not be valid.
		def veto_time_out(valid=True):
			return lambda s: s.resolve_team_guess(*(s.vetoable_team_guess if valid and s.in_veto_phase else (PLAYERS[1], PLAYERS[1:4])),
													veto_timeout_override=True)

		# Paths where the game ends normally.
		normal_tests = (
			Test(desc="Game ends immediately by correct word guess", include_veto_phase=False, steps=(
				Step(from_state=State.PLAYING, to_state=State.WORD_GUESSED, action=do_for_player(0)["correct_word_guess"]),
			), win="0"),
			Test(desc="Game ends immediately by incorrect word guess", include_veto_phase=False, steps=(
				Step(from_state=State.PLAYING, to_state=State.WORD_GUESSED, action=do_for_player(0)["incorrect_word_guess"]),
			), win="1"),
			Test(desc="Game ends immediately by correct word guess", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.WORD_GUESSED, action=do_for_player(0)["correct_word_guess"]),
			), win="0"),
			Test(desc="Game ends immediately by incorrect word guess", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.WORD_GUESSED, action=do_for_player(0)["incorrect_word_guess"]),
			), win="1"),

			Test(desc="Game ends immediately by correct team guess", include_veto_phase=False, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED, action=do_for_player(0)["correct_team_guess"]),
			), win="0"),
			Test(desc="Game ends immediately by incorrect team guess", include_veto_phase=False, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED, action=do_for_player(0)["incorrect_team_guess"]),
			), win="1"),

			Test(desc="Correct team guessed, vetoed correctly by same player", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["correct_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.VETO_PHASE_OVER, action=do_for_player(0)["correct_word_guess"]),
			), win="0"),
			Test(desc="Correct team guessed, vetoed incorrectly by same player", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["correct_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.VETO_PHASE_OVER, action=do_for_player(0)["incorrect_word_guess"]),
			), win="1"),
			Test(desc="Correct team guessed, vetoed correctly by same team", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["correct_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.VETO_PHASE_OVER, action=do_for_player(1)["correct_word_guess"]),
			), win="0"),
			Test(desc="Correct team guessed, vetoed incorrectly by same team", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["correct_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.VETO_PHASE_OVER, action=do_for_player(1)["incorrect_word_guess"]),
			), win="1"),
			Test(desc="Correct team guessed, vetoed correctly by opposing team", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["correct_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.VETO_PHASE_OVER, action=do_for_player(3)["correct_word_guess"]),
			), win="1"),
			Test(desc="Correct team guessed, vetoed incorrectly by opposing team", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["correct_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.VETO_PHASE_OVER, action=do_for_player(3)["incorrect_word_guess"]),
			), win="0"),

			Test(desc="Incorrect team guessed, vetoed correctly by same player", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["incorrect_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.VETO_PHASE_OVER, action=do_for_player(0)["correct_word_guess"]),
			), win="0"),
			Test(desc="Incorrect team guessed, vetoed incorrectly by same player", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["incorrect_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.VETO_PHASE_OVER, action=do_for_player(0)["incorrect_word_guess"]),
			), win="1"),
			Test(desc="Incorrect team guessed, vetoed correctly by same team", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["incorrect_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.VETO_PHASE_OVER, action=do_for_player(1)["correct_word_guess"]),
			), win="0"),
			Test(desc="Incorrect team guessed, vetoed incorrectly by same team", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["incorrect_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.VETO_PHASE_OVER, action=do_for_player(1)["incorrect_word_guess"]),
			), win="1"),
			Test(desc="Incorrect team guessed, vetoed correctly by opposing team", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["incorrect_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.VETO_PHASE_OVER, action=do_for_player(3)["correct_word_guess"]),
			), win="1"),
			Test(desc="Incorrect team guessed, vetoed incorrectly by opposing team", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["incorrect_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.VETO_PHASE_OVER, action=do_for_player(3)["incorrect_word_guess"]),
			), win="0"),

			Test(desc="Correct team guessed, veto phase timed out", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["correct_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.VETO_PHASE_OVER, action=veto_time_out()),
			), win="0"),
			Test(desc="Incorrect team guessed, veto phase timed out", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["incorrect_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.VETO_PHASE_OVER, action=veto_time_out()),
			), win="1"),
		)

		# Error raised by invalid veto timeout during an ongoing game.
		veto_error_tests = (
			Test(desc="Veto timeout with ongoing game", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.ERROR, action=veto_time_out()),
			), win=None),
			Test(desc="Veto timeout for ongoing game with no veto phase", include_veto_phase=False, steps=(
				Step(from_state=State.PLAYING, to_state=State.ERROR, action=veto_time_out()),
			), win=None),
			Test(desc="Veto timeout with invalid team guess to resolve", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["correct_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.ERROR, action=veto_time_out(valid=False)),
			), win=None),

			Test(desc="Attempt to guess team (by same player) during veto phase", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["incorrect_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.ERROR, action=do_for_player(0)["correct_team_guess"]),
			), win=None),
			Test(desc="Attempt to guess team (by same team) during veto phase", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["incorrect_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.ERROR, action=do_for_player(1)["correct_team_guess"]),
			), win=None),
			Test(desc="Attempt to guess team (by opposing team) during veto phase", include_veto_phase=True, steps=(
				Step(from_state=State.PLAYING, to_state=State.TEAM_GUESSED_VETOABLE, action=do_for_player(0)["incorrect_team_guess"]),
				Step(from_state=State.TEAM_GUESSED_VETOABLE, to_state=State.ERROR, action=do_for_player(3)["correct_team_guess"]),
			), win=None),
		)

		# Errors raised by attempting to make a guess or veto timeouts after the game is over.
		def invalid_continutation(test, action_name):
			desc = test.desc + ", attempted action after game over: " + action_name
			action = veto_time_out() if action_name == "veto_time_out" else do_for_player(0)[action_name]
			error_step = Step(from_state=test.steps[-1].to_state, to_state=State.ERROR, action=action)
			steps = (*test.steps, error_step)
			return Test(desc=desc, include_veto_phase=test.include_veto_phase, steps=steps, win=None)

		continuation_error_tests = [invalid_continutation(test, action_name)
									for test in normal_tests for action_name in do_for_player(0).keys()] + \
								   [invalid_continutation(test, "veto_time_out") for test in normal_tests if test.include_veto_phase]

		for test in (*normal_tests, *veto_error_tests, *continuation_error_tests):
			with self.subTest(desc=test.desc, include_veto_phase=test.include_veto_phase):
				run_test(test)


if __name__ == '__main__':
	unittest.main()
