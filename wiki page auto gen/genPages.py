import shapez2
import os
import math

FORMATS_PATH = "./formats"

SCENARIOS_ORDER = [
    "onboarding",
    "default",
    "hard",
    "insane",
    "hexagonal"
]
# CHANGELOG_PATH = "./gameFiles/Changelog.json"

TASKS_OUTPUT_PATH = "./outputTaskLists.txt"

MILESTONES_OUTPUT_PATH = "./outputMilestoneLists.txt"

BP_SHAPES_OUTPUT_PATH = "./outputBpShapeLists.txt"

OL_REWARDS_OUTPUT_PATH = "./outputOLRewardLists.txt"
OL_SHAPE_BADGES_OUTPUT_PATH = "./outputOLShapeBadgeLists.txt"
OL_GOAL_LINES_OUTPUT_PATH = "./outputOLGoalLineLists.txt"

# CHANGELOG_OUTPUT_PATH = "./outputChangelog.txt"

MAX_OL_GOAL_LINE_COST = 2_147_482_600

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

def parseAndFormatCurrencyRewards(rewards:shapez2.research.Rewards,scenario:shapez2.research.Scenario) -> list[str]:
    output = []
    for rewardAmount,formatName,multiplier in [
        (rewards.researchPoints,"rewardResearchPoints",100),
        (rewards.blueprintCurrency,"rewardBlueprintPoints",scenario.researchConfig.baseBlueprintRewardMultiplier),
        # platform limit shown ingame is divided by 2
        (rewards.chunkLimit,"rewardPlatformUnits",scenario.researchConfig.baseChunkLimitMultiplier/2)
    ]:
        actualAmount = math.floor(rewardAmount*(multiplier/100))
        if actualAmount != 0:
            output.append(formats[formatName].format(
                amount = f"{actualAmount:,}"
            ))
    return output

def getFormattedRewards(rawRewards:shapez2.research.Rewards,scenario:shapez2.research.Scenario) -> str:

    rewards = []
    seenBuildingNames = []
    seenPlatformNames = []

    for building in rawRewards.buildingVariants:
        buildingName = building.title.translate().renderToStringNoFeatures()
        if buildingName not in seenBuildingNames:
            rewards.append(formats["rewardBuilding"].format(
                building = buildingName
            ))
            seenBuildingNames.append(buildingName)

    for platformGroup in rawRewards.islandGroups:
        platformName = platformGroup.title.translate().renderToStringNoFeatures()
        if platformName not in seenPlatformNames:
            rewards.append(formats["rewardPlatform"].format(
                platform = platformName
            ))
            seenPlatformNames.append(platformName)

    for wikiEntry in rawRewards.wikiEntries:
        rewards.append(formats["rewardKnowledgePanelEntry"].format(
            entry = shapez2.translations.TranslationString(f"wiki.{wikiEntry}.title").translate().renderToStringNoFeatures()
        ))

    for mechanic in rawRewards.mechanics:
        rewards.append(formats["rewardMechanic"].format(
            mechanic = mechanic.title.translate().renderToStringNoFeatures()
        ))

    rewards.extend(parseAndFormatCurrencyRewards(rawRewards,scenario))

    return formats["rewardsJoiner"].format().join(rewards)

def getTooltipSafeString(string:str) -> str:
    return string.replace("<span class=\"gl\">","").replace("</span>","").replace("\n"," ")

def OLGoalLineAmountFormula(level:int,startingAmount:int,growth:int) -> int:
    """level in [0;+inf["""
    amount = startingAmount * ((1+(growth/100))**level)
    amount = min(amount,(2**31)-1001)
    return round(amount/100) * 100

