This is my first attempt at making a Discord bot. 
My goal is a bot that can help manage clans in servers for video games.
Mostly learning as I'm going, with occasional cleanups to help me get better at understanding.

Work in progress - Started April 23, 2026

TO DO (Last updated May 6 2026)
- /promote (user) (level) to promote a user to a higher level. Admin+ only, but Admin should NOT be able to promote themselves or someone else to level 4.
- /demote (user) (level) to demote a user to a lower level. Admin+ only. To demote from Level 1 -> 0, use /roster remove. 
- /link (nickname) (@user) to link a user to a nickname, making clan stat integration much easier. 
- /unlink (@user) to unlink a user and to revert the nickname back to a "guest" nickname
- Bugfixes: All clan info not being deleted when client runs /clan delete
- Bugfixes: Roster edits do not reflect kills leaderboard edits (May need to make a separate kill roster and a general roster)
- Edge cases: Discord message character limit exceeded; clan info edited but original messages already printed... etc. 
- Future reliability improvements
- Database migration from JSON to SQLite before testing to select servers
- Method to keep the bot permanently on (wihtout relying on my PC)

Once I finish this bot's core logic and features, I want to test it on select servers.
