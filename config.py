import yaml

# Prefix is hardcoded in many user-facing strings, so if you change this you'll want to change those too
bot_prefix = "!"

word_list_path = "wordlists/wordlist2000.txt"
config_data = {}

def init(config=None):
	# Read overrides from yaml file.
	config_file = f"config/{config}.yaml"
	with open(config_file, "r") as f:
		globals().update(yaml.safe_load(f.read()))