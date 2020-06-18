import discord
from discord.ext import commands

from help import show_help_page, show_command_help
from rooms import here


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

		# If not in DM and round is ongoing, display additional info
		if not isinstance(ctx.channel, discord.channel.DMChannel) and here(ctx).in_round:
			await self.bot.get_cog("Status").show_team_sizes_message(ctx)

	@commands.command(
		brief="Get notified when people want to play",
		description="Add yourself to the \"Notify on Games\" role, which can be pinged to alert those interested in joining games. This gets pinged when someone messages `@Notify of Games`, not automatically when there's a game.",
		aliases=["n"],
	)
	async def notify(self, ctx):
		member = ctx.author
		notify_role = discord.utils.get(ctx.guild.roles, name="Notify of games")
		if notify_role in member.roles:
			await ctx.send(f"{member.mention} already has \"Notify on Games\" role.")
		else:
			await member.add_roles(notify_role)
			await ctx.send(f"{member.mention} granted \"Notify on Games\" role.")

	@commands.command(
		brief="Remove yourself from being notified",
		description="Remove yourself from the \"Notify on Games\" role.",
		aliases=["un"],
	)
	async def unnotify(self, ctx):
		member = ctx.author
		notify_role = discord.utils.get(ctx.guild.roles, name="Notify of games")
		if notify_role not in member.roles:
			await ctx.send(f"{member.mention} already doesn't have \"Notify on Games\" role.")
		else:
			await member.remove_roles(notify_role)
			await ctx.send(f"{member.mention} removed from \"Notify on Games\" role.")

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
