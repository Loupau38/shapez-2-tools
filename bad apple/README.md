Generate a blueprint to display bad apple in shapez 2

- `original` contains bad apple in a custom format with 1 bit per pixel
- `downscale.py` downscales it to the desired ingame screen size in `downscaled`
- `convertToBlueprint.py` converts it to a blueprint in `bad apple.spz2bp`
- `display.py` uses `downscaled` and `audio.mp3` to display the downscaled version

All other files are taken from [Fake ShapeBot 2](https://github.com/Loupau38/Fake-ShapeBot-2.0)