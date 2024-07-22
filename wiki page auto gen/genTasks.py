import shapeViewer
import pygamePIL
import json
import os

GAME_VERSION_NAME = "0.0.4"

FORMAT_NAMES = [
    "firstTask",
    "taskBlueprintPointsReward",
    "task",
    "taskGroup",
    "taskList",
    "taskListsPage",
    "taskPlatformUnitsReward",
    "taskResearchPointsReward"
]

SCENARIO_PATHS = [
    "./gameFiles/OnboardingScenario.json",
    "./gameFiles/DefaultScenario.json",
    "./gameFiles/HardScenario.json",
    "./gameFiles/InsaneScenario.json",
    "./gameFiles/HexagonalScenario.json"
]
TRANSLATIONS_PATH = "./gameFiles/translations-en-US.json"

OUTPUT_PATH = "./taskListsOutput.txt"
SHAPES_OUTPUT_PATH_FORMAT = "./taskShapesOutput/{scenarioName}/"
SHAPES_OUTPUT_FILE_NAME_FORMAT = "Task-Shape-{shapeCode}-100.png"
SHAPE_SIZE = 100

FORMAT_PATHS = [f"./formats/{f}Format.txt" for f in FORMAT_NAMES]

def main() -> None:

    formats:dict[str,str] = {}
    for name,path in zip(FORMAT_NAMES,FORMAT_PATHS):
        with open(path,encoding="utf-8") as f:
            formats[name] = f.read()

    scenarios = []
    for path in SCENARIO_PATHS:
        with open(path,encoding="utf-8") as f:
            scenarios.append(json.load(f))

    with open(TRANSLATIONS_PATH,encoding="utf-8") as f:
        translations = json.load(f)

    def getTranslation(key:str) -> str:
        return translations[key.removeprefix("@")]

    taskLists = ""
    taskListLens = {}

    for scenario in scenarios:

        taskGroups = ""
        scenarioName = getTranslation(scenario["Title"])
        curOutputPath = SHAPES_OUTPUT_PATH_FORMAT.format(
            scenarioName = scenarioName
        )
        os.makedirs(curOutputPath,exist_ok=True)

        taskListLens[scenario["UniqueId"]] = len(scenario["Progression"]["SideQuestGroups"])
        if scenario.get("BasedOnScenarioId") is None:
            toAddTaskGroupIndex = 0
        else:
            toAddTaskGroupIndex = taskListLens[scenario["BasedOnScenarioId"]]

        for taskGroupIndex,taskGroup in enumerate(scenario["Progression"]["SideQuestGroups"],start=1):

            tasks = []

            for taskIndex,task in enumerate(taskGroup["SideQuests"],start=1):

                rewards = []

                for reward in task["Rewards"]:

                    if reward["$type"] == "ResearchPointsReward":
                        rewards.append(formats["taskResearchPointsReward"].format(
                            amount = reward["Amount"]
                        ))
                    elif reward["$type"] == "BlueprintCurrencyReward":
                        rewards.append(formats["taskBlueprintPointsReward"].format(
                            amount = reward["Amount"]
                        ))
                    elif reward["$type"] == "ChunkLimitReward":
                        rewards.append(formats["taskPlatformUnitsReward"].format(
                            amount = round(reward["Amount"]*(scenario["Config"]["BaseChunkLimitMultiplier"]/100))
                        ))

                shapeCode:str = task["Costs"][0]["Shape"]
                shapeCodeFileSafe = shapeCode.replace(":","-")

                curShapeOutputPath = curOutputPath+SHAPES_OUTPUT_FILE_NAME_FORMAT.format(
                    shapeCode = shapeCodeFileSafe
                )
                if not os.path.exists(curShapeOutputPath):
                    shapeRendered = shapeViewer.renderShape(shapeCode,SHAPE_SIZE,shapeConfig=(
                        shapeViewer.SHAPE_CONFIG_HEX
                        if scenario["Config"]["ShapesConfigurationId"] == "DefaultShapesHexagonalConfiguration" else
                        shapeViewer.SHAPE_CONFIG_QUAD
                    ))
                    pygamePIL.image_save(shapeRendered,curShapeOutputPath)

                tasks.append((
                    taskIndex,
                    shapeCodeFileSafe,
                    shapeCode,
                    task["Costs"][0]["Amount"],
                    "<br/>".join(rewards)
                ))

            taskGroups += formats["taskGroup"].format(
                firstTask = formats["firstTask"].format(
                    numTasks = len(taskGroup["SideQuests"]),
                    taskGroupIndex = toAddTaskGroupIndex + taskGroupIndex,
                    taskGroupName = getTranslation(taskGroup["Title"]),
                    taskShapeImage = tasks[0][1],
                    taskShapeCode = tasks[0][2],
                    taskShapeAmount = tasks[0][3],
                    taskRewards = tasks[0][4],
                    taskGroupMilestoneRequired = getTranslation(f"@research.{taskGroup['RequiredUpgradeIds'][0]}.title")
                ),
                tasks = "".join(formats["task"].format(
                    taskIndex = t[0],
                    taskShapeImage = t[1],
                    taskShapeCode = t[2],
                    taskShapeAmount = t[3],
                    taskRewards = t[4],
                ) for t in tasks[1:])
            )

        taskLists += formats["taskList"].format(
            scenarioName = scenarioName,
            taskGroups = taskGroups
        )

    output = formats["taskListsPage"].format(
        gameVersion = GAME_VERSION_NAME,
        taskLists = taskLists
    )

    with open(OUTPUT_PATH,"w",encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    main()