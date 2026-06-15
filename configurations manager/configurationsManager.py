import shutil
import os
import json
import traceback
import sys
from dataclasses import dataclass
import enum
import typing
import datetime
import webbrowser
from collections.abc import Callable
import time

GAME_ID = "2162800"
GAME_FOLDER_NAME = "shapez 2"

PATH_PREFIX = "\\\\?\\" if os.name == "nt" else "" # avoid issues with long file paths
BUILTIN_MOD_NAMES = {
    "3542611357" : "Shapez Shifter",
    "3542712030" : "MonoMod.RuntimeDetour",
    "3591335975" : "AssimpNet",
    "3738646868" : "Shapez Shifter [Developer]"
}
MOD_MANIFEST_FILE_NAME = "manifest.json"
USER_INPUT_PROMPT = "> "
RUN_WITH_STEAM_URL = f"steam://rungameid/{GAME_ID}"
OPEN_STEAM_URL = "steam://"

STEAMAPPS_PATH = ("{base}","steamapps")
STEAM_APP_MANIFEST_PATH = STEAMAPPS_PATH + (f"appmanifest_{GAME_ID}.acf",)
STEAM_GAME_PATH = STEAMAPPS_PATH + ("common",GAME_FOLDER_NAME)
STEAM_MODS_PATH = STEAMAPPS_PATH + ("workshop","content",GAME_ID)
STEAM_USERS_PATH = ("{base}","userdata")
STEAM_USER_CONFIG_PATH = STEAM_USERS_PATH + ("{userId}","config","localconfig.vdf")
STEAM_GAME_EXEC_FILE_PATHS = [
    STEAM_GAME_PATH + ("shapez 2.exe",),
    STEAM_GAME_PATH + ("shapez 2.app","Contents","MacOS","shapez 2"),
    STEAM_GAME_PATH + ("shapez 2.x86_64",)
]

DATA_FOLDER_PATH = os.path.join(PATH_PREFIX+os.getcwd(),"data")
CONFIG_PATH = os.path.join(DATA_FOLDER_PATH,"config.json")
BRANCHES_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH,"branches")
BRANCH_INFO_FILE_NAME = "branchInfo.json"
BRANCH_FILES_FOLDER_NAME = "files"
MODS_FOLDER_PATH = os.path.join(DATA_FOLDER_PATH,"mods")

os.makedirs(BRANCHES_FOLDER_PATH,exist_ok=True)
os.makedirs(MODS_FOLDER_PATH,exist_ok=True)

@dataclass
class GameConfig:
    name:str
    branch:str
    mods:list[str]
    launchParams:str
    lastTimeUsed:datetime.datetime

class LaunchMethod(enum.Enum):
    runSteam = "runSteam"
    runFile = "runFile"
    openSteam = "openSteam"
    none = "none"

@dataclass
class AppConfig:
    steamPath:str
    steamUserId:str
    launchMethod:LaunchMethod
    modNames:dict[str,str]
    configurations:list[GameConfig]

class BranchInfo(typing.TypedDict):
    size:str
    buildId:str
    manifest:str

class ModInfo(typing.TypedDict):
    name:str
    author:str|None
    description:str|None
    dependencies:list[str]

#region utility

def storeAppConfig() -> None:
    serialized = {
        "steamPath" : appConfig.steamPath.removeprefix(PATH_PREFIX),
        "steamUserId" : appConfig.steamUserId,
        "launchMethod" : appConfig.launchMethod.value,
        "modNames" : appConfig.modNames,
        "configurations" : [
            {
                "name" : c.name,
                "branch" : c.branch,
                "mods" : c.mods,
                "launchParams" : c.launchParams,
                "lastTimeUsed" : c.lastTimeUsed.isoformat()
            }
            for c in appConfig.configurations
        ]
    }
    with open(CONFIG_PATH,"w",encoding="utf-8") as f:
        json.dump(serialized,f,indent=4)

