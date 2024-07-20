import globalInfos
import utils
import gameInfos.common
import gameInfos.translations
import json

class InternalVariantList:
    def __init__(self,id:str,title:str) -> None:
        self.id = id
        self.title = title
        self.internalVariants:list[Building] = []

class Building:
    def __init__(self,id:str,tiles:list[utils.Pos],fromInternalVariantList:InternalVariantList) -> None:
        self.id = id
        self.tiles = tiles
        self.fromInternalVariantList = fromInternalVariantList

def _loadBuildings() -> tuple[dict[str,InternalVariantList],dict[str,Building]]:

    with open(globalInfos.GI_BUILDINGS_PATH,encoding="utf-8") as f:
        buildingsRaw = json.load(f)

    allInternalVariantLists = {}
    allBuildings = {}

    for internalVariantListRaw in buildingsRaw["Buildings"]:
        if internalVariantListRaw.get("Title") is None:
            curInternalVariantListTitle = gameInfos.translations.getTranslation(f"building-variant.{internalVariantListRaw['Id']}.title")
        else:
            curInternalVariantListTitle = internalVariantListRaw["Title"]
        curInternalVariantList = InternalVariantList(
            internalVariantListRaw["Id"],
            curInternalVariantListTitle
        )
        allInternalVariantLists[curInternalVariantList.id] = curInternalVariantList
        for buildingRaw in internalVariantListRaw["InternalVariants"]:
            curBuilding = Building(
                buildingRaw["Id"],
                [gameInfos.common.loadPos(tile) for tile in buildingRaw["Tiles"]],
                curInternalVariantList
            )
            allBuildings[curBuilding.id] = curBuilding
            curInternalVariantList.internalVariants.append(curBuilding)

    return allInternalVariantLists, allBuildings

allInternalVariantLists, allBuildings = _loadBuildings()

def getCategorizedBuildingCounts(counts:dict[str,int]) -> dict[str,dict[str,int]]:

    internalVariants:dict[str,dict[str,int]] = {}
    for b,c in counts.items():
        curIV = allBuildings[b].fromInternalVariantList.id
        if internalVariants.get(curIV) is None:
            internalVariants[curIV] = {}
        internalVariants[curIV][b] = c

    return internalVariants