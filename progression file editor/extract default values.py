import os
import json

GAME_PROGRESSION_PATH = os.path.expandvars("%USERPROFILE%/Downloads/basedata-v1058/scenarios/DefaultScenario.json")
IDENTIFIERS_PATH = os.path.expandvars("%USERPROFILE%/Downloads/basedata-v1058/identifiers.json")
DEFAULT_PROGRESSION_PATH = "./defaultProgression.json"
DEFUALT_VALUES_PATH = "./defaultValues.json"

with open(GAME_PROGRESSION_PATH,encoding="utf-8") as f:
    gameProgression = json.load(f)
with open(IDENTIFIERS_PATH,encoding="utf-8") as f:
    identifiers = json.load(f)

with open(DEFAULT_PROGRESSION_PATH,"w",encoding="utf-8") as f:
    json.dump(gameProgression,f,ensure_ascii=True,indent=4)

defaultProgression = gameProgression["Progression"]
defaultConfig = gameProgression["Config"]

nodeIds = []
nodeTitles = []
nodeDescriptions = []

sideQuestGroupTitles = []
sideQuestIds = []

linearUpgradeIds = []
linearUpgradeTitles = []

mechanicIds = []
mechanicTitles = []
mechanicDescriptions = []
mechanicIcons = []

buildingVariants = identifiers["BuildingVariantIds"]
islandLayouts = identifiers["IslandLayoutIds"]
wikiEntries = identifiers["WikiEntryIds"]
images = identifiers["ImageIds"]
videos = identifiers["VideoIds"]

for level in defaultProgression["Levels"]:
    nodeIds.append(level["Id"])
    nodeTitles.append(level["Title"])
    nodeDescriptions.append(level["Description"])

for sideQuestGroup in defaultProgression["SideQuestGroups"]:
    sideQuestGroupTitles.append(sideQuestGroup["Title"])
    for sideQuest in sideQuestGroup["SideQuests"]:
        sideQuestIds.append(sideQuest["Id"])

for sideUpgrade in defaultProgression["SideUpgrades"]:
    nodeIds.append(sideUpgrade["Id"])
    nodeTitles.append(sideUpgrade["Title"])
    nodeDescriptions.append(sideUpgrade["Description"])

for linearUpgrade in defaultProgression["LinearUpgrades"]:
    linearUpgradeIds.append(linearUpgrade["Id"])
    linearUpgradeTitles.append(linearUpgrade["Title"])

for mechanic in defaultProgression["Mechanics"]:
    mechanicIds.append(mechanic["Id"])
    mechanicTitles.append(mechanic["Title"])
    mechanicDescriptions.append(mechanic["Description"])
    if mechanic["IconId"] not in mechanicIcons: # remove when all mechanics get different icons
        mechanicIcons.append(mechanic["IconId"])

defaultValues = {
    "nodeIds" : nodeIds,
    "nodeTitles" : nodeTitles,
    "nodeDescriptions" : nodeDescriptions,

    "sideQuestGroupTitles" : sideQuestGroupTitles,
    "sideQuestIds" : sideQuestIds,

    "linearUpgradeIds" : linearUpgradeIds,
    "linearUpgradeTitles" : linearUpgradeTitles,

    "mechanicIds" : mechanicIds,
    "mechanicTitles" : mechanicTitles,
    "mechanicDescriptions" : mechanicDescriptions,
    "mechanicIcons" : mechanicIcons,

    "buildingVariants" : buildingVariants,
    "islandLayouts" : islandLayouts,
    "wikiEntries" : wikiEntries,
    "images" : images,
    "videos" : videos,
}

with open(DEFUALT_VALUES_PATH,"w",encoding="utf-8") as f:
    json.dump(defaultValues,f,ensure_ascii=True,indent=4)