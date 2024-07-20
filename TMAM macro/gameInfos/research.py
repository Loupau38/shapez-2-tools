import globalInfos
import json

class Node:
    def __init__(self,id:str,title:str,desc:str,goalShape:str,goalAmount:int,unlocks:list[str]) -> None:
        self.id = id
        self.title = title
        self.desc = desc
        self.goalShape = goalShape
        self.goalAmount = goalAmount
        self.unlocks = unlocks

class Level:
    def __init__(self,milestone:Node,sideGoals:list[Node]) -> None:
        self.milestone = milestone
        self.sideGoals = sideGoals

def _loadResearchTree() -> tuple[list[Level],str]:

    with open(globalInfos.GI_RESEARCH_PATH,encoding="utf-8") as f:
        researchRaw = json.load(f)

    treeVersion = researchRaw["GameVersion"]

    reserachTree = []

    for levelRaw in researchRaw["Levels"]:
        reserachTree.append(Level(
            Node(*levelRaw["Node"].values()),
            [Node(*sg.values()) for sg in levelRaw["SideGoals"]]
        ))

    return reserachTree, treeVersion

reserachTree, treeVersion = _loadResearchTree()