def loadAppConfig() -> None:
    global appConfig
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH,encoding="utf-8") as f:
            raw = json.load(f)
        appConfig = AppConfig(
            PATH_PREFIX + raw["steamPath"],
            raw["steamUserId"],
            LaunchMethod(raw["launchMethod"]),
            raw["modNames"],
            [
                GameConfig(
                    c["name"],
                    c["branch"],
                    c["mods"],
                    c["launchParams"],
                    datetime.datetime.fromisoformat(c["lastTimeUsed"])
                )
                for c in raw["configurations"]
            ]
        )
    else:
        appConfig = AppConfig("","",LaunchMethod.runSteam,{},[])
        editSteamPath()
        editSteamUserId()

def choiceInputChoicesDisplay(choices:list[str]) -> None:
    numLen = len(str(len(choices)))
    for i,c in enumerate(choices,start=1):
        print(f"{i:>{numLen}} : {c}")

def choiceInput(choices:list[str]) -> int:
    choiceInputChoicesDisplay(choices)
    while True:
        choice = input(USER_INPUT_PROMPT)
        try:
            choiceInt = int(choice)
        except ValueError:
            print("Not a number")
            print()
            continue
        if (choiceInt < 1) or (choiceInt > len(choices)):
            print("Number not in range")
            print()
            continue
        print()
        return choiceInt - 1

def multiChoiceInput(choices:list[str]) -> list[int]:
    choiceInputChoicesDisplay(choices)
    while True:
        rawChoices = input("Comma-separated list of numbers : ")
        if rawChoices == "":
            return []
        numbers = rawChoices.split(",")
        valid = True
        validNumbers = set()
        for num in numbers:
            try:
                numInt = int(num)
            except ValueError:
                print(f"Not a number : {num}")
                print()
                valid = False
                break
            if (numInt < 1) or (numInt > len(choices)):
                print(f"Number not in range : {numInt}")
                print()
                valid = False
                break
            validNumbers.add(numInt-1)
        if valid:
            print()
            return list(validNumbers)

type AcfDict = dict[str,str|AcfDict]

def parseAcf(raw:str) -> AcfDict:

    index = 0

    def parseString() -> str:
        nonlocal index
        assert raw[index] == '"', "String doesn't start with \""
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
        return '"' + string.replace("\\","\\\\").replace('"','\\"') + '"'

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

def removeDirContents(dirPath:str) -> None:
    for dirEntry in os.scandir(dirPath):
        if dirEntry.is_dir():
            shutil.rmtree(dirEntry.path)
        else:
            os.remove(dirEntry.path)

def copyDirContents(src:str,dest:str) -> None:
    shutil.copytree(src,dest,dirs_exist_ok=True)

def removeDir(dirPath:str) -> None:
    shutil.rmtree(dirPath)

def resolveSteamPath(path:tuple[str,...]) -> str:
    return os.path.join(*[
        e.format(
            base = appConfig.steamPath,
            userId = appConfig.steamUserId
        )
        for e in path
    ])



def getAppManifestContent() -> AcfDict:
    with open(resolveSteamPath(STEAM_APP_MANIFEST_PATH),encoding="utf-8") as f:
        return parseAcf(f.read())

def setAppManifestContent(content:AcfDict) -> None:
    with open(resolveSteamPath(STEAM_APP_MANIFEST_PATH),"w",encoding="utf-8") as f:
        f.write(serializeAcf(content))

def getSteamUserConfig() -> AcfDict:
    with open(resolveSteamPath(STEAM_USER_CONFIG_PATH),encoding="utf-8") as f:
        return parseAcf(f.read())

def setSteamUserConfig(content:AcfDict) -> None:
    with open(resolveSteamPath(STEAM_USER_CONFIG_PATH),"w",encoding="utf-8") as f:
        f.write(serializeAcf(content))



def getCurBranchInfo() -> tuple[str,BranchInfo]:
    appManifest = getAppManifestContent()
    appState = appManifest["AppState"]
    userConfig = appState["UserConfig"]
    branchName = userConfig["BetaKey"]
    branchSize = appState["SizeOnDisk"]
    buildId = appState["buildid"]
    depots = appState["InstalledDepots"]
    if len(depots) == 0:
        raise Exception("'InstalledDepots' is empty")
    firstDepot = list(depots.values())[0]
    branchManifest = firstDepot["manifest"]
    return (
        branchName,
        {
            "size" : branchSize,
            "buildId" : buildId,
            "manifest" : branchManifest
        }
    )

