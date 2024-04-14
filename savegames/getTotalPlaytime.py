import decoder
import os
import json

SAVEGAMES_DIRS = [
    os.path.expandvars("%LOCALAPPDATA%low\\tobspr Games\\shapez 2\\savegames"),
    os.path.expandvars("%LOCALAPPDATA%low\\tobspr Games\\shapez 2\\savegame backups_")
]
TEMP_EXTRACTION_PATH = "./temp"

SAVEGAME_INFO_PATH = "savegame.json"

def main() -> None:

    totalPlayTime = 0
    numSavegames = 0

    for savegameDir in SAVEGAMES_DIRS:
        for dirEntry in os.scandir(savegameDir):
            if dirEntry.is_dir():
                latestBackup = decoder.getLatestBackup(dirEntry.path)
                print(f"Decompressing '{latestBackup}'")
                decoder.decompressSavegame(latestBackup,TEMP_EXTRACTION_PATH,[SAVEGAME_INFO_PATH])
                with open(TEMP_EXTRACTION_PATH+"/"+SAVEGAME_INFO_PATH,encoding="utf-8") as f:
                    savegameInfo = json.load(f)
                    totalPlayTime += savegameInfo["TotalPlaytime"]
                    numSavegames += 1

    print(f"Total playtime in seconds : {totalPlayTime:.3f}")
    print(f"Total playtime in minutes : {totalPlayTime/60:.3f}")
    print(f"Total playtime in hours : {totalPlayTime/3600:.3f}")
    print(f"With {numSavegames} savegames")
    input()

if __name__ == "__main__":
    main()