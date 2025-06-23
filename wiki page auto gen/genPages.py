import json
import os
import math

GAME_VERSION_NAME = "0.1.1"

FORMATS_PATH = "./formats"

SCENARIO_PATHS = [
    "./gameFiles/onboarding-scenario.json",
    "./gameFiles/default-scenario.json",
    "./gameFiles/hard-scenario.json",
    "./gameFiles/insane-scenario.json",
    "./gameFiles/hexagonal-scenario.json"
]
TRANSLATIONS_PATH = "./gameFiles/translations-en-US.json"
# CHANGELOG_PATH = "./gameFiles/Changelog.json"

TASKS_OUTPUT_PATH = "./outputTaskLists.txt"

MILESTONES_OUTPUT_PATH = "./outputMilestoneLists.txt"

BP_SHAPES_OUTPUT_PATH = "./outputBpShapeLists.txt"

OL_REWARDS_OUTPUT_PATH = "./outputOLRewardLists.txt"
OL_SHAPE_BADGES_OUTPUT_PATH = "./outputOLShapeBadgeLists.txt"
OL_GOAL_LINES_OUTPUT_PATH = "./outputOLGoalLineLists.txt"

# CHANGELOG_OUTPUT_PATH = "./outputChangelog.txt"

MAX_OL_GOAL_LINE_COST = 2_147_482_600

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

def loadFormats(folder:str) -> dict[str,str]:
    formats:dict[str,str] = {}
    for dirEntry in os.scandir(folder):
        if dirEntry.is_dir():
            formats.update(loadFormats(dirEntry.path))
        else:
            with open(dirEntry.path,encoding="utf-8") as f:
                formats[dirEntry.name.removesuffix(".txt")] = f.read()
    return formats
formats = loadFormats(FORMATS_PATH)

def parseAndFormatCurrencyReward(reward:dict[str,str|int],scenario:dict) -> str:
    for rewardType,formatName,multiplier in [
        ("ResearchPointsReward","rewardResearchPoints",100),
        ("BlueprintCurrencyReward","rewardBlueprintPoints",scenario["ResearchConfig"]["BaseBlueprintRewardMultiplier"]),
        # platform limit shown ingame is divided by 2
        ("ChunkLimitReward","rewardPlatformUnits",scenario["ResearchConfig"]["BaseChunkLimitMultiplier"]/2)
    ]:
        if reward["$type"] == rewardType:
            actualAmount = math.floor(reward["Amount"]*(multiplier/100))
            return formats[formatName].format(
                amount = f"{actualAmount:,}"
            )
    raise ValueError("unknown reward type")

def getFormattedRewards(rawRewards:list[dict[str,str|int]],scenario:dict) -> str:

    rewards = []
    seenBuildingNames = []
    seenPlatformNames = []

    for reward in rawRewards:

        if reward["$type"] in ("ResearchPointsReward","BlueprintCurrencyReward","ChunkLimitReward"):
            rewards.append(parseAndFormatCurrencyReward(reward,scenario))
        elif reward["$type"] == "BuildingReward":
            buildingName = getTranslation(f"building-variant.{reward["BuildingDefinitionGroupId"]}.title")
            if buildingName not in seenBuildingNames:
                rewards.append(formats["rewardBuilding"].format(
                    building = buildingName
                ))
                seenBuildingNames.append(buildingName)
        elif reward["$type"] == "IslandGroupReward":
            platformName = getTranslation(f"island-group.{reward["GroupId"]}.title")
            if platformName not in seenPlatformNames:
                rewards.append(formats["rewardPlatform"].format(
                    platform = platformName
                ))
                seenPlatformNames.append(platformName)
        elif reward["$type"] == "WikiEntryReward":
            rewards.append(formats["rewardKnowledgePanelEntry"].format(
                entry = getTranslation(f"wiki.{reward["EntryId"]}.title")
            ))
        elif reward["$type"] == "MechanicReward":
            rewards.append(formats["rewardMechanic"].format(
                # mechanic names are defined in scenarios, but they all use the same 'research.<id>.title' structure
                mechanic = getTranslation(f"research.{reward["MechanicId"]}.title")
            ))
        else:
            raise ValueError(f"Unknown reward type : {reward["$type"]}")

    return formats["rewardsJoiner"].format().join(rewards)

def getTooltipSafeString(string:str) -> str:
    return string.replace("<span class=\"gl\">","").replace("</span>","").replace("\n"," ")

def OLGoalLineAmountFormula(level:int,startingAmount:int,growth:int) -> int:
    """level in [0;+inf["""
    amount = startingAmount * ((1+(growth/100))**level)
    amount = min(amount,(2**31)-1001)
    return round(amount/100) * 100