def listSavedBranches() -> list[str]:
    return [d.name for d in os.scandir(BRANCHES_FOLDER_PATH)]

def saveCurBranch(branchName:str,branchInfo:BranchInfo) -> None:

    branchPath = os.path.join(BRANCHES_FOLDER_PATH,branchName)

    if os.path.exists(branchPath):
        print(f"Removing existing copy of branch '{branchName}'...")
        removeDirContents(branchPath)
    else:
        os.makedirs(branchPath,exist_ok=True)

    with open(os.path.join(
        branchPath,
        BRANCH_INFO_FILE_NAME
    ),"w",encoding="utf-8") as f:
        json.dump(branchInfo,f,indent=4)

    print(f"Creating copy of branch '{branchName}'...")
    copyDirContents(
        resolveSteamPath(STEAM_GAME_PATH),
        os.path.join(branchPath,BRANCH_FILES_FOLDER_NAME)
    )
    print(f"Successfully saved branch '{branchName}'")

def installSavedBranch(branchName:str):

    branchPath = os.path.join(BRANCHES_FOLDER_PATH,branchName)
    with open(os.path.join(branchPath,BRANCH_INFO_FILE_NAME),encoding="utf-8") as f:
        branchInfo:BranchInfo = json.load(f)

    appManifest = getAppManifestContent()

    appState = appManifest["AppState"]
    userConfig = appState["UserConfig"]
    mountedConfig = appState["MountedConfig"]
    depots = appState["InstalledDepots"]
    if len(depots) == 0:
        raise Exception("'InstalledDepots' is empty")
    firstDepot = list(depots.values())[0]

    appState["SizeOnDisk"] = branchInfo["size"]
    appState["buildid"] = branchInfo["buildId"]
    appState["TargetBuildID"] = branchInfo["buildId"]
    firstDepot["manifest"] = branchInfo["manifest"]
    firstDepot["size"] = branchInfo["size"]
    userConfig["BetaKey"] = branchName
    mountedConfig["BetaKey"] = branchName

    gameInstallPath = resolveSteamPath(STEAM_GAME_PATH)
    print("Removing existing installation...")
    removeDirContents(gameInstallPath)

    print("Updating app manifest...")
    setAppManifestContent(appManifest)

    print(f"Copying branch '{branchName}'...")
    copyDirContents(
        os.path.join(branchPath,BRANCH_FILES_FOLDER_NAME),
        gameInstallPath
    )
    print(f"Successfully installed branch '{branchName}'")

def removeSavedBranch(branch:str) -> None:
    print(f"Removing saved copy of branch '{branch}'...")
    removeDir(os.path.join(BRANCHES_FOLDER_PATH,branch))
    print(f"Saved branch '{branch}' removed")



def getModInfo(modId:str,location:typing.Literal["steam","saved"]) -> ModInfo:
    manifestPath = os.path.join(
        resolveSteamPath(STEAM_MODS_PATH) if location == "steam" else MODS_FOLDER_PATH,
        modId,
        MOD_MANIFEST_FILE_NAME
    )
    with open(manifestPath,"rb") as f:
        modManifest:dict = json.load(f)
    author = modManifest.get("Author")
    description = modManifest.get("Description")
    if modId not in appConfig.modNames:
        if modId in BUILTIN_MOD_NAMES:
            appConfig.modNames[modId] = BUILTIN_MOD_NAMES[modId]
        else:
            print(f"Unknown mod '{modId}'")
            print(f"Author : {author}")
            print(f"Description : {description}")
            print("Please enter the name of this mod")
            appConfig.modNames[modId] = input(USER_INPUT_PROMPT).strip()
        storeAppConfig()
    return {
        "name" : appConfig.modNames[modId],
        "author" : author,
        "description" : description,
        "dependencies" : [
            d["ModId"].removeprefix("steam:")
            for d in modManifest.get("Dependencies",[])
            if d["ModId"].startswith("steam:")
        ]
    }

def listSteamMods() -> list[str]:
    return [
        d.name
        for d in os.scandir(resolveSteamPath(STEAM_MODS_PATH))
        if d.is_dir()
    ]