def main() -> None:

    # with open(CHANGELOG_PATH,encoding="utf-8") as f:
    #     changelogRaw:list[dict[str,str|list[str]]] = json.load(f)

    autoGenMsg = formats["autoGenMsg"].format(
        gameVersion = shapez2.versions.GAME_VERSIONS.get(shapez2.versions.LATEST_GAME_VERSION)[-1]
    )

    scenarioNames = {}

    taskLists = ""

    milestoneLists = ""

    bpShapeLists = ""

    OLRewardLists = ""
    OLShapeBadgesNoDuplicates:list[tuple[list[str],tuple[int,str,list[shapez2.gameObjects.Shape]]]] = []
    OLGoalLineLists = ""

    for scenarioPartialId in SCENARIOS_ORDER:

        scenarioId = f"{scenarioPartialId}-scenario"
        scenario = shapez2.research.ingameScenarios[scenarioId]
        scenarioName = scenario.title.translate().renderToStringNoFeatures()
        scenarioNames[scenarioId] = scenarioName
        if scenario.researchConfig.shapesConfig == shapez2.ingameData.QUAD_SHAPES_CONFIG:
            curShapesConfig = "quad"
        elif scenario.researchConfig.shapesConfig == shapez2.ingameData.HEX_SHAPES_CONFIG:
            curShapesConfig = "hex"
        else:
            raise ValueError("Unknown shapes config")

        if scenarioId == "onboarding-scenario":
            onboardingMilestones = [m.id for m in scenario.milestones]
            onboardingTasks = [t.title.getRaw() for t in scenario.taskGroups]

        # if the scenario has initially unlocked upgrades, deduce that it is based on another scenario
        if (
            (
                (len(scenario.researchConfig.initiallyUnlockedMilestones) == 0)
                or (
                    (len(scenario.researchConfig.initiallyUnlockedMilestones) == 1)
                    and (scenario.researchConfig.initiallyUnlockedMilestones[0].id == "RNInitial")
                )
            )
            and (len(scenario.researchConfig.initiallyUnlockedSideTasks) == 0)
            and (len(scenario.researchConfig.initiallyUnlockedSideUpgrades) == 0)
        ):
            basedOnScenario = False
            taskBasedOnScenarioNote = ""
            milestoneBasedOnScenarioNote = ""
        else:
            basedOnScenario = True
            # kind of hack, could be based on a different scenario
            basedOnScenarioName = (
                shapez2.translations.TranslationString("scenario.onboarding.title")
                .translate().renderToStringNoFeatures()
            )
            taskBasedOnScenarioNote = formats["taskListBasedOnScenarioNote"].format(
                basedOnScenario = basedOnScenarioName
            )
            milestoneBasedOnScenarioNote = formats["milestoneListBasedOnScenarioNote"].format(
                basedOnScenario = basedOnScenarioName
            )

        #####

        taskGroups = ""

        for taskGroupIndex,taskGroup in enumerate(scenario.taskGroups,start=1):

            if basedOnScenario and (taskGroup.title.getRaw() in onboardingTasks):
                continue # skip task group as it's from another scenario

            tasks = []

            for taskIndex,task in enumerate(taskGroup.tasks,start=1):

                tasks.append(formats["task"].format(
                    taskIndex = taskIndex,
                    taskShapeCode = task.costs[0].shape.toShapeCode(),
                    taskShapesConfig = curShapesConfig,
                    taskShapeAmount = task.costs[0].amount,
                    taskRewards = getFormattedRewards(task.rewards,scenario)
                ))

            taskGroups += formats["taskGroup"].format(
                numTasks = len(taskGroup.tasks),
                taskGroupIndex = taskGroupIndex,
                taskGroupName = taskGroup.title.translate().renderToStringNoFeatures(),
                firstTask = tasks[0],
                taskGroupMilestoneRequired = (
                    "/"
                    if len(taskGroup.requirements.requiredMilestones) == 0 else
                    taskGroup.requirements.requiredMilestones[0].title.translate().renderToStringNoFeatures()
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
            if len(m.lines) == 0 else
            max(
                len(l.shapes) for l in m.lines
            )
            for m in scenario.milestones
        )

        for milestoneIndex,milestone in enumerate(scenario.milestones):

            if basedOnScenario and (milestone.id in onboardingMilestones):
                continue # skip milestone as it's from another scenario

            rawShapeLines = milestone.lines.copy()
            shapeLines = []

            if rawShapeLines == []:
                rawShapeLines.append(shapez2.research.MilestoneShapeLine(
                    shapez2.research.MilestoneShapeLineReuseType.none,
                    0,
                    0,
                    []
                ))

            for shapeLine in rawShapeLines:

                toFormatShapes = []

                for _ in range(shapeLine.startingOffset):
                    toFormatShapes.append({"shape":{"type":"none"},"reuse":"none"})

                for shapeIndex,shape in enumerate(shapeLine.shapes):
                    curShape = {"type":"shape","code":shape.shape.toShapeCode(),"amount":shape.amount}
                    if shapeIndex == len(shapeLine.shapes)-1:
                        if shapeLine.reuseType == shapez2.research.MilestoneShapeLineReuseType.nextMilestone:
                            toFormatShapes.append({"shape":curShape,"reuse":"next"})
                        elif shapeLine.reuseType == shapez2.research.MilestoneShapeLineReuseType.operatorLevel:
                            toFormatShapes.append({"shape":curShape,"reuse":"OL"})
                        elif shapeLine.reuseType == shapez2.research.MilestoneShapeLineReuseType.sameMilestone:
                            toFormatShapes.extend([
                                {"shape":curShape,"reuse":"none"},
                                {"shape":{
                                    "type":"reuse",
                                    "value":"above" if shapeLine.reuseOffset < 0 else "below"
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

            milestones += formats["milestone"].format(
                numShapeLines = len(rawShapeLines),
                milestoneIndex = milestoneIndex,
                milestoneName = milestone.title.translate().renderToStringNoFeatures(),
                milestoneDescription = getTooltipSafeString(milestone.description.translate().renderToStringNoFeatures()),
                firstShapeLine = shapeLines[0],
                milestoneRewards = getFormattedRewards(milestone.rewards,scenario),
                unlockedUpgrades = formats["rewardsJoiner"].format().join(
                    upgradeTitle
                    for upgrade in (
                        scenario.sideUpgrades
                        + scenario.linearUpgrades
                    )
                    if (
                        (
                            (milestone in upgrade.requirements.requiredMilestones)
                            or any(milestone in m.unlockedBy for m in upgrade.requirements.requiredMechanics)
                        )
                        and ((upgradeTitle:=upgrade.title.translate().renderToStringNoFeatures()) != "")
                    )
                ),
                unlockedTasks = formats["rewardsJoiner"].format().join(
                    taskGroup.title.translate().renderToStringNoFeatures()
                    for taskGroup in scenario.taskGroups
                    if (
                        (milestone in taskGroup.requirements.requiredMilestones)
                        or any(milestone in m.unlockedBy for m in taskGroup.requirements.requiredMechanics)
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

        for bpShape in scenario.researchConfig.blueprintCurrencyShapes:

            if len(bpShape.requirements.requiredMechanics) != 0:
                raise ValueError("BP shapes unlocked with mechanics unsupported")
            if len(bpShape.requirements.requiredSideUpgrades) != 0:
                raise ValueError("BP shapes unlocked with side upgrades unsupported")
            if len(bpShape.requirements.requiredFutureUpgrades) != 0:
                raise ValueError("BP shapes unlocked with future upgrades unsupported")
            if len(bpShape.requirements.requiredMilestones) > 1:
                raise ValueError("BP shapes unlocked with multiple milestones unsupported")

            bpShapes += formats["bpShape"].format(
                shapeCode = bpShape.shape.toShapeCode(),
                shapesConfig = curShapesConfig,
                pointsReward = bpShape.currencyAmount,
                milestoneRequired = (
                    "/"
                    if len(bpShape.requirements.requiredMilestones) == 0 else
                    bpShape.requirements.requiredMilestones[0].title.translate().renderToStringNoFeatures()
                )
            )

        bpShapeLists += formats["bpShapeList"].format(
            scenarioName = scenarioName,
            bpShapes = bpShapes
        )

        #####

        playerLevelConfig = scenario.operatorLevelConfig
        if playerLevelConfig.goalLines != []: # only consider scenarios with OL reachable

            OLRewards = ""
            scenarioOLRewards = list(reversed(playerLevelConfig.rewards))

            for i,OLReward in enumerate(scenarioOLRewards):

                if i+1 < len(scenarioOLRewards):
                    levels = formats["levelRange"].format(
                        levelStart = OLReward.minLevel,
                        levelEnd = scenarioOLRewards[i+1].minLevel - 1
                    )
                else:
                    levels = formats["levelThreshold"].format(
                        levelStart = OLReward.minLevel
                    )

                formattedRewards = parseAndFormatCurrencyRewards(OLReward.rewards,scenario)

                OLRewards += formats["OLReward"].format(
                    levels = levels,
                    RPRewards = formattedRewards[0],
                    BPRewards = formattedRewards[1],
                    PURewards = formattedRewards[2]
                )

            OLRewardLists += formats["OLRewardList"].format(
                scenarioName = scenarioName,
                OLRewards = OLRewards
            )

            #####

            newShapeBadgeList = True
            for scenarioIds,(shapeInterval,_,shapeBadges) in OLShapeBadgesNoDuplicates:
                if (
                    (playerLevelConfig.badgeShapes == shapeBadges)
                    and (playerLevelConfig.badgeShapeInterval == shapeInterval)
                ):
                    newShapeBadgeList = False
                    scenarioIds.append(scenarioId)
                    break

            if newShapeBadgeList:
                OLShapeBadgesNoDuplicates.append(([scenarioId],(
                    playerLevelConfig.badgeShapeInterval,
                    curShapesConfig,
                    playerLevelConfig.badgeShapes
                )))

            #####

            OLGoalLines = ""

            for goalLine in playerLevelConfig.goalLines:

                level = 0
                while True:
                    cost = OLGoalLineAmountFormula(
                        level,
                        goalLine.startingAmount,
                        goalLine.growth
                    )
                    if cost >= MAX_OL_GOAL_LINE_COST:
                        break
                    level += 1

                if goalLine.type == shapez2.research.OperatorLevelGoalLineType.randomCrystals:
                    shapeInfo = formats["OLGoalLineRandomShapeCrystals"].format()
                elif goalLine.type == shapez2.research.OperatorLevelGoalLineType.randomNoCrystals:
                    shapeInfo = formats["OLGoalLineRandomShape"].format()
                else:
                    shapeInfo = formats["OLGoalLineShape"].format(
                        shapeCode = goalLine.shape.toShapeCode(),
                        shapesConfig = curShapesConfig
                    )

                if len(goalLine.requirements.requiredMechanics) != 0:
                    raise ValueError("OL goal line unlocked with mechanics unsupported")
                if len(goalLine.requirements.requiredSideUpgrades) != 0:
                    raise ValueError("OL goal line unlocked with side upgrades unsupported")
                if len(goalLine.requirements.requiredFutureUpgrades) != 0:
                    raise ValueError("OL goal line unlocked with future upgrades unsupported")
                if len(goalLine.requirements.requiredMilestones) > 1:
                    raise ValueError("OL goal line unlocked with multiple milestones unsupported")

                OLGoalLines += formats["OLGoalLine"].format(
                    shapeInfo = shapeInfo,
                    milestoneRequired = (
                        "/"
                        if len(goalLine.requirements.requiredMilestones) == 0 else
                        goalLine.requirements.requiredMilestones[0].title.translate().renderToStringNoFeatures()
                    ),
                    startingAmount = goalLine.startingAmount,
                    growth = goalLine.growth,
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
                shapeCode = shapeBadge.toShapeCode(),
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