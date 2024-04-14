import zipfile
import os

NUMBERS = [str(i) for i in range(10)]
def isNumber(string:str) -> bool:
    if string == "":
        return False
    for char in string:
        if char not in NUMBERS:
            return False
    return True

def getLatestBackup(directoryPath:str) -> str:
    latestBackupNum = 0
    latestBackup = None
    for dirEntry in os.scandir(directoryPath):
        if (
            dirEntry.is_file()
            and dirEntry.name.startswith("backup-v")
            and isNumber(curNum:=dirEntry.name.removeprefix("backup-v").split("-")[0])
            and (curNum:=int(curNum)) >= latestBackupNum
            ):
            latestBackup = dirEntry.path
            latestBackupNum = curNum
    if latestBackup is None:
        raise ValueError(f"No backups found in '{directoryPath}'")
    return latestBackup

def decompressSavegame(savegamePath:str,extractToPath:str,onlyExtractFiles:list[str]|None=None) -> None:
    with zipfile.ZipFile(savegamePath,"r") as zipRef:
        zipRef.extractall(extractToPath,onlyExtractFiles)