def names_of(players):
	return [player.display_name for player in players]

def names_string(players):
	return ", ".join(names_of(players))

def names_list_string(players):
	return "[" + ", ".join([f"**{name}**" for name in names_of(players)]) + "]"