def listSavedMods() -> list[str]:
    return [d.name for d in os.scandir(MODS_FOLDER_PATH)]

def saveMod(modId:str,modName:str) -> None:

    source = os.path.join(resolveSteamPath(STEAM_MODS_PATH),modId)
    dest = os.path.join(MODS_FOLDER_PATH,modId)

    if os.path.exists(dest):
        print(f"Removing existing copy of mod '{modName}'...")
        removeDirContents(dest)
    else:
        os.makedirs(dest,exist_ok=True)

    print(f"Creating copy of mod '{modName}'...")
    copyDirContents(source,dest)
    print(f"Successfully saved mod '{modName}'")

def removeInstalledMod(modId:str) -> None:
    removeDir(os.path.join(resolveSteamPath(STEAM_MODS_PATH),modId))

def installSavedMod(modId:str) -> None:
    installTo = os.path.join(resolveSteamPath(STEAM_MODS_PATH),modId)
    os.makedirs(installTo,exist_ok=True)
    copyDirContents(os.path.join(MODS_FOLDER_PATH,modId),installTo)

def removeSavedMod(modId:str) -> None:
    removeDir(os.path.join(MODS_FOLDER_PATH,modId))



def gameLaunchLogic(launchParams:str) -> None:

    if appConfig.launchMethod == LaunchMethod.runSteam:
        webbrowser.open(RUN_WITH_STEAM_URL)
        print("Game launched via Steam")
        return

    if appConfig.launchMethod == LaunchMethod.runFile:
        resolvedPaths = []
        for path in STEAM_GAME_EXEC_FILE_PATHS:
            resolvedPath = resolveSteamPath(path)
            resolvedPaths.append(resolvedPath)
            if not os.path.exists(resolvedPath):
                continue
            command = '"' + resolvedPath.removeprefix(PATH_PREFIX) + '"'
            if launchParams != "":
                command += " " + launchParams
            os.system(command)
            print("Game launched from executable file")
            return
        print("Error : None of these files exist :")
        print("\n".join(resolvedPaths))
        return

    if appConfig.launchMethod == LaunchMethod.openSteam:
        webbrowser.open(OPEN_STEAM_URL)
        print("Opened Steam")

    if appConfig.launchMethod == LaunchMethod.none:
        print("App configured to do nothing on game launch")

def displayMod(modId:str,modInfo:ModInfo) -> str:
    return f"[{modId}] {modInfo["name"]}"

def getModDependencies(mods:list[str]) -> list[str]:
    dependencies:set[str] = set()
    savedMods = listSavedMods()
    toCheck = set(mods)
    checked = set()
    while len(toCheck) > 0:
        mod = toCheck.pop()
        checked.add(mod)
        modInfo = getModInfo(mod,"saved")
        for d in modInfo["dependencies"]:
            if d not in savedMods:
                print(
                    f"Warning : Mod '{d}' listed as a dependency of '{displayMod(mod,modInfo)}'"
                    + " but doesn't have a saved copy, skipping"
                )
                continue
            if d in mods:
                continue
            dependencies.add(d)
            if d not in checked:
                toCheck.add(d)
    return list(dependencies)

def getCurTime() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)

def displayModList(
    mods:list[str],
    modInfoGetter:Callable[[str],ModInfo]
) -> str:
    if len(mods) == 0:
        return "None"
    return ", ".join(
        displayMod(m,modInfoGetter(m))
        for m in mods
    )

#endregion

#region CLI

def editSteamPath() -> None:
    defaultPath = "C:\\Program Files (x86)\\Steam"
    print("Enter the path to the Steam folder")
    print(f"or leave empty to use the default : {defaultPath}")
    choice = input(USER_INPUT_PROMPT)
    print()
    appConfig.steamPath = defaultPath if choice == "" else choice
    storeAppConfig()

def editSteamUserId() -> None:
    usersFolder = resolveSteamPath(STEAM_USERS_PATH)
    userIds = [f.name for f in os.scandir(usersFolder) if f.is_dir()]
    if len(userIds) == 0:
        raise Exception(f"No folders found in {usersFolder}")
    if len(userIds) == 1:
        userId = userIds[0]
        print(f"Defaulting to user '{userId}'")
        print()
    else:
        print("Select which one is your Steam friend code")
        userId = userIds[choiceInput(userIds)]
    appConfig.steamUserId = userId
    storeAppConfig()

