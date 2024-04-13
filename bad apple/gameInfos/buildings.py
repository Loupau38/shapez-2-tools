import globalInfos
import utils
import gameInfos.common
import json

class VariantList:
    def __init__(self,id:str,title:str) -> None:
        self.id = id
        self.title = title
        self.variants:list[InternalVariantList] = []

class InternalVariantList:
    def __init__(self,id:str,title:str,fromVariantList:VariantList) -> None:
        self.id = id
        self.title = title
        self.fromVariantList = fromVariantList
        self.internalVariants:list[Building] = []

class Building:
    def __init__(self,id:str,tiles:list[utils.Pos],fromInternalVariantList:InternalVariantList) -> None:
        self.id = id
        self.tiles = tiles
        self.fromInternalVariantList = fromInternalVariantList

def _loadBuildings() -> tuple[dict[str,VariantList],dict[str,InternalVariantList],dict[str,Building]]:

    with open(globalInfos.GI_BUILDINGS_PATH,encoding="utf-8") as f:
        buildingsRaw = json.load(f)

    allVariantLists = {}
    allInternalVariantLists = {}
    allBuildings = {}

    for variantListRaw in buildingsRaw["Buildings"]:
        curVariantList = VariantList(variantListRaw["Id"],variantListRaw["Title"])
        allVariantLists[curVariantList.id] = curVariantList
        for internalVariantListRaw in variantListRaw["Variants"]:
            curInternalVariantList = InternalVariantList(internalVariantListRaw["Id"],internalVariantListRaw["Title"],curVariantList)
            allInternalVariantLists[curInternalVariantList.id] = curInternalVariantList
            curVariantList.variants.append(curInternalVariantList)
            for buildingRaw in internalVariantListRaw["InternalVariants"]:
                curBuilding = Building(
                    buildingRaw["Id"],
                    [gameInfos.common.loadPos(tile) for tile in buildingRaw["Tiles"]],
                    curInternalVariantList
                )
                allBuildings[curBuilding.id] = curBuilding
                curInternalVariantList.internalVariants.append(curBuilding)

    return allVariantLists, allInternalVariantLists, allBuildings

allVariantLists, allInternalVariantLists, allBuildings = _loadBuildings()

def getCategorizedBuildingCounts(counts:dict[str,int]) -> dict[str,dict[str,dict[str,int]]]:

    internalVariants:dict[str,dict[str,int]] = {}
    for b,c in counts.items():
        curIV = allBuildings[b].fromInternalVariantList.id
        if internalVariants.get(curIV) is None:
            internalVariants[curIV] = {}
        internalVariants[curIV][b] = c

    variants = {}
    for iv,c in internalVariants.items():
        curV = allInternalVariantLists[iv].fromVariantList.id
        if variants.get(curV) is None:
            variants[curV] = {}
        variants[curV][iv] = c

    return variants