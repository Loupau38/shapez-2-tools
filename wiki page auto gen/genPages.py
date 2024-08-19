import shapeViewer
import pygamePIL
import json
import os

GAME_VERSION_NAME = "0.0.8"

FORMAT_NAMES = [
    "autoGenMsg",
    "bpShape",
    "bpShapeList",
    "bpShapeListsPage",
    "changelogCategory",
    "changelogEntry",
    "changelogPage",
    "changelogVersion",
    "milestone",
    "milestoneList",
    "milestoneListBasedOnScenarioNote",
    "milestoneListsPage",
    "milestoneShape",
    "milestoneShapeContainer",
    "milestoneShapeEmpty",
    "milestoneShapeLineContainer",
    "milestoneShapeReuse",
    "milestoneShapeReuseAbove",
    "milestoneShapeReuseBelow",
    "milestoneShapeReuseNext",
    "milestoneShapeReuseNone",
    "milestoneShapeReuseOperatorLevel",
    "rewardBlueprintPoints",
    "rewardBuilding",
    "rewardKnowledgePanelEntry",
    "rewardMechanic",
    "rewardPlatform",
    "rewardPlatformUnits",
    "rewardResearchPoints",
    "rewardsJoiner",
    "task",
    "taskContainer",
    "taskGroup",
    "taskList",
    "taskListBasedOnScenarioNote",
    "taskListsPage"
]
FORMAT_PATHS = [f"./formats/{f}.txt" for f in FORMAT_NAMES]

SCENARIO_PATHS = [
    "./gameFiles/OnboardingScenario.json",
    "./gameFiles/DefaultScenario.json",
    "./gameFiles/HardScenario.json",
    "./gameFiles/InsaneScenario.json",
    "./gameFiles/HexagonalScenario.json"
]
TRANSLATIONS_PATH = "./gameFiles/translations-en-US.json"
CHANGELOG_PATH = "./gameFiles/Changelog.json"

TASKS_OUTPUT_PATH = "./outputTaskLists.txt"
TASK_SHAPES_OUTPUT_PATH = "./outputTaskShapes/"
TASK_SHAPES_OUTPUT_FILE_NAME_FORMAT = "Task-Shape-{shapeCode}-100.png"

MILESTONES_OUTPUT_PATH = "./outputMilestoneLists.txt"
MILESTONE_SHAPES_OUTPUT_PATH = "./outputMilestoneShapes/"
MILESTONE_SHAPES_OUTPUT_FILE_NAME_FORMAT = "Milestone-Shape-{shapeCode}-100.png"

BP_SHAPES_OUTPUT_PATH = "./outputBpShapeLists.txt"
BP_SHAPE_SHAPES_OUTPUT_PATH = "./outputBpShapeShapes/"
BP_SHAPE_SHAPES_OUTPUT_FILE_NAME_FORMAT = "Blueprint-Shape-{shapeCode}-100.png"

CHANGELOG_OUTPUT_PATH = "./outputChangelog.txt"

SHAPE_SIZE = 100

def loadTranslations() -> dict[str,str]:

    with open(TRANSLATIONS_PATH,encoding="utf-8") as f:
        translations:dict[str,str] = json.load(f)

    for key,value in translations.items():

        splits = value.split("<copy-from:")
        newValue = splits[0]
        for split in splits[1:]:
            replaceKey, *otherText = split.split("/>")
            newValue += translations[replaceKey]
            newValue += "/>".join(otherText)

        newValue = newValue.replace("<gl>","<span class=\"gl\">")
        newValue = newValue.replace("</gl>","</span>")

        translations[key] = newValue

    return translations

translations = loadTranslations()

def getTranslation(key:str) -> str:
    return translations[key.removeprefix("@")]

def loadFormats() -> dict[str,str]:
    formats:dict[str,str] = {}
    for name,path in zip(FORMAT_NAMES,FORMAT_PATHS):
        with open(path,encoding="utf-8") as f:
            formats[name] = f.read()
    return formats
formats = loadFormats()

