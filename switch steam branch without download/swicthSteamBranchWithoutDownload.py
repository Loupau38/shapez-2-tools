import shutil
import os
import json

DATA_FOLDER_PATH = os.path.join(os.curdir,"SSBWD_data")
CONFIG_PATH = os.path.join(DATA_FOLDER_PATH,"config.json")
GAMES_PATH = os.path.join(DATA_FOLDER_PATH,"games")
STEAM_GAMES_FOLDER = "common"
GAME_INFO_FILE_NAME = "gameInfo.json"
BRANCH_INFO_FILE_NAME = "branchInfo.json"
BRANCHES_FOLDER_NAME = "branches"
BRANCH_FILES_FOLDER_NAME = "files"

os.makedirs(GAMES_PATH,exist_ok=True)

def askForSteamappsPath() -> str:
    defaultPath = "C:\\Program Files (x86)\\Steam\\steamapps"
    print("Enter the path to the steamapps folder")
    print(f"or leave empty to use the default : {defaultPath}")
    choice = input("> ")
    print()
    path = defaultPath if choice == "" else choice
    with open(CONFIG_PATH,"w",encoding="utf-8") as f:
        json.dump({"steamappsPath":path},f,indent=4)
    return path

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH,encoding="utf-8") as f:
        steamappsPath = json.load(f)["steamappsPath"]
else:
    steamappsPath = askForSteamappsPath()

type AcfDict = dict[str,str|AcfDict]

def parseAcf(raw:str) -> AcfDict:

    index = 0

    def parseString() -> str:
        nonlocal index
        assert raw[index] == '"'
        index += 1
        curString = ""
        while True:
            char = raw[index]
            if char == '"':
                index += 1
                return curString
            if char == "\\":
                index += 1
            curString += raw[index]
            index += 1

    def skipWhiteSpace() -> None:
        nonlocal index
        while True:
            if index >= len(raw):
                raise EOFError
            if raw[index] not in (" ","\n","\t"):
                return
            index += 1

    def parseDictData() -> AcfDict:
        nonlocal index
        curDict = {}
        while True:
            try:
                skipWhiteSpace()
            except EOFError:
                return curDict
            if raw[index] == "}":
                index += 1
                return curDict
            key = parseString()
            skipWhiteSpace()
            if raw[index] == "{":
                index += 1
                value = parseDictData()
            else:
                value = parseString()
            curDict[key] = value

    return parseDictData()

def serializeAcf(parsed:AcfDict) -> str:

    INDENT = "\t"
    KEY_VALUE_SEP = "\t\t"
    LINE_SEP = "\n"

    def serializeString(string:str) -> str:
        return '"' + string.replace("\\","\\\\") + '"'

    def serializeDictData(parsed:AcfDict,depth:int) -> str:
        curOutput = ""
        for key,value in parsed.items():
            curOutput += INDENT*depth
            curOutput += serializeString(key)
            if isinstance(value,str):
                curOutput += KEY_VALUE_SEP
                curOutput += serializeString(value)
            else:
                curOutput += LINE_SEP + (INDENT*depth) + "{" + LINE_SEP
                curOutput += serializeDictData(value,depth+1)
                curOutput += (INDENT*depth) + "}"
            curOutput += LINE_SEP
        return curOutput

    return serializeDictData(parsed,0)

def choiceInput(choices:list[str]) -> int:
    for i,c in enumerate(choices,start=1):
        print(f"{i} : {c}")
    choice = int(input("> "))
    print()
    return choice

def removeDirContents(dirPath:str) -> None:
    for dirEntry in os.scandir(dirPath):
        if dirEntry.is_dir():
            shutil.rmtree(dirEntry.path)
        else:
            os.remove(dirEntry.path)

def copyDirContents(src:str,dest:str) -> None:
    shutil.copytree(src,dest,dirs_exist_ok=True)

