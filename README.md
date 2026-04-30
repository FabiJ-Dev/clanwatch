This is my first attempt at making a Discord bot. 
My goal is a bot that can help manage clans in servers for video games.
Mostly learning as I'm going, with occasional cleanups to help me get better at understanding.

Work in progress - Started April 23, 2026

TO DO (Last updated April 30 2026)
- /roster (add/edit/delete) (@username) (nickname on leaderboard) (country - first letter) (country)
For testing purposes, maximum 15 players in a single clan. May expand.
Roster message will split based on levels set in the server: Level 1s at the bottom, level 4s at the top. 
- /vs (add/edit/delete) (date in DD/MM/YY) (score {your clan} {other clan}) (other clan's shorthand tag)
Would appear as (mockup), Clan A (yours) vs Clan B (them)

01 | 30/4/26 | CA 5:2 CB | ✅

02 | 30/4/26 | CA 5:5 CB | 🟡

03 | 30/4/26 | CA 2:5 CB | ❌ 

- /kills (add/remove/set/clear) for kill leaderboard.
Would appear as (mockup):
**Top Kills for [Clan]**
1. 🇺🇸 PlayerA - 30 ☠
2. 🇧🇷 PlayerB - 29 ☠
3. 🇪🇸 PlayerC - 28 ☠
[continue...

If player has 0 kills, they do not appear on the leaderboard.
If player is removed from the clan, I need to pick whether I keep them on the leaderboard or delete them. Or the admin of the clan can decide that if they run /kill clear with that deleted player.
- /promote (user) (level) to promote a user to a higher level. Admin+ only, but Admin should NOT be able to promote themselves or someone else to level 4.
- /demote (user) (level) to demote a user to a lower level. Admin+ only. To demote from Level 1 -> 0, use /roster remove. 
- Winrate calculation in the vs history when running /vs. 
- Edge cases: Discord message character limit exceeded; clan info edited but original messages already printed... etc. 
- Future reliability improvements

All data is stored in the storage json files. May be converted to a database later, but for now, this is how I'm going since it's going to be a small test pool that have this bot when it's ready to be tested.

Once I finish this bot's core logic and features, I want to test it on select servers.
