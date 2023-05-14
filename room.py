from name_utils import names_string
from shibboleth import Shibboleth


class RoomError(Exception):
	pass

class Room:
	def __init__(self, room_name, playing_role, channel):
		self.room_name = room_name
		self.playing_role = playing_role
		self.channel = channel

		self.room_players = []
		self.queued_joiners = []
		self.queued_leavers = []

		self.round_num = 1

		self.num_words = 0
		self.max_guess = 3
		self.veto_duration = 45
		self.skew_chance = 0.0

		self.game = None
		self.paused = False

	def __repr__(self):
		return self.status_string

	def make_game(self):
		include_veto_phase = self.veto_duration > 0
		num_players = len(self.room_players)
		if num_players <= 2 * self.max_guess:
			team_guess_size = None
		else:
			team_guess_size = self.max_guess

		if self.num_words == 0:
			num_words = min(max(2 * num_players, 10), 14) 
		else:
			num_words = self.num_words

		return Shibboleth(self.room_players, num_words, include_veto_phase=include_veto_phase, team_guess_size=team_guess_size, skew_chance=self.skew_chance)

	def start_round(self):
		if self.in_round:
			raise RoomError("Round already started.")
		self.game = self.make_game()
		self.paused = False

	@property
	def in_round(self):
		return self.game is not None

	def end_round(self):
		if not self.in_round:
			raise RoomError("No round ongoing")
		self.game = None
		self.paused = False
		self.round_num += 1

	def add_player(self, player):
		if self.in_round:
			raise RoomError("Can't add player while round is ongoing.")
		if player not in self.room_players:
			self.room_players.append(player)
			self.remove_member_from_joiner_queue(player)

	def remove_player(self, player):
		if self.in_round:
			raise RoomError("Can't remove player while round is ongoing.")
		if player in self.room_players:
			self.room_players.remove(player)
			self.remove_member_from_leaver_queue(player)

	def remove_all_players(self):
		if self.in_round:
			raise RoomError("Can't remove players while round is ongoing.")
		self.room_players = []

	def add_member_to_joiner_queue(self, member):
		if (member not in self.queued_joiners) and (member not in self.room_players):
			self.queued_joiners.append(member)

	def remove_member_from_joiner_queue(self, member):
		if member in self.queued_joiners:
			self.queued_joiners.remove(member)

	def add_member_to_leaver_queue(self, member):
		if (member not in self.queued_leavers) and (member not in self.queued_leavers):
			self.queued_leavers.append(member)

	def remove_member_from_leaver_queue(self, member):
		if member in self.queued_leavers:
			self.queued_leavers.remove(member)

	def sync_players(self):
		self.remove_all_players()

		if self.playing_role is None:
			return

		# Enumerating the users in the channel with the playing roles requires the members intent
		for member in self.channel.members:
			if self.playing_role in member.roles:
				self.add_player(member)

	@property
	def player_name_string(self):
		player_names = names_string(self.room_players)
		return f"Players in room ({len(self.room_players)}): {player_names}"

	@property
	def status_string(self):
		info_strings = []

		info_strings.append(f"Room: {self.room_name}")
		playing_role_name = self.playing_role.name if self.playing_role else "None"
		info_strings.append(f"Playing role: {playing_role_name}")
		info_strings.append(f"Round {self.round_num}")
		info_strings.append(self.player_name_string)
		if bool(self.queued_joiners):
			queued_joiner_names = names_string(self.queued_joiners)
			info_strings.append(f"Joining next round: {queued_joiner_names}")

		if self.in_round:
			info_strings.extend(self.game.info_strings)
			info_strings.append(f"Paused: {self.paused}")
		return "\n".join(info_strings)

	def pause(self):
		if self.paused:
			raise RoomError("Already paused.")
		self.paused = True

	def unpause(self):
		if not self.paused:
			raise RoomError("Already unpaused.")
		self.paused = False

	def resolve_team_guess(self, guesser, guessed_players, veto_timeout_override=False):
		if not self.in_round:
			raise RoomError("No game ongoing.")
		if self.paused:
			raise RoomError("Can't make guess while paused.")

		return self.game.resolve_team_guess(guesser, guessed_players, veto_timeout_override=veto_timeout_override)

	def resolve_word_guess(self, guesser, word):
		if not self.in_round:
			raise RoomError("No game ongoing.")
		if self.paused:
			raise RoomError("Can't make guess while paused.")

		return self.game.resolve_word_guess(guesser, word)
