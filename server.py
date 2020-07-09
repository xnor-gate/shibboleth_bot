import discord
from discord.ext import commands

from check import no_dm_predicate
import config

class Server(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def cog_check(self, ctx):
		return no_dm_predicate(ctx)

	def get_notify_role(self, ctx):
		for role in config.notify_roles:
			notify_role = discord.utils.get(ctx.guild.roles, name=role)
			if notify_role:
				return notify_role
		assert False, "No notify role"

	@commands.command(
		brief="Get pinged on Discord when people want to play",
		description="Give yourself the \"Notify on Games\" role (or this server's equivalent), which can be pinged to alert those interested in joining games. This gets pinged when someone messages `@Notify of Games`, not automatically when there's a game.",
		aliases=["n"],
	)
	async def notify(self, ctx):
		member = ctx.author
		notify_role = self.get_notify_role(ctx)
		notify_role_name = notify_role.name

		if notify_role in member.roles:
			await ctx.send(f"{member.mention} already has `{notify_role_name}` role.")
		else:
			await member.add_roles(notify_role)
			await ctx.send(f"{member.mention} granted `{notify_role_name}` role.")

	@commands.command(
		brief="Remove yourself from being notified",
		description="Remove yourself from having the \"Notify on Games\" role (or this server's equivalent).",
		aliases=["un"],
	)
	async def unnotify(self, ctx):
		member = ctx.author
		notify_role = self.get_notify_role(ctx)
		notify_role_name = notify_role.name

		if notify_role not in member.roles:
			await ctx.send(f"{member.mention} already doesn't have `{notify_role_name}` role.")
		else:
			await member.remove_roles(notify_role)
			await ctx.send(f"{member.mention} removed from `{notify_role_name}` role.")

	@commands.command(
		brief="Show invite link to this server channel",
		description="Show an invite link to this server and channel to copy-paste",
		aliases=["i"],
	)
	async def invite(self, ctx):
		link = await ctx.channel.create_invite()
		await ctx.send(f"Invite link: {link}")