def startupChecks() -> None:

    curBranchName, curBranchInfo = getCurBranchInfo()
    if curBranchName not in listSavedBranches():
        print(f"Saving new branch : {curBranchName}")
        saveCurBranch(curBranchName,curBranchInfo)
        print()

    savedMods = listSavedMods()
    for modId in listSteamMods():
        if modId in savedMods:
            continue
        print(f"Saving new mod : {modId}")
        saveMod(modId,getModInfo(modId,"steam")["name"])
        print()

def askForConfig(msg:str) -> GameConfig|None:

    if len(appConfig.configurations) == 0:
        print("Error : No saved configurations")
        print()
        return None

    if len(appConfig.configurations) == 1:
        curConfig = appConfig.configurations[0]
        print(f"Defaulting to configuration '{curConfig.name}'")
        print()
        return curConfig

    sortedConfigs = sorted(
        appConfig.configurations,
        key=lambda c: c.lastTimeUsed,
        reverse=True
    )
    print(msg)
    return sortedConfigs[choiceInput([c.name for c in sortedConfigs])]

def launchGame() -> None:

    curConfig = askForConfig("Select the configuration to use")
    if curConfig is None:
        return

    print(f"Applying configuration : {curConfig.name}")
    print()

    curBranchName, curBranchInfo = getCurBranchInfo()
    if curBranchName == curConfig.branch:
        print("Installed branch matches wanted branch")
    else:
        print(f"Installed branch and wanted branch mismatch, saving '{curBranchName}'...")
        saveCurBranch(curBranchName,curBranchInfo)
        print(f"Installing '{curConfig.branch}'...")
        installSavedBranch(curConfig.branch)
    print()

    installedMods = listSteamMods()
    modsChanged = False

    for modId in installedMods:
        if modId not in curConfig.mods:
            modName = getModInfo(modId,"steam")["name"]
            print(f"Unwanted mod : {modName}")
            print(f"Saving mod '{modName}'...")
            saveMod(modId,modName)
            print(f"Removing install for mod '{modName}'...")
            removeInstalledMod(modId)
            print(f"Removed unwanted mod : {modName}")
            print()
            modsChanged = True

    for modId in curConfig.mods:
        if modId not in installedMods:
            modName = getModInfo(modId,"saved")["name"]
            print(f"Installing wanted mod '{modName}'...")
            installSavedMod(modId)
            print(f"Installed wanted mod : {modName}")
            print()
            modsChanged = True

    if not modsChanged:
        print("Installed mods match wanted mods")
        print()

    userConfig = getSteamUserConfig()
    paramsContainer = userConfig["UserLocalConfigStore"]["Software"]["Valve"]["Steam"]["apps"][GAME_ID]
    if paramsContainer["LaunchOptions"] == curConfig.launchParams:
        print("Current launch parameters match wanted launch parameters")
    else:
        print("Applying wanted launch paramters...")
        paramsContainer["LaunchOptions"] = curConfig.launchParams
        setSteamUserConfig(userConfig)
        print("Wanted launch parameters applied")
    print()

    print("Launching game...")
    gameLaunchLogic(curConfig.launchParams)
    print()

    curConfig.lastTimeUsed = getCurTime()
    storeAppConfig()

    print("Quitting app in 3s...")
    time.sleep(3)

def askForBranch(msg:str) -> str|None:

    savedBranches = listSavedBranches()

    if len(savedBranches) == 0:
        print("Error : No saved branches")
        print()
        return None

    if len(savedBranches) == 1:
        print(f"Defaulting to branch '{savedBranches[0]}'")
        print()
        return savedBranches[0]

    print(msg)
    return savedBranches[choiceInput(savedBranches)]

