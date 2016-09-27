# TenhouBot
A simple Tenhou Bot.

## Requirement
1. This bot is written by pure python. The only dependency is python-2.7.9 (or newer version).
2. Phantomjs(attached win/linux version in subdirectory) is called to utilize tenhou "牌理". Then, the most useless tile is discarded.

## Usage
1. Run `python MainBot.py`
2. Input lobby number and game type number when it prompts "input:", separated by comma.
  * Public rating lobby is 0
  * Game type number: 般南喰赤(9), 般東喰赤(1). For more detail, please check comments at bottom of "MainBot.py"
3. Default Bot user is NoName. To use other account, please revise the name in `send('<HELO name="NoName" tid="f0" sx="M" />\0')` to your account and replace dash("-") by "%2D"

## Frame
1. connect to server
2. authorization
3. register the game with given lobby number and game type
4. choose tile to discard by "牌理"
5. richii once it can

