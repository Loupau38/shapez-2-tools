import os
import json

GAME_VERSION = 1064
BASE_PATH = os.path.expandvars(f"%LOCALAPPDATA%low/tobspr Games/shapez 2/basedata-v{GAME_VERSION}")
GAME_SCENARIO_PATHS = [
    BASE_PATH + "/scenarios/DefaultScenario.json",
    BASE_PATH + "/scenarios/OnboardingScenario.json"
]
IDENTIFIERS_PATH = BASE_PATH + "/identifiers.json"
DEFAULT_SCENARIO_PATH = "./defaultScenario.json"
DEFUALT_VALUES_PATH = "./defaultValues.json"

gameScenarios = []
for path in GAME_SCENARIO_PATHS:
    with open(path,encoding="utf-8") as f:
        gameScenarios.append(json.load(f))
with open(IDENTIFIERS_PATH,encoding="utf-8") as f:
    identifiers = json.load(f)

with open(DEFAULT_SCENARIO_PATH,"w",encoding="utf-8") as f:
    json.dump(gameScenarios[0],f,ensure_ascii=True,indent=4)

buildingVariants = identifiers["BuildingVariantIds"]
islandLayouts = identifiers["IslandLayoutIds"]
wikiEntries = identifiers["WikiEntryIds"]
images = identifiers["ImageIds"]
videos = identifiers["VideoIds"]

nodeIds = set()
nodeTitles = set()
nodeDescriptions = set()

sideQuestGroupTitles = set()
sideQuestIds = set()

linearUpgradeIds = set()
linearUpgradeTitles = set()

mechanicIds = set()
mechanicTitles = set()
mechanicDescriptions = set()
mechanicIcons = set()

for scenario in gameScenarios:

    curProgression = scenario["Progression"]

    for level in curProgression["Levels"]:
        nodeIds.add(level["Id"])
        nodeTitles.add(level["Title"])
        nodeDescriptions.add(level["Description"])

    for sideQuestGroup in curProgression["SideQuestGroups"]:
        sideQuestGroupTitles.add(sideQuestGroup["Title"])
        for sideQuest in sideQuestGroup["SideQuests"]:
            sideQuestIds.add(sideQuest["Id"])

    for sideUpgrade in curProgression["SideUpgrades"]:
        nodeIds.add(sideUpgrade["Id"])
        nodeTitles.add(sideUpgrade["Title"])
        nodeDescriptions.add(sideUpgrade["Description"])

    for linearUpgrade in curProgression["LinearUpgrades"]:
        linearUpgradeIds.add(linearUpgrade["Id"])
        linearUpgradeTitles.add(linearUpgrade["Title"])

    for mechanic in curProgression["Mechanics"]:
        mechanicIds.add(mechanic["Id"])
        mechanicTitles.add(mechanic["Title"])
        mechanicDescriptions.add(mechanic["Description"])
        mechanicIcons.add(mechanic["IconId"])

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
for k,v in defaultValues.items():
    defaultValues[k] = sorted(e for e in list(v) if e != "")

with open(DEFUALT_VALUES_PATH,"w",encoding="utf-8") as f:
    json.dump(defaultValues,f,ensure_ascii=True,indent=4)