def askForMods(alreadySelected:list[str]|None) -> list[str]:

    savedMods = listSavedMods()
    modsInfo = {
        id : getModInfo(id,"saved")
        for id in savedMods
    }

    if len(savedMods) == 0:
        print("No saved mods, skipping step")
        print()
        return []

    def modSelectionDisplay(mod:str) -> str:
        return (
            (
                ""
                if alreadySelected is None else
                f"[{"X" if mod in alreadySelected else " "}] "
            )
            + displayMod(mod,modsInfo[mod])
        )

    if alreadySelected is None:
        print("Select which mods will be used by the configuration")
        print("Dependencies will be automatically added")
        print("Leave empty for no mods")
    else:
        print("Select which mods to toggle between used and unused")
        print("Dependencies will be automatically added (but not removed)")
        print("Leave empty to not make any change")

    toToggle = [
        savedMods[i]
        for i in multiChoiceInput([
            modSelectionDisplay(m)
            for m in savedMods
        ])
    ]

    if alreadySelected is None:
        selectedMods = toToggle
        modDependencies = getModDependencies(selectedMods)
    else:
        toKeep = [m for m in alreadySelected if m not in toToggle]
        toRemove = [m for m in alreadySelected if m in toToggle]
        toAdd = [m for m in toToggle if m not in alreadySelected]
        selectedMods = toKeep + toAdd
        modDependencies = [m for m in getModDependencies(selectedMods) if m not in toRemove]

    print(f"Mods selected : {displayModList(
        selectedMods,
        lambda m: modsInfo[m]
    )}")
    print(f"Dependencies added : {displayModList(
        modDependencies,
        lambda m: getModInfo(m,"saved")
    )}")
    print()
    return selectedMods + modDependencies

def deletionConfirmation(objName:str) -> bool:
    print(f"Are you sure you want to delete {objName} ? This action cannot be undone")
    c = input("y/n > ") == "y"
    print()
    return c

def editGameConfigLogic(config:GameConfig) -> None:

    while True:

        print(f"Editing configuration '{config.name}'")
        print("Select what to edit")
        action = choiceInput([
            "Name",
            "Branch",
            "Mods",
            "Launch parameters",
            "Exit editing"
        ])

        if action == 0:
            print("Enter the new name")
            config.name = input(USER_INPUT_PROMPT)
            print()
            continue

        if action == 1:
            branch = askForBranch(f"Select the new branch (currently '{config.branch}')")
            if branch is not None:
                config.branch = branch
            continue

        if action == 2:
            config.mods = askForMods(config.mods)
            continue

        if action == 3:
            print("Enter the new launch parameters")
            print("Current parameters (will be removed if not reentered below) :")
            print(config.launchParams)
            config.launchParams = input(USER_INPUT_PROMPT)
            print()
            continue

        if action == 4:
            break

    storeAppConfig()
    print(f"Saved modifications to '{config.name}'")
    print()

def createGameConfig() -> None:

    action = choiceInput([
        "Create a configuration from scratch",
        "Copy an existing configuration"
    ])

    if action == 1:
        toCopy = askForConfig("Select the configuration to copy")
        if toCopy is None:
            return
        newConfig = GameConfig(
            toCopy.name + " (copy)",
            toCopy.branch,
            toCopy.mods.copy(),
            toCopy.launchParams,
            getCurTime()
        )
        appConfig.configurations.append(newConfig)
        print(f"Configuration '{newConfig.name}' has been created, opening editing options")
        editGameConfigLogic(newConfig)
        return

    print("Choose a name for the configuration")
    configName = input(USER_INPUT_PROMPT)
    print()

    configBranch = askForBranch("Select a branch for the configuration")

    configMods = askForMods(None)

    print("Enter the launch parameters used for the configuration")
    print("Leave empty for no launch parameters")
    configLaunchParams = input(USER_INPUT_PROMPT)
    print()

    newConfig = GameConfig(
        configName,
        configBranch,
        configMods,
        configLaunchParams,
        getCurTime()
    )
    appConfig.configurations.append(newConfig)
    storeAppConfig()

    print(f"Configuration '{newConfig.name}' has been created")
    print()

def editGameConfig() -> None:
    config = askForConfig("Select the configuration to edit")
    if config is None:
        return
    editGameConfigLogic(config)

