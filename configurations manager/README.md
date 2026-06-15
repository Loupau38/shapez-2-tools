This app allows you to create configurations for the game, a configuration being :

- A Steam beta branch
- Enabled mods
- Launch parameters

You can then switch between configurations using this app without having to redownload any content. (before said content is saved by this app, a first download using Steam is required)

Usage : download either `configurationsManager.exe` or `configurationsManager.py` and run it. This app's settings and saved branches/mods are stored in a `data` folder next to the downloaded file, it's thus recommended to move the file outside of the generic downloads folder.

When launching the app for the first time, you'll need to create a configuration before being able to launch the game. You can also select how the game is launched in the settings.

In order to keep this app simple, only file manipulation is done (no Steam API requests), this unfortunately has a few downsides :
- Anytime a new mod is discovered, you will have to enter its name in the app.
- If the game is launched with some mods enabled and some disabled, the disabled mods will appear in a warning screen ingame at the start.
- If you verify the game files in Steam, all disabled mods will be redownloaded.
- All disabled mods will show up greyed out in the mods tab ingame as `A new mod has been discovered and will be loaded after restarting the game.`

Don't hesitate to contact me if it doesn't work for you.