while True:

    print("Make sure to restart steam after switching branches !")
    print()

    action = choiceInput([
        "Save current branch and switch to another",
        "Save current branch",
        "View current branch",
        "Add new game",
        "Change steamapps path",
        "Exit"
    ])

    if action == 6:
        break

    if action == 5:
        steamappsPath = askForSteamappsPath()
        continue

    curSavedGames:list[str] = []
    for dirEntry in os.scandir(GAMES_PATH):
        if dirEntry.is_dir():
            curSavedGames.append(dirEntry.name)

    if action == 4:

        canBeAdded:list[tuple[str,str]] = []
        for dirEntry in os.scandir(steamappsPath):
            if (
                dirEntry.is_file()
                and dirEntry.name.startswith("appmanifest_")
                and dirEntry.name.endswith(".acf")
            ):
                with open(dirEntry.path,encoding="utf-8") as f:
                    gameInfo = parseAcf(f.read())
                gameName = gameInfo["AppState"]["installdir"]
                if gameName not in curSavedGames:
                    canBeAdded.append((gameName,gameInfo["AppState"]["appid"]))

        if len(canBeAdded) == 0:
            print("No games to add")
            print()
            continue

        print("Select the game to add")
        toAdd = canBeAdded[choiceInput(g[0] for g in canBeAdded)-1]
        os.makedirs(os.path.join(GAMES_PATH,toAdd[0]),exist_ok=True)
        os.makedirs(os.path.join(GAMES_PATH,toAdd[0],BRANCHES_FOLDER_NAME),exist_ok=True)
        with open(os.path.join(
            GAMES_PATH,
            toAdd[0],
            GAME_INFO_FILE_NAME
        ),"w",encoding="utf-8") as f:
            json.dump({"gameId":toAdd[1]},f,indent=4)
        print(f"Added '{toAdd[0]}'")
        print()
        continue

    if len(curSavedGames) == 0:
        print("No games added")
        print()
        continue

    if len(curSavedGames) == 1:
        selectedGame = curSavedGames[0]
        print(f"Defaulting to game '{selectedGame}'")
        print()
    else:
        print("Select a game")
        selectedGame = curSavedGames[choiceInput(curSavedGames)-1]
    selectedGamePath = os.path.join(GAMES_PATH,selectedGame)
    gameInstallPath = os.path.join(steamappsPath,STEAM_GAMES_FOLDER,selectedGame)

    with open(os.path.join(
        selectedGamePath,
        GAME_INFO_FILE_NAME
    ),encoding="utf-8") as f:
        selectedGameId = json.load(f)["gameId"]

    selectedGameManifestPath = os.path.join(
        steamappsPath,
        f"appmanifest_{selectedGameId}.acf"
    )
    with open(selectedGameManifestPath,encoding="utf-8") as f:
        selectedGameManifest = parseAcf(f.read())

    curBranch = selectedGameManifest["AppState"]["UserConfig"]["BetaKey"]

    if action == 3:
        print(f"Currently on branch '{curBranch}'")
        print()
        continue

    allBranchesPath = os.path.join(selectedGamePath,BRANCHES_FOLDER_NAME)
    curBranchPath = os.path.join(allBranchesPath,curBranch)

    if os.path.exists(curBranchPath):
        print(f"Removing existing copy of branch '{curBranch}'...")
        removeDirContents(curBranchPath)
    else:
        os.makedirs(curBranchPath,exist_ok=True)

    with open(os.path.join(
        curBranchPath,
        BRANCH_INFO_FILE_NAME
    ),"w",encoding="utf-8") as f:
        json.dump({
            "size" : selectedGameManifest["AppState"]["SizeOnDisk"],
            "buildId" : selectedGameManifest["AppState"]["buildid"],
            "manifest" : list(selectedGameManifest["AppState"]["InstalledDepots"].values())[0]["manifest"],
        },f,indent=4)

    print(f"Creating copy of branch '{curBranch}'...")
    copyDirContents(gameInstallPath,os.path.join(curBranchPath,BRANCH_FILES_FOLDER_NAME))
    print(f"Successfully saved branch '{curBranch}'")
    print()

    if action == 2:
        continue

    selectableBranches:list[str] = []
    for dirEntry in os.scandir(allBranchesPath):
        if dirEntry.is_dir() and (dirEntry.name != curBranch):
            selectableBranches.append(dirEntry.name)

    if len(selectableBranches) == 0:
        print("No saved branches other than the current")
        print()
        continue

    if len(selectableBranches) == 1:
        switchToBranch = selectableBranches[0]
        print(f"Defaulting to branch '{switchToBranch}'")
        print()
    else:
        print("Select the branch to switch to")
        switchToBranch = selectableBranches[choiceInput(selectableBranches)-1]

    switchToBranchPath = os.path.join(allBranchesPath,switchToBranch)

    with open(os.path.join(switchToBranchPath,BRANCH_INFO_FILE_NAME),encoding="utf-8") as f:
        switchToBranchInfo = json.load(f)

    selectedGameManifest["AppState"]["SizeOnDisk"] = switchToBranchInfo["size"]
    selectedGameManifest["AppState"]["buildid"] = switchToBranchInfo["buildId"]
    selectedGameManifest["AppState"]["TargetBuildID"] = switchToBranchInfo["buildId"]
    firstDepot = list(selectedGameManifest["AppState"]["InstalledDepots"].values())[0]
    firstDepot["manifest"] = switchToBranchInfo["manifest"]
    firstDepot["size"] = switchToBranchInfo["size"]
    selectedGameManifest["AppState"]["UserConfig"]["BetaKey"] = switchToBranch
    selectedGameManifest["AppState"]["MountedConfig"]["BetaKey"] = switchToBranch

    print("Removing existing installation...")
    removeDirContents(gameInstallPath)

    with open(selectedGameManifestPath,"w",encoding="utf-8") as f:
        f.write(serializeAcf(selectedGameManifest))

    print(f"Copying branch '{switchToBranch}'...")
    copyDirContents(os.path.join(switchToBranchPath,BRANCH_FILES_FOLDER_NAME),gameInstallPath)
    print(f"Successfully copied branch '{switchToBranch}'")
    print()