def editAppConfig() -> None:

    while True:

        print("Select which setting to edit")
        action = choiceInput([
            "Steam path",
            "Steam friend code",
            "Game launch method",
            "Exit settings"
        ])

        if action == 0:
            editSteamPath()
            continue

        if action == 1:
            editSteamUserId()
            continue

        if action == 2:
            print("Select which launch method to use")
            appConfig.launchMethod = [
                LaunchMethod.runSteam,
                LaunchMethod.runFile,
                LaunchMethod.openSteam,
                LaunchMethod.none
            ][choiceInput([
                f"Launch the game via Steam ({RUN_WITH_STEAM_URL})",
                "Launch the game executable (shapez 2.exe, shapez 2.x86_64, ...)",
                f"Open Steam ({OPEN_STEAM_URL})",
                "Do nothing (only change the installed files)"
            ])]
            continue

        if action == 3:
            break

    storeAppConfig()
    print("Settings saved")
    print()

def askForMod(msg:str,location:typing.Literal["saved","steam"]) -> str|None:

    mods = listSavedMods() if location == "saved" else listSteamMods()

    if len(mods) == 0:
        print(f"Error : No {"saved" if location == "saved" else "installed"} mods")
        print()
        return None

    if len(mods) == 1:
        print(f"Defaulting to mod '{displayMod(mods[0],getModInfo(mods[0],location))}'")
        print()
        return mods[0]

    print(msg)
    return mods[choiceInput([displayMod(m,getModInfo(m,location)) for m in mods])]

def updateSavedElem() -> None:

    print("Select what to update")
    action = choiceInput([
        "The current branch",
        "A mod",
        "Exit to main menu"
    ])

    if action == 2:
        return

    if action == 0:
        saveCurBranch(*getCurBranchInfo())
        print()
        return

    modId = askForMod("Select the mod to update","steam")
    if modId is None:
        return

    saveMod(modId,getModInfo(modId,"steam")["name"])
    print()

def removeSavedElem() -> None:

    print("Select what to delete")
    action = choiceInput([
        "A saved branch",
        "A saved mod",
        "A configuration",
        "Exit to main menu"
    ])

    if action == 3:
        return

    if action == 0:
        branch = askForBranch("Select the branch to delete")
        if branch is None:
            return
        if deletionConfirmation(f"the saved branch '{branch}'"):
            removeSavedBranch(branch)
            print()
        return

    if action == 1:
        modId = askForMod("Select the mod to delete","saved")
        if modId is None:
            return
        modName = displayMod(modId,getModInfo(modId,"saved"))
        if deletionConfirmation(f"the saved mod '{modName}'"):
            print(f"Removing mod '{modName}'...")
            removeSavedMod(modId)
            if modId in appConfig.modNames:
                appConfig.modNames.pop(modId)
                storeAppConfig()
            print(f"Mod '{modName}' removed")
            print()
        return

    config = askForConfig("Select the configuration to delete")
    if config is None:
        return
    if deletionConfirmation(f"the configuration '{config.name}'"):
        for i,c in enumerate(appConfig.configurations):
            if c is config:
                appConfig.configurations.pop(i)
                storeAppConfig()
                print(f"Configuration '{config.name}' removed")
                print()
                return
        print("Error : configuration wasn't found in the list of configurations")
        print()

def mainIteration() -> bool:

    print("=== Main menu ===")
    print()

    action = choiceInput([
        "Launch the game",
        "Create a configuration",
        "Edit a configuration",
        "Edit app settings",
        "Update a saved branch/mod",
        "Remove a saved branch/mod/configuration",
        "Exit"
    ])

    if action == 6:
        return True

    [
        launchGame,
        createGameConfig,
        editGameConfig,
        editAppConfig,
        updateSavedElem,
        removeSavedElem
    ][action]()

    return action == 0

def mainLoop() -> None:
    global appConfig

    print("Make sure Steam is closed while using this tool !")
    print()

    loadAppConfig()
    startupChecks()

    while True:
        if mainIteration():
            break

def errorHandler() -> None:

    try:
        mainLoop()
    except Exception:
        print()
        print("Error happened :")
        print()
        print("".join(traceback.format_exception(*sys.exc_info())))
        input("Press enter to quit")

if __name__ == "__main__":
    errorHandler()

#endregion