# Shibboleth bot

This is a Discord bot to play the hidden-team word game Shibboleth remotely via real-time text on the [Shibboleth discord server](https://discord.gg/2SeRD8t).

### Table of Contents
1. [Using the bot](#using-the-bot)
2. [How to play Shibboleth](#how-to-play-shibboleth)
    - [Rules](#rules)
    - [Veto phase](#veto-phase)
    - [Partial team guesses](#partial-team-guesses)
3. [Playing on Discord](#playing-on-discord)
    - [Round logistics](#round-logistics)
    - [Fairness](#fairness)
    - [Discord tricks](#discord-tricks)
        - [Reactions](#reactions)
4. [Development](#development)
    - [Adding the bot to your server](#adding-the-bot-to-your-server)
    - [Forking this code](#forking-this-code)
3. [Credits](#credits)


## Using the bot
If you want to play, write `!join` in the game's channel. Write `!help` to show the bot's list of commands. You can do this in any channel in the server or by messaging the Shibboleth bot. Use `!help command` to get details on using that command.

## How to play Shibboleth

### Rules

Shibboleth (aka Castlefall) is a fast-paced hidden-team word game for 3 to 12 players. It's kind-of like Codenames, Spyfall, and Castle of the Devil. A round takes about 2-10 minutes.

You are given a secret word that only you know. Half the players get one secret word and half have another. For example, in a five-player game, three players might have "banana" and two might have "skateboard". 

The people sharing your word are your team, and those with the other word are your opponents. You want to work with your team and figure out who they are. At any point in the round, you can submit a guess of either:
- The full set of people on your team
- The opposing team's word

After any guess, the round immediately ends and the teams and words are revealed. If you're right, your team wins, and you're wrong, your team loses.

You try to find your team by giving clues about your word. The idea is to convince teammates that you share the same word, while being vague or tricky enough that the opposing team won't figure out your word. Cluing is freeform. You can say whatever you want in your clues, and you can clue whenever you want -- there aren't any turns. The only rule is your clues have to be public to everyone. You can assume anything someone says during a round is a clue, unless it's marked as "not a clue" ("nac").

A list of 14 or so random words including both secret words is publicly displayed. Scanning through it can help you look for words that the other team might be cluing. If you find one that seems to match, you might then give clues pretending that's your word to test this theory and try to infiltrate their team.

### Veto phase

If you play with a veto phase, when a player guesses their team, the round doesn't end yet and nothing is revealed. Instead, there is a 45-second veto period where anyone may guess the opposing team's word. If someone does, this word guess takes precedence and immediately determines who wins the round, and the earlier team guess is ignored. If, however, this period ends without anyone guessing a word, the original team guess goes through and determines the winner. 

A veto phase is not triggered when someone guesses the opposing team's word -- the round still ends immediately.

The idea of the veto phase is that if the other team gives obvious clues for their word and then quickly guesses their team, you have a bit of time to review their clues and check the word list to figure out their word and take the win. While usually players not among the guessed team are trying to figure out the guessed team's word, anyone may submit a word guess, including a player who was guessed or even the guesser themselves.

### Partial team guesses

In games with many players, guessing your exact team is hard, so there's an option to allow guessing only part of your team. For example, in a 9-player game, you might play that you need to guess exactly 3 people on your team counting yourself. The guess counts as  right if all those people are your on team and your whole team wins, even though some teammates aren't included in the guess.

### Skew

Small games with 2, 3, or 4 players might use the "skew" option to give a chance of more unbalanced team sizes 0v2, 0v3, or 1v3, which makes guessing your team harder. For example, in a 3-player game with skew chance 0.3, there's a 30% chance that the teams are secretly 0v3 instead of the usual 1v2, where every has the same word and will all win or all lose. Here, you could guess a team size 1 (just yourself), size 2, or size 3 (everyone).

## Playing on Discord

You can play on the [Shibboleth discord server](https://discord.gg/2SeRD8t). Just follow the link, click to accept the invite, and type in a name to show for you. If Discord asks for your e-mail to link your account, you can ignore this by clicking outside the prompt.

The bot automatically sends players their secret words and resolves guesses. Write `!help` to see the list of bot commands. You can play with your friends online at any time. If the Shibboleth user doesn't appear as online under "Bot", it's offline -- please let the maintainer know.

It's recommended to play Shibboleth on a computer rather than a phone.

### Round logistics

The game usually happens in the channel `shibboleth-game`. Go to that channel and write `!join` to play in the next round. You can see who is playing in the panel on the right. Players' names are highlighted in chat. There can be multiple games going at once in different game channels.

When a round starts, you'll get a DM (direct message) from the Shibboleth bot with your secret word. This will appear as a notication in "Home" (the Discord controller symbol) at the top of the list of channels on the left side. Click `Home`, then under direct messages click `Shibboleth` to see the message with your secret word. Then return to the game by clicking the link in the message.

You clue by typing in the chat. If players agree, you can instead clue over voice chat. To join the voice channel, click the Voice Chat channel corresponding to the game room.

During a round, the list of words is pinned to the channel, and you can view it with the shortcut Ctrl+P or pressing the pin icon. There is unfortunately not a way to keep it open while typing a clue, short of opening a separate broswer window with it. You can write `!words` to post it in the channel.

### Fairness

This games runs on the honor system. To make cluing fair:

- Don't look up information such as by Googling things
- Don't tell things to other players except through the chat
- Don't edit your messages or remove reactions to intentionally hide information
- Don't use weird crypto-ish clues like "The sum of the letter values mod 7...". Wordplay is fine and encouraged.

### Discord tricks

When making a team guess, it's recommend to use Discord's user autocomplete by typing @, starting to type their names, then pressing tab or clicking on it. This helps avoid typos. Both nicknames and usernames work. If there are similarly-named users, you can usually find the one who is playing because they have a green circle for online.

Use `@username` to direct your message to someone, such as to indicate that your message is aimed at them. You can reply to a message of theirs by clicking the `...` menu on their message on it and choosing `Quote`, such as to indicate that your clue confirms you understand their clue.

You might want to choose "Compact" for the Discord appearance when playing to shrink space between clues so you can see more on screen. Set this by clicking to the settings gear next to your user name at the bottom left, click `Appearance` under `App settings`, and check `Compact`.

#### Reactions

You can post reactions (emoji) on a message by clicking the smiley-face while hovering over it. You can also include them in your own message by clicking the smiley on the far right of the message box, or pressing Ctrl+E. You can also type the name like `:tree:`, which will autocomplete. Beware that the specific emoji images might differ on different people's devices.

Reactions on a clue can be used as a shorthand to express what you think about it. Some emoji with a conventional meaning are listed in the Shibboleth server category for convenience. For example, the `:vouch:` star symbol expresses that you fully trust the cluer as being on your team, and the `:fishing:` rod accuses the cluer of cluing a word that isn't theirs as bait. These have no rules function and are just a means of communication.

## Development

### Adding the bot to your server

You can add this bot to any Discord server that you manage. This is done solely through Discord's interface; it doesn't require running any code. Add the bot to your server using [this link](https://discord.com/api/oauth2/authorize?client_id=696541868548423782&permissions=268446720&scope=bot).

You can optionally do these:

- To restrict the bot to a specific channel or channels, for each channel you *don't* want it in, go to its channel permissions, add the Shibboleth role as a new permissions category, and remove its "Read Messages" permission. (Unfortunately, [Discord doesn't seem to provide a more scalable way to do this](https://support.discord.com/hc/en-us/community/posts/360045778711-Restrict-bots-to-certain-channels-#:~:text=At%20the%20moment%2C%20the%20only,the%20more%20tedious%20it%20becomes.).) If your channel permissions are synced with a category, you can change permissions for that category to affect all its channels.
- If you want a visible role to mark who is playing, create a role named `Playing Shibboleth`. Put it lower than the bot's Shibboleth role in the role list.
- If you want a role people can use to ping other about games, create a role named `Notify of Shibboleth Games`. Put it lower than the bot's Shibboleth role in the role list. Users can do `!notify` and `!unnotify` to get or remove this role, but the bot won't be ping it automatically.

The bot asks for the following permissions when you add it. You can uncheck them, or later change them via the permissions of the "Shibboleth" role or permissions for specific channels. You'll need Send Messages and View Channels (Read Messages) in a channel for the bot to function there.

* Send Messages
* View Channels (aka Read Messages)
* Manage Roles (optional: to handle `Playing Shibboleth` and `Notify of Shibboleth Games` roles if they exist)
* Manage Messages (optional: to pin the word list each round for easy access)

### Forking this code

You can also fork this code to run it locally for your Discord servers, creating a copy of this bot. To set up the project for local development:

1. Install dependencies (optionally in a virtualenv, if desired):

    ``` bash
    $ python3 -m pip install -r requirements.txt
    ```

To make a new instance of the bot and add it to your server:

1. [Obtain](https://discordpy.readthedocs.io/en/latest/discord.html#creating-a-bot-account) a Discord bot token and save it in `config/token.txt`.
2. [Invite](https://discordpy.readthedocs.io/en/latest/discord.html#inviting-your-bot) the bot to an appropriate server using the instructions in [the previous section](#adding-the-bot-to-your-server), except using your bot application's invite link.
3. (Optional) [Create](https://support.discord.com/hc/en-us/articles/206029707-How-do-I-set-up-Permissions-) an appropriately named role on the server for each channel (to hold users who are currently playing). You can also create a role for players who wish to be notified of a game. Role names are configured in `./config`. (See `./config/shib.yaml` for an example.) Make sure these role are listed below the role for your bot so that the bot has permissions for them.

Run unit tests:
``` bash
$ python3 -m unittest
```

Start the bot:

``` bash
$ python3 bot.py
```

Or pass `--config` to use a custom configuration matching your server/channels. To use `./config/foo.yaml`, run:

``` bash
$ python3 bot.py --config=foo
```

## Credits

Shibboleth bot and server by xnor-gate. Thanks to Discord for their platform and API, to Rapptz and contributors for [discord.py](https://github.com/Rapptz/discord.py) in which the bot was written, and to the discord.py Discord community for their frequent help.

Shibboleth (as Castlefall) was invented by people at MIT in 2017. Thanks to [garywang](https://github.com/garywang) and [betaveros](https://github.com/betaveros/castlefall) for making their sites to play the game in person at [mp.garywang.net](https://mp.garywang.net/) and [bpchen.com/castlefall](http://www.bpchen.com/castlefall) from which this project took inspiration.

Thanks to [dfkoh](https://github.com/dfkoh) for producing part of the word list, to [tckmn](https://github.com/tckmn) for making the server icon, and to [lchen025](https://github.com/lchen025) for code contributions. Thanks to everyone who suggested names and improvements.
