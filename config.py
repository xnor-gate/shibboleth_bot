import yaml

# Hardcoded in many user-facing strings, so if you change this you'll want to change those too
bot_prefix = "!"

# Default word list relative path
word_list_path = "wordlists/wordlist2000.txt"

# Map of channel name to optional role name for players in the given channel.
# Can be extended by adding the same numerical suffix to both, e.g. shibboleth-game2 -> Playing2
playing_roles_in_channels = {}

# Name of optional role for players in a channel not matching any of the above.
misc_playing_role = None

# Name of optional role for players wishing to be notified of a game.
notify_role = None

def init(config=None):
	# Read overrides from yaml file.
	config_file = "config/" + config + ".yaml"
	with open(config_file, "r") as f:
		globals().update(yaml.safe_load(f.read()))
