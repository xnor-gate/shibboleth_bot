from discord.ext import commands
from help import show_help_page, show_command_help

class Info(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		# self._original_help_command = bot.help_command
		# bot.help_command = MyHelpCommand(verify_checks=False, sort_commands=True)
		# bot.help_command.cog = self

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
		await ctx.send("\n".join(lines))

	@commands.command(
		brief="Show invite link to this server channel",
		description="Show an invite link to this server and channel to copy-paste",
		aliases=["i"],
	)
	async def invite(self, ctx):
		link = await ctx.channel.create_invite()
		await ctx.send(f"Invite link: {link}")
