This is my first attempt at making a Discord bot. 
My goal is a bot that can help manage clans in servers for video games.
Mostly learning as I'm going, with occasional cleanups to help me get better at understanding.

Work in progress - Started April 23, 2026

TO DO (Last updated April 27 2026)
- /roster (add/edit/delete)
- countries.py, to have a country flag printed with the player's name and clan tag
- /vs (add/edit/delete)
- /kills (add/remove/set/clear) for kill leaderboard. If player has 0 kills, they do not appear.
- /promote (user) (level) to promote a user to a higher level. Admin+ only, but Admin should NOT be able to promote themselves or someone else to level 4.
- /demote (user) (level) to demote a user to a lower level. Admin+ only. To demote from Level 1 -> 0, use /roster remove. 
- Winrate calculation in the vs history when running /vs.
- Edge cases: Discord message character limit exceeded; clan info edited but original messages already printed... etc. 
- Future reliability improvements

All data is stored in the storage json files. May be converted to a database later, but for now, this is how I'm going since it's going to be a small test pool that have this bot when it's ready to be tested.

Once I finish this bot's core logic and features, I want to test it on select servers.