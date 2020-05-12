# Shibboleth bot

This is a Discord bot to play the hidden-team word game Shibboleth remotely via chat. You can play on the [Shibboleth discord server](https://discord.com/invite/TmHxFfG). It's available to play at any time -- just get a group of friends to join for a round.

### Table of Contents
1. [Using the bot](#using-the-bot)
2. [How to play Shibboleth](#how-to-play-shibboleth)
    1. [Veto phase](#veto-phase)
    2. [Partial team guesses](#partial-team-guesses)
3. [Playing on Discord](#playing-on-discord)
    1. [Round logistics](#round-logistics)
    2. [Fairness](#fairness)
    3. [Advanced](#advanced)
    4. [Reactions](#reactions)

## Using the bot
Write `!help` to see the bot's list of commands. You can do this in any channel in the server or to the bot via DM. Use `!help command` to get more detailed infomation on a command and its usage.

## How to play Shibboleth
Shibboleth (aka Castlefall) is a hidden-team word game for 4 to 12 players. A round takes about 5-20 minutes.

You are given a secret word that only you know. Half the players have one secret word and half have another. For example, in a five-player game, three players might get "banana" and two might get "portfolio". 

Your team is the people sharing your word. Your goal is to figure out who is on your team, or to figure out the opposing team's secret word is. If you or someone on your team succeed at this, you win.

You do this by giving clues for your word. The idea is to convince teammates that you share the same word, but be vague or tricky enough that the opposing team won't figure out your word. You can say clues whenever you want -- there aren't any turns. You have to give your clues publicly to everyone.

A list of 14 or so random words including both secret words is publicly displayed. Looking at this list can help you figure out if the other team might be cluing a certain word. You might then pretend to have that word to try to see if it's indeed their word and infiltrate their team.

At any point, you can submit a guess, and this decides which team wins. You can guess either:
- The full set of people on your team
- The opposing team's word

After the guess, the words and teams are revealed and the round ends. If your guess is correct, you and your team win. Otherwise, you and your team lose. When one team wins, the other loses, and vice versa.

### Veto phase

If you play with a veto phase, the round does not immediately end when a player guesses their team, and nothing is revealed yet. Instead, there is a 45-second period where anyone may guess the opposing team's word. If someone does, this word guess takes precedence and immediately determines who wins the round, and the earlier team guess is ignored. Otherwise, if this period ends without anyone guessing a word, the original team guess goes through and decides the winner.

The idea of the veto phase is that if the other team that gives too obvious clues for their word then quickly guesses their team, you have a bit of time to consider their clues and review the word list to figure out their word and win. While usually it's players not among those guessed trying to figure out the guessed team's word, anyone may submit a word guess, inlcuding a player who was guessed or even the guesser themselves.

### Partial team guesses

In games with many players, guessing your exact team is hard, an option is allow guessing only part of your team. For example, in a 9-player game, you might play that you need to guess exactly 3 people on your team counting yourself. The guess is right if all those people are your on team, even though some teammates won't be included in the guess. If any of the people you guess are not on your team, you lose. 

## Playing on Discord

You can play on the [Shibboleth discord server](https://discord.com/invite/TmHxFfG). The bot automatically sends players their secret words and resolves guesses. Write `!help` to see the list of bot commands. You can play at any time if you have people online to play with. If the Shibboleth user doesn't appear as online under "Bot", it must be  down -- please let the maintainer of the repository know.

If you don't have a Discord account, just click the invite and type in a name to show for you. Discord asks for your e-mail to link your account, but you can ignore this by clicking outside the prompt.

It's recommended to play Shibboleth on a computer rather than a phone.

### Round logistics

The game happens in the channel `shibboleth-game`. Go to that channel and write `!join` to join the next round. You can see who is playing in the right panel, and their names will show as highlighted in chat. There can be multiple games going at once in the different game channels.

When a round starts, you'll get a DM (direct message) from the Shibboleth bot with your secret word. This should appear as a notication in "Home" at the top of the list of channels on the left side. Click `Home`, then under direct messages click `Shibboleth`. Then return to the game by clicking the Shibboleth server.

During a round, the list of words is pinned to the channel, and can be opened with the shortcut Ctrl + E or by pressing the pin icon. There is unfortunately not a way to keep this open while typing a clue. You might want to open it in a separate tab. Use the command `!wordlist` to display it the chat, or `!wordlist [your username]` to message it to yourself.

In general, you clue by typing in chat. If players agree, you can instead clue over voice. To join the voice channel, see the channel menu on the left, and click the Voice Chat corresponding to the game room.

### Fairness

This games runs on the honor system. To make cluing fair:

- Don't look up information such as by Googling things
- Don't tell things to other players except through the chat

### Advanced

Use `@username` to direct your message to someone, such as to indicate that your clue or response is directed to them. You can also reply to their message by clicking the `...` menu on their message on it and choosing `Quote`. 

You might want to use Compact Mode when playing, which makes messages take up less space so you can see more clues. Set this by going to the setting gear next to your user name, under `App settings` click `Appearance`, then check `Compact`.

### Reactions

You can post reactions (emoji) on a message by clicking the smiley-face while hovering over it. You can also include them in your own message by clicking the smiley on the far right of the message box, or pressing Ctrl + E. You can also type the name like `:tree:`, which will autocomplete. Beware that the emoji might appear different on diffent people's screens, and some are hard to see in dark mode.

Reactions can be used as a quick shorthand, for examples indicate that you understood the marked clue. Some emoji have a conventional meaning, and are listed in the Shibboleth server emoji for convenience. For example, the `:vouch:` star symbol indicates that you fully trust the cluer as being on your team, and the `:fishing:` rod accuses the cluer of cluing a word that isn't theirs as bait. These have no rules function and are just a shorthand. Feel free to suggest more emoji to add to the server.