def main() -> None:

    scenarios = []
    for path in SCENARIO_PATHS:
        with open(path,encoding="utf-8") as f:
            scenarios.append(json.load(f))

    # with open(CHANGELOG_PATH,encoding="utf-8") as f:
    #     changelogRaw:list[dict[str,str|list[str]]] = json.load(f)

    autoGenMsg = formats["autoGenMsg"].format(
        gameVersion = GAME_VERSION_NAME
    )

    scenarioNames = {}

    taskLists = ""

    milestoneLists = ""

    bpShapeLists = ""

    OLRewardLists = ""
    OLShapeBadgesNoDuplicates:list[tuple[list[str],tuple[int,str,list[str]]]] = []
    OLGoalLineLists = ""

    for scenario in scenarios:

        scenarioId = scenario["UniqueId"]
        scenarioName = getTranslation(scenario["Title"])
        scenarioNames[scenarioId] = scenarioName
        if scenario["ResearchConfig"]["ShapesConfigurationId"] == "DefaultShapesQuadConfiguration":
            curShapesConfig = "quad"
        elif scenario["ResearchConfig"]["ShapesConfigurationId"] == "DefaultShapesHexagonalConfiguration":
            curShapesConfig = "hex"
        else:
            raise ValueError("Unknown shapes config")

        if scenarioId == "onboarding-scenario":
            onboardingMilestones = [m["Definition"]["Id"] for m in scenario["Progression"]["Levels"]["Levels"]]
            onboardingTasks = [t["Title"] for t in scenario["Progression"]["SideQuestGroups"]["SideQuestGroups"]]

        # if the scenario has initially unlocked upgrades, deduce that it is based on another scenario
        initiallyUnlockedUpgrades = scenario["ResearchConfig"]["InitiallyUnlockedUpgrades"]
        if initiallyUnlockedUpgrades in ([],["RNInitial"]):
            basedOnScenario = False
            taskBasedOnScenarioNote = ""
            milestoneBasedOnScenarioNote = ""
        else:
            basedOnScenario = True
            # kind of hack, could be based on a different scenario
            basedOnScenarioName = getTranslation("@scenario.onboarding.title")
            taskBasedOnScenarioNote = formats["taskListBasedOnScenarioNote"].format(
                basedOnScenario = basedOnScenarioName
            )
            milestoneBasedOnScenarioNote = formats["milestoneListBasedOnScenarioNote"].format(
                basedOnScenario = basedOnScenarioName
            )

        #####

        taskGroups = ""

        for taskGroupIndex,taskGroup in enumerate(scenario["Progression"]["SideQuestGroups"]["SideQuestGroups"],start=1):

            if basedOnScenario and (taskGroup["Title"] in onboardingTasks):
                continue # skip task group as it's from another scenario

            tasks = []

            for taskIndex,task in enumerate(taskGroup["SideQuests"],start=1):

                tasks.append(formats["task"].format(
                    taskIndex = taskIndex,
                    taskShapeCode = task["Costs"][0]["Shape"],
                    taskShapesConfig = curShapesConfig,
                    taskShapeAmount = task["Costs"][0]["Amount"],
                    taskRewards = getFormattedRewards(task["Rewards"],scenario)
                ))

            taskGroups += formats["taskGroup"].format(
                numTasks = len(taskGroup["SideQuests"]),
                taskGroupIndex = taskGroupIndex,
                taskGroupName = getTranslation(taskGroup["Title"]),
                firstTask = tasks[0],
                taskGroupMilestoneRequired = (
                    "/"
                    if len(taskGroup["RequiredUpgradeIds"]) == 0 else
                    getTranslation(f"research.{taskGroup["RequiredUpgradeIds"][0]}.title")
                ),
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
        maxMilestoneShapesPerLine = max(
            0
            if len(m["Lines"]["Lines"]) == 0 else
            max(
                len(l["Shapes"]) for l in m["Lines"]["Lines"]
            )
            for m in scenario["Progression"]["Levels"]["Levels"]
        )

        for milestoneIndex,milestone in enumerate(scenario["Progression"]["Levels"]["Levels"]):

            if basedOnScenario and (milestone["Definition"]["Id"] in onboardingMilestones):
                continue # skip milestone as it's from another scenario

            shapeLines = []

            if milestone["Lines"]["Lines"] == []:
                milestone["Lines"]["Lines"].append({"Shapes":[]})

            for shapeLine in milestone["Lines"]["Lines"]:

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
                        curShape = formats["milestoneShape"].format(
                            shapeCode = toFormatShape["shape"]["code"],
                            shapesConfig = curShapesConfig,
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

            unlockedMechanics = [r["MechanicId"] for r in milestone["Rewards"]["Rewards"] if r["$type"] == "MechanicReward"]

            milestones += formats["milestone"].format(
                numShapeLines = len(milestone["Lines"]["Lines"]),
                milestoneIndex = milestoneIndex,
                milestoneName = getTranslation(milestone["Definition"]["Title"]),
                milestoneDescription = getTooltipSafeString(getTranslation(milestone["Definition"]["Description"])),
                firstShapeLine = shapeLines[0],
                milestoneRewards = getFormattedRewards(milestone["Rewards"]["Rewards"],scenario),
                unlockedUpgrades = formats["rewardsJoiner"].format().join(
                    getTranslation(upgrade["Title"])
                    for upgrade in (
                        scenario["Progression"]["SideUpgrades"]["SideUpgrades"]
                        + scenario["Progression"]["LinearUpgrades"]["LinearUpgrades"]
                    )
                    if (
                        (
                            (milestone["Definition"]["Id"] in upgrade["RequiredUpgradeIds"])
                            or any(m in upgrade["RequiredMechanicIds"] for m in unlockedMechanics)
                        )
                        and (upgrade["Title"] != "")
                    )
                ),
                unlockedTasks = formats["rewardsJoiner"].format().join(
                    getTranslation(taskGroup["Title"])
                    for taskGroup in scenario["Progression"]["SideQuestGroups"]["SideQuestGroups"]
                    if (
                        (milestone["Definition"]["Id"] in taskGroup["RequiredUpgradeIds"])
                        or any(m in taskGroup["RequiredMechanicIds"] for m in unlockedMechanics)
                    )
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

        for bpShape in scenario["ResearchConfig"]["BlueprintCurrencyShapes"]:

            if len(bpShape["RequiredMechanicIds"]) != 0:
                raise ValueError("BP shapes unlocked with mechanics unsupported")
            if len(bpShape["RequiredUpgradeIds"]) > 1:
                raise ValueError("BP shapes unlocked with multiple upgrades unsupported")

            bpShapes += formats["bpShape"].format(
                shapeCode = bpShape["Shape"],
                shapesConfig = curShapesConfig,
                pointsReward = bpShape["Amount"],
                milestoneRequired = (
                    "/"
                    if len(bpShape["RequiredUpgradeIds"]) == 0 else
                    getTranslation(f"research.{bpShape["RequiredUpgradeIds"][0]}.title")
                )
            )

        bpShapeLists += formats["bpShapeList"].format(
            scenarioName = scenarioName,
            bpShapes = bpShapes
        )

        #####

        playerLevelConfig = scenario["PlayerLevelConfig"]
        if playerLevelConfig["GoalLines"] != []: # only consider scenarios with OL reachable

            OLRewards = ""
            scenarioOLRewards = list(reversed(playerLevelConfig["Rewards"]))

            for i,OLReward in enumerate(scenarioOLRewards):

                if i+1 < len(scenarioOLRewards):
                    levels = formats["levelRange"].format(
                        levelStart = OLReward["MinimumLevel"],
                        levelEnd = scenarioOLRewards[i+1]["MinimumLevel"] - 1
                    )
                else:
                    levels = formats["levelThreshold"].format(
                        levelStart = OLReward["MinimumLevel"]
                    )

                formattedRewards = {
                    reward["$type"] : parseAndFormatCurrencyReward(reward,scenario)
                    for reward in OLReward["Rewards"]
                }

                OLRewards += formats["OLReward"].format(
                    levels = levels,
                    PURewards = formattedRewards["ChunkLimitReward"],
                    BPRewards = formattedRewards["BlueprintCurrencyReward"],
                    RPRewards = formattedRewards["ResearchPointsReward"]
                )

            OLRewardLists += formats["OLRewardList"].format(
                scenarioName = scenarioName,
                OLRewards = OLRewards
            )

            #####

            newShapeBadgeList = True
            for scenarioIds,(shapeInterval,_,shapeBadges) in OLShapeBadgesNoDuplicates:
                if (
                    (playerLevelConfig["IconicLevelShapes"]["LevelShapes"] == shapeBadges)
                    and (playerLevelConfig["IconicLevelShapeInterval"] == shapeInterval)
                ):
                    newShapeBadgeList = False
                    scenarioIds.append(scenarioId)
                    break

            if newShapeBadgeList:
                OLShapeBadgesNoDuplicates.append(([scenarioId],(
                    playerLevelConfig["IconicLevelShapeInterval"],
                    curShapesConfig,
                    playerLevelConfig["IconicLevelShapes"]["LevelShapes"]
                )))

            #####

            OLGoalLines = ""

            for goalLine in playerLevelConfig["GoalLines"]:

                level = 0
                while True:
                    cost = OLGoalLineAmountFormula(
                        level,
                        goalLine["StartingAmount"],
                        goalLine["ExponentialGrowthPercentPerLevel"]
                    )
                    if cost >= MAX_OL_GOAL_LINE_COST:
                        break
                    level += 1

                if goalLine.get("Randomized"):
                    if goalLine.get("RandomizedUseCrystals"):
                        shapeInfo = formats["OLGoalLineRandomShapeCrystals"].format()
                    else:
                        shapeInfo = formats["OLGoalLineRandomShape"].format()
                else:
                    shapeInfo = formats["OLGoalLineShape"].format(
                        shapeCode = goalLine["Shape"],
                        shapesConfig = curShapesConfig
                    )

                if len(goalLine["RequiredMechanicIds"]) != 0:
                    raise ValueError("OL goal line unlocked with mechanics unsupported")
                if len(bpShape["RequiredUpgradeIds"]) > 1:
                    raise ValueError("OL goal line unlocked with multiple upgrades unsupported")

                OLGoalLines += formats["OLGoalLine"].format(
                    shapeInfo = shapeInfo,
                    milestoneRequired = (
                        "/"
                        if len(goalLine["RequiredUpgradeIds"]) == 0 else
                        getTranslation(f"research.{goalLine["RequiredUpgradeIds"][0]}.title")
                    ),
                    startingAmount = goalLine["StartingAmount"],
                    growth = goalLine["ExponentialGrowthPercentPerLevel"],
                    maxCostAtLevel = level
                )

            OLGoalLineLists += formats["OLGoalLineList"].format(
                scenarioName = scenarioName,
                OLGoalLines = OLGoalLines
            )

    #####

    OLShapeBadgeLists = ""

    for scenarioIds,(shapeInterval,shapesConfig,shapeBadges) in OLShapeBadgesNoDuplicates:

        OLShapeBadges = ""

        for i,shapeBadge in enumerate(shapeBadges):

            if i+1 == len(shapeBadges):
                levels = formats["levelThreshold"].format(
                    levelStart = i
                )
            elif shapeInterval == 1:
                levels = formats["levelSingle"].format(
                    level = i
                )
            else:
                levels = formats["levelRange"].format(
                    levelStart = i,
                    levelEnd = i + shapeInterval - 1
                )

            OLShapeBadges += formats["OLShapeBadge"].format(
                levels = levels,
                shapeCode = shapeBadge,
                shapesConfig = shapesConfig
            )

        OLShapeBadgeLists += formats["OLShapeBadgeList"].format(
            scenarioNames = ", ".join(scenarioNames[id] for id in scenarioIds),
            OLShapeBadges = OLShapeBadges
        )

    #####

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

    OLRewardListsOutput = formats["OLRewardListsPage"].format(
        autoGenMsg = autoGenMsg,
        OLRewardLists = OLRewardLists
    )
    with open(OL_REWARDS_OUTPUT_PATH,"w",encoding="utf-8") as f:
        f.write(OLRewardListsOutput)

    OLShapeBadgeListsOutput = formats["OLShapeBadgeListsPage"].format(
        autoGenMsg = autoGenMsg,
        OLShapeBadgeLists = OLShapeBadgeLists
    )
    with open(OL_SHAPE_BADGES_OUTPUT_PATH,"w",encoding="utf-8") as f:
        f.write(OLShapeBadgeListsOutput)

    OLGoalLineListsOutput = formats["OLGoalLineListsPage"].format(
        autoGenMsg = autoGenMsg,
        OLGoalLineLists = OLGoalLineLists
    )
    with open(OL_GOAL_LINES_OUTPUT_PATH,"w",encoding="utf-8") as f:
        f.write(OLGoalLineListsOutput)

    #####

    # changelog = ""

    # for versionChangelog in changelogRaw:

    #     entries = ""

    #     for entry in versionChangelog["Entries"]:

    #         if entry.startswith("[[") and entry.endswith("]]"):
    #             entries += formats["changelogCategory"].format(
    #                 categoryName = entry.removeprefix("[[").removesuffix("]]")
    #             )
    #         else:
    #             entries += formats["changelogEntry"].format(
    #                 entryText = entry
    #             )

    #     changelog += formats["changelogVersion"].format(
    #         versionName = versionChangelog["Version"],
    #         releaseDate = versionChangelog["Date"],
    #         entries = entries
    #     )

    # changelogOutput = formats["changelogPage"].format(
    #     autoGenMsg = autoGenMsg,
    #     changelog = changelog
    # )
    # with open(CHANGELOG_OUTPUT_PATH,"w",encoding="utf-8") as f:
    #     f.write(changelogOutput)

if __name__ == "__main__":
    main()