def getFormattedRewards(rawRewards:list[dict[str,str]],scenario:dict) -> str:

    rewards = []
    seenBuildingNames = []
    seenPlatformNames = []

    for reward in rawRewards:

        if reward["$type"] == "ResearchPointsReward":
            rewards.append(formats["rewardResearchPoints"].format(
                amount = reward["Amount"]
            ))
        elif reward["$type"] == "BlueprintCurrencyReward":
            rewards.append(formats["rewardBlueprintPoints"].format(
                amount = round(reward["Amount"]*(scenario["Config"]["BaseBlueprintRewardMultiplier"]/100))
            ))
        elif reward["$type"] == "ChunkLimitReward":
            rewards.append(formats["rewardPlatformUnits"].format(
                amount = round(reward["Amount"]*(scenario["Config"]["BaseChunkLimitMultiplier"]/100))
            ))
        elif reward["$type"] == "BuildingReward":
            buildingName = getTranslation(f"building-variant.{reward['BuildingVariantId']}.title")
            if buildingName not in seenBuildingNames:
                rewards.append(formats["rewardBuilding"].format(
                    building = buildingName
                ))
                seenBuildingNames.append(buildingName)
        elif reward["$type"] == "IslandLayoutReward":
            platformName = getTranslation(f"island-layout.{reward['LayoutId']}.title")
            if platformName not in  seenPlatformNames:
                rewards.append(formats["rewardPlatform"].format(
                    platform = platformName
                ))
                seenPlatformNames.append(platformName)
        elif reward["$type"] == "WikiEntryReward":
            rewards.append(formats["rewardKnowledgePanelEntry"].format(
                entry = getTranslation(f"wiki.{reward['EntryId']}.title")
            ))
        elif reward["$type"] == "MechanicReward":
            rewards.append(formats["rewardMechanic"].format(
                # mechanic names are defined in scenarios, but they all use the same 'research.<id>.title' structure
                mechanic = getTranslation(f"research.{reward['MechanicId']}.title")
            ))

    return formats["rewardsJoiner"].format().join(rewards)

def renderShape(shapeCode:str,scenario:dict,outputPath:str) -> None:
    if not os.path.exists(outputPath):
        shapeRendered = shapeViewer.renderShape(shapeCode,SHAPE_SIZE,shapeConfig=(
            shapeViewer.SHAPE_CONFIG_HEX
            if scenario["Config"]["ShapesConfigurationId"] == "DefaultShapesHexagonalConfiguration" else
            shapeViewer.SHAPE_CONFIG_QUAD
        ))
        pygamePIL.image_save(shapeRendered,outputPath)
        print(f"Generated new shape : {outputPath}")

def getTooltipSafeString(string:str) -> str:
    return string.replace("<span class=\"gl\">","").replace("</span>","").replace("\n"," ")

