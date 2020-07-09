import yaml

def init(config):
	globals().update({
		# Hardcoded in many user-facing strings, so if you change this you'll want to change those too
		"bot_prefix": "!",

		# Settings below require manual configuration on Discord server.
		# Expected to be configured via config/foo.yaml file.

		# Map of channel names to the role name used for players in that channel.
		"playing_roles_in_channels": {},
		# Role name for players in channel names not matching any of the above.
		"misc_role": "",
		# List of role names for players who wish to be notified of a new game.
		# The first one listed that exists in the guild will be used.
		"notify_roles": [],
	})

	# Read overrides from yaml file.
	config_file = "config/" + config + ".yaml"
	with open(config_file, "r") as f:
		globals().update(yaml.safe_load(f.read()))
