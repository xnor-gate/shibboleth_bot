from discord.ext import commands

from rooms import here


def is_dm(ctx):
	return ctx.guild is None

async def no_dm_predicate(ctx):
	if is_dm(ctx):
		raise commands.CheckFailure("Can't do that via DM.")
	return True

def no_dm():
	return commands.check(no_dm_predicate)


def round_ongoing(ctx):
	return here(ctx).in_round

async def during_round_predicate(ctx):
	if not round_ongoing(ctx):
		raise commands.CheckFailure("Can only do that during a round.")
	return True

def during_round():
	return commands.check(during_round_predicate)


def is_by_player(ctx):
	return round_ongoing(ctx) and (ctx.author in here(ctx).game.players)

async def by_player_predicate(ctx):
	if not is_by_player(ctx):
		raise commands.CheckFailure("Only players in the current round can do that.")
	return True

def by_player():
	return commands.check(by_player_predicate)
