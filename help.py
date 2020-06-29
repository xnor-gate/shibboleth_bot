import discord
from discord.ext import commands

from help_command import show_help_page, show_command_help
from rooms import here

class Help(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(
		brief="Show this help page, or help for the given command",
		description="Show this help page. If called with a command, show details and usage info for it.",
		aliases=["h"],
	)
	async def help(self, ctx, command=None):
		if command is None:
			await show_help_page(ctx)
		else:
			await show_command_help(ctx, command)

	@commands.command(
		brief="Show reminder of guess commands",
		description="Show a reminder of the instructions to guess a word.",
		aliases=["hg"],
	)
	async def howguess(self, ctx):
		guess_message = "Use `!gw word` to guess the opposing team's word.\nUse `!gt [teammates]` to guess your team. Write their names space-separated; you can use `@` to autocomplete. You can omit yourself."
		await ctx.send(guess_message)

		# If not in DM and round is ongoing, display additional info
		if not isinstance(ctx.channel, discord.channel.DMChannel) and here(ctx).in_round:
			await self.bot.get_cog("Status").show_team_sizes_message(ctx)

	@commands.command(
		brief="Show useful Discord shortcuts",
		description="Show useful Discord keyboard shortcuts.",
		aliases=["sh"],
	)
	async def shortcuts(self, ctx):
		lines = []
		lines.append("`Ctrl + P`: Show pinned wordlist")
		lines.append("`Ctrl + E`: Open emoji (reactions) menu")
		lines.append("`Ctrl + F`: Search recent messages")
		lines.append("Compact view is recommended to see more clues at once (`User Settings > App Settings > Appearance`)")
		await ctx.send("\n".join(lines))