def main() -> None:

    scenarios = []
    for path in SCENARIO_PATHS:
        with open(path,encoding="utf-8") as f:
            scenarios.append(json.load(f))

    with open(CHANGELOG_PATH,encoding="utf-8") as f:
        changelogRaw:list[dict[str,str|list[str]]] = json.load(f)

    autoGenMsg = formats["autoGenMsg"].format(
        gameVersion = GAME_VERSION_NAME
    )

    scenarioNames = {}

    taskLists = ""
    taskListLens = {}

    milestoneLists = ""
    milestoneListLens = {}

    bpShapeLists = ""

    for scenario in scenarios:

        scenarioId = scenario["UniqueId"]
        scenarioName = getTranslation(scenario["Title"])
        scenarioNames[scenarioId] = scenarioName

        if scenario.get("BasedOnScenarioId") is None:
            toAddTaskGroupIndex = 0
            toAddMilestoneIndex = 0
            taskBasedOnScenarioNote = ""
            milestoneBasedOnScenarioNote = ""
        else:
            basedOnScenarioId = scenario["BasedOnScenarioId"]
            toAddTaskGroupIndex = taskListLens[basedOnScenarioId]
            toAddMilestoneIndex = milestoneListLens[basedOnScenarioId]
            taskBasedOnScenarioNote = formats["taskListBasedOnScenarioNote"].format(
                basedOnScenario = scenarioNames[basedOnScenarioId]
            )
            milestoneBasedOnScenarioNote = formats["milestoneListBasedOnScenarioNote"].format(
                basedOnScenario = scenarioNames[basedOnScenarioId]
            )

        taskGroups = ""
        curTaskShapesOutputPath = TASK_SHAPES_OUTPUT_PATH
        os.makedirs(curTaskShapesOutputPath,exist_ok=True)
        taskListLens[scenarioId] = len(scenario["Progression"]["SideQuestGroups"])

        for taskGroupIndex,taskGroup in enumerate(scenario["Progression"]["SideQuestGroups"],start=1):

            tasks = []

            for taskIndex,task in enumerate(taskGroup["SideQuests"],start=1):

                shapeCode:str = task["Costs"][0]["Shape"]
                shapeCodeFileSafe = shapeCode.replace(":","-")
                curShapeOutputPath = curTaskShapesOutputPath + TASK_SHAPES_OUTPUT_FILE_NAME_FORMAT.format(
                    shapeCode = shapeCodeFileSafe
                )
                renderShape(shapeCode,scenario,curShapeOutputPath)

                tasks.append(formats["task"].format(
                    taskIndex = taskIndex,
                    taskShapeImage = shapeCodeFileSafe,
                    taskShapeCode = shapeCode,
                    taskShapeAmount = task["Costs"][0]["Amount"],
                    taskRewards = getFormattedRewards(task["Rewards"],scenario)
                ))

            taskGroups += formats["taskGroup"].format(
                numTasks = len(taskGroup["SideQuests"]),
                taskGroupIndex = toAddTaskGroupIndex + taskGroupIndex,
                taskGroupName = getTranslation(taskGroup["Title"]),
                firstTask = tasks[0],
                taskGroupMilestoneRequired = getTranslation(f"research.{taskGroup['RequiredUpgradeIds'][0]}.title"),
                tasks = "".join(formats["taskContainer"].format(
                    task = t
                ) for t in tasks[1:])
            )

        taskLists += formats["taskList"].format(
            scenarioName = scenarioName,
            basedOnScenarioNote = taskBasedOnScenarioNote,
            taskGroups = taskGroups
        )

        #####

        milestones = ""
        curMilestoneShapesOutputPath = MILESTONE_SHAPES_OUTPUT_PATH
        os.makedirs(curMilestoneShapesOutputPath,exist_ok=True)
        milestoneListLens[scenarioId] = len(scenario["Progression"]["Levels"])
        maxMilestoneShapesPerLine = max(0 if len(m["Lines"]) == 0 else max(len(l["Shapes"]) for l in m["Lines"]) for m in scenario["Progression"]["Levels"])

        for milestoneIndex,milestone in enumerate(scenario["Progression"]["Levels"]):

            shapeLines = []

            if milestone["Lines"] == []:
                milestone["Lines"].append({"Shapes":[]})

            for shapeLine in milestone["Lines"]:

                toFormatShapes = []

                for _ in range(shapeLine.get("StartingOffset",0)):
                    toFormatShapes.append({"shape":{"type":"none"},"reuse":"none"})

                for shapeIndex,shape in enumerate(shapeLine["Shapes"]):
                    curShape = {"type":"shape","code":shape["Shape"],"amount":shape["Amount"]}
                    if shapeIndex == len(shapeLine["Shapes"])-1:
                        if shapeLine.get("ReusedAtNextMilestone",False):
                            toFormatShapes.append({"shape":curShape,"reuse":"next"})
                        elif shapeLine.get("ReusedForPlayerLevel",False):
                            toFormatShapes.append({"shape":curShape,"reuse":"OL"})
                        elif shapeLine.get("ReusedAtSameMilestone",False):
                            toFormatShapes.extend([
                                {"shape":curShape,"reuse":"none"},
                                {"shape":{
                                    "type":"reuse",
                                    "value":"above" if shapeLine["ReusedAtSameMilestoneOffset"] < 0 else "below"
                                },"reuse":"none"}
                            ])
                        else:
                            toFormatShapes.append({"shape":curShape,"reuse":"none"})
                    else:
                        toFormatShapes.append({"shape":curShape,"reuse":"default"})

                toFormatShapes.extend([{"shape":{"type":"none"},"reuse":"none"}]*(maxMilestoneShapesPerLine-len(toFormatShapes)))

                curShapeLine = ""

                for toFormatShape in toFormatShapes:

                    if toFormatShape["shape"]["type"] == "none":
                        curShape = formats["milestoneShapeEmpty"].format()
                    elif toFormatShape["shape"]["type"] == "shape":
                        shapeCode = toFormatShape["shape"]["code"]
                        shapeCodeFileSafe = shapeCode.replace(":","-")
                        curShapeOutputPath = curMilestoneShapesOutputPath + MILESTONE_SHAPES_OUTPUT_FILE_NAME_FORMAT.format(
                            shapeCode = shapeCodeFileSafe
                        )
                        renderShape(shapeCode,scenario,curShapeOutputPath)
                        curShape = formats["milestoneShape"].format(
                            shapeImage = shapeCodeFileSafe,
                            shapeCode = shapeCode,
                            shapeAmount = toFormatShape["shape"]["amount"]
                        )
                    elif toFormatShape["shape"]["type"] == "reuse":
                        if toFormatShape["shape"]["value"] == "above":
                            curShape = formats["milestoneShapeReuseAbove"].format()
                        else:
                            curShape = formats["milestoneShapeReuseBelow"].format()

                    if toFormatShape["reuse"] == "none":
                        curReuse = formats["milestoneShapeReuseNone"].format()
                    elif toFormatShape["reuse"] == "default":
                        curReuse = formats["milestoneShapeReuse"].format()
                    elif toFormatShape["reuse"] == "next":
                        curReuse = formats["milestoneShapeReuseNext"].format()
                    elif toFormatShape["reuse"] == "OL":
                        curReuse = formats["milestoneShapeReuseOperatorLevel"].format()

                    curShapeLine += formats["milestoneShapeContainer"].format(
                        shape = curShape,
                        reuse = curReuse
                    )

                shapeLines.append(curShapeLine)

            milestones += formats["milestone"].format(
                numShapeLines = len(milestone["Lines"]),
                milestoneIndex = toAddMilestoneIndex + milestoneIndex,
                milestoneName = getTranslation(milestone["Title"]),
                milestoneDescription = getTooltipSafeString(getTranslation(milestone["Description"])),
                firstShapeLine = shapeLines[0],
                milestoneRewards = getFormattedRewards(milestone["Rewards"],scenario),
                unlockedUpgrades = formats["rewardsJoiner"].format().join(
                    getTranslation(upgrade["Title"])
                    for upgrade in scenario["Progression"]["SideUpgrades"]
                    if (milestone["Id"] in upgrade["RequiredUpgradeIds"]) and (upgrade["Title"] != "")
                ),
                unlockedTasks = formats["rewardsJoiner"].format().join(
                    getTranslation(taskGroup["Title"])
                    for taskGroup in scenario["Progression"]["SideQuestGroups"]
                    if milestone["Id"] in taskGroup["RequiredUpgradeIds"]
                ),
                shapeLines = "".join(formats["milestoneShapeLineContainer"].format(
                    shapeLine = sl
                ) for sl in shapeLines[1:])
            )

        milestoneLists += formats["milestoneList"].format(
            scenarioName = scenarioName,
            basedOnScenarioNote = milestoneBasedOnScenarioNote,
            milestones = milestones
        )

        #####

        bpShapes = ""
        curBPShapesOutputPath = BP_SHAPE_SHAPES_OUTPUT_PATH
        os.makedirs(curBPShapesOutputPath,exist_ok=True)

        for bpShape in scenario["Config"]["BlueprintCurrencyShapes"]:

            shapeCode = bpShape["Shape"]
            shapeCodeFileSafe = shapeCode.replace(":","-")
            curShapeOutputPath = curBPShapesOutputPath + BP_SHAPE_SHAPES_OUTPUT_FILE_NAME_FORMAT.format(
                shapeCode = shapeCodeFileSafe
            )
            renderShape(shapeCode,scenario,curShapeOutputPath)

            bpShapes += formats["bpShape"].format(
                shapeImage = shapeCodeFileSafe,
                shapeCode = shapeCode,
                pointsReward = bpShape["Amount"],
                milestoneRequired = getTranslation(f"research.{bpShape['RequiredUpgradeId']}.title")
            )

        bpShapeLists += formats["bpShapeList"].format(
            scenarioName = scenarioName,
            bpShapes = bpShapes
        )

    taskListsOutput = formats["taskListsPage"].format(
        autoGenMsg = autoGenMsg,
        taskLists = taskLists
    )
    with open(TASKS_OUTPUT_PATH,"w",encoding="utf-8") as f:
        f.write(taskListsOutput)

    milestoneListsOutput = formats["milestoneListsPage"].format(
        autoGenMsg = autoGenMsg,
        milestoneLists = milestoneLists
    )
    with open(MILESTONES_OUTPUT_PATH,"w",encoding="utf-8") as f:
        f.write(milestoneListsOutput)

    bpShapeListsOutput = formats["bpShapeListsPage"].format(
        autoGenMsg = autoGenMsg,
        bpShapeLists = bpShapeLists
    )
    with open(BP_SHAPES_OUTPUT_PATH,"w",encoding="utf-8") as f:
        f.write(bpShapeListsOutput)

    #####

    changelog = ""

    for versionChangelog in changelogRaw:

        entries = ""

        for entry in versionChangelog["Entries"]:

            if entry.startswith("[[") and entry.endswith("]]"):
                entries += formats["changelogCategory"].format(
                    categoryName = entry.removeprefix("[[").removesuffix("]]")
                )
            else:
                entries += formats["changelogEntry"].format(
                    entryText = entry
                )

        changelog += formats["changelogVersion"].format(
            versionName = versionChangelog["Version"],
            releaseDate = versionChangelog["Date"],
            entries = entries
        )

    changelogOutput = formats["changelogPage"].format(
        autoGenMsg = autoGenMsg,
        changelog = changelog
    )
    with open(CHANGELOG_OUTPUT_PATH,"w",encoding="utf-8") as f:
        f.write(changelogOutput)

if __name__ == "__main__":
    main()