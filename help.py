class CommandError(Exception):
	pass

async def show_help_page(ctx):
	bot = ctx.bot
	message_lines = []

	prefix = "For game rules and Discord tips, see <http://github.com/xnor-gate/shibboleth_bot/blob/master/README.md>"

	for cog_name, cog in bot.cogs.items():
		message_lines.append(f"{cog_name}:")
		for command in cog.get_commands():
			if command.hidden:
				continue
			short_command = "!" + min(command.aliases, key=len) if command.aliases else ""
			explanation = command.brief

			command_line = f"  !{command.name:<12}{short_command:<7}{explanation}"
			message_lines.append(command_line)

	message_lines.append("")
	message_lines.append("Put any arguments to a command space-separated like \"!gw apple\" or \"!gt @Alice @Bob\".\nCall !help on a command for more info on using it.")

	message = "\n".join(message_lines)
	boxed_message = prefix + "\n" + f"```{message}```"
	await ctx.send(boxed_message, embed=None)

async def show_command_help(ctx, command_name):
	command_name = command_name.lstrip("!")

	all_commands = ctx.bot.all_commands
	if command_name not in all_commands.keys():
		raise CommandError(f"Unknown command")

	command = all_commands[command_name]

	name = command.name
	short_command = "!" + min(command.aliases, key=len) if command.aliases else ""

	desc = command.description
	command_signature_string = " " + command.signature if command.signature else ""

	await ctx.send(f"`!{name}{command_signature_string}`: {desc} `{short_command}` for short.")
