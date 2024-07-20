import utils
from utils import Rotation, Pos, Size
import gameInfos
import globalInfos
import shapeCodeGenerator
import gzip
import base64
import json
import typing
import math
import binascii

PREFIX = "SHAPEZ2"
SEPARATOR = "-"
SUFFIX = "$"

BUILDING_BP_TYPE = "Building"
ISLAND_BP_TYPE = "Island"

NUM_LAYERS = 3
ISLAND_ROTATION_CENTER = utils.FloatPos(*([(gameInfos.islands.ISLAND_SIZE/2)-.5]*2))

NUM_BP_ICONS = 4

# use variables instead of string literals and make potential ID changes not go unnoticed at the same time
BUILDING_IDS = {
    "label" : gameInfos.buildings.allBuildings["LabelDefaultInternalVariant"].id,
    "constantSignal" : gameInfos.buildings.allBuildings["ConstantSignalDefaultInternalVariant"].id,
    "itemProducer" : gameInfos.buildings.allBuildings["SandboxItemProducerDefaultInternalVariant"].id,
    "fluidProducer" : gameInfos.buildings.allBuildings["SandboxFluidProducerDefaultInternalVariant"].id,
    "button" : gameInfos.buildings.allBuildings["ButtonDefaultInternalVariant"].id,
    "compareGate" : gameInfos.buildings.allBuildings["LogicGateCompareInternalVariant"].id,
    "wireGlobalSender" : gameInfos.buildings.allBuildings["WireGlobalTransmitterSenderInternalVariant"].id,
    "wireGlobalReceiver" : gameInfos.buildings.allBuildings["WireGlobalTransmitterReceiverInternalVariant"].id
}
ISLAND_IDS = {
    "spaceBelt" : gameInfos.islands.allIslands["Layout_SpaceBeltNode"].id,
    "spacePipe" : gameInfos.islands.allIslands["Layout_SpacePipeNode"].id,
    "rail" : gameInfos.islands.allIslands["Layout_RailNode"].id,
    "trainShapesLoader" : gameInfos.islands.allIslands["Layout_TrainLoader_Shapes"].id,
    "trainShapesLoaderFlipped" : gameInfos.islands.allIslands["Layout_TrainLoader_Shapes_Flipped"].id,
    "trainShapesUnloader" : gameInfos.islands.allIslands["Layout_TrainUnloader_Shapes"].id,
    "trainShapesUnloaderFlipped" : gameInfos.islands.allIslands["Layout_TrainUnloader_Shapes_Flipped"].id,
    "trainFluidsLoader" : gameInfos.islands.allIslands["Layout_TrainLoader_Fluids"].id,
    "trainFluidsLoaderFlipped" : gameInfos.islands.allIslands["Layout_TrainLoader_Fluids_Flipped"].id,
    "trainFluidsUnloader" : gameInfos.islands.allIslands["Layout_TrainUnloader_Fluids"].id,
    "trainFluidsUnloaderFlipped" : gameInfos.islands.allIslands["Layout_TrainUnloader_Fluids_Flipped"].id,
    "trainStop" : gameInfos.islands.allIslands["Layout_TrainStation"].id,
    "trainProducerRed" : gameInfos.islands.allIslands["Layout_TrainProducer_Red"].id,
    "trainProducerGreen" : gameInfos.islands.allIslands["Layout_TrainProducer_Green"].id,
    "trainProducerBlue" : gameInfos.islands.allIslands["Layout_TrainProducer_Blue"].id,
    "trainProducerWhite" : gameInfos.islands.allIslands["Layout_TrainProducer_White"].id
}

ISLANDS_WITH_RAIL_EXTRA_DATA = [ISLAND_IDS[id] for id in (
    "trainShapesLoader",
    "trainShapesLoaderFlipped",
    "trainShapesUnloader",
    "trainShapesUnloaderFlipped",
    "trainFluidsLoader",
    "trainFluidsLoaderFlipped",
    "trainFluidsUnloader",
    "trainFluidsUnloaderFlipped",
    "trainStop"
)]

class BlueprintError(Exception): ...

class BlueprintIcon:

    def __init__(self,raw:str|None) -> None:
        self.type:typing.Literal["empty","icon","shape"]
        if raw is None:
            self.type = "empty"
        elif raw.startswith("icon:"):
            self.type = "icon"
            self.value = raw.removeprefix("icon:")
        else:
            self.type = "shape"
            self.value = raw.removeprefix("shape:")

    def _encode(self) -> str|None:
        if self.type == "empty":
            return None
        if self.type == "icon":
            return f"icon:{self.value}"
        return f"shape:{self.value}"

class TileEntry:
    def __init__(self,referTo) -> None:
        self.referTo:BuildingEntry|IslandEntry = referTo

class BuildingEntry:

    def __init__(self,pos:Pos,rotation:Rotation,type:gameInfos.buildings.Building,extra:typing.Any) -> None:
        self.pos = pos
        self.rotation = rotation
        self.type = type
        self.extra:typing.Any
        if extra is None:
            self.extra = _getDefaultEntryExtraData(type.id)
        else:
            self.extra = extra

    def _encode(self) -> dict:
        toReturn = {
            "T" : self.type.id
        }
        _omitKeyIfDefault(toReturn,"X",self.pos.x)
        _omitKeyIfDefault(toReturn,"Y",self.pos.y)
        _omitKeyIfDefault(toReturn,"L",self.pos.z)
        _omitKeyIfDefault(toReturn,"R",self.rotation.value)
        _omitKeyIfDefault(toReturn,"C",_encodeEntryExtraData(self.extra,self.type.id,False))
        return toReturn

class BuildingBlueprint:

    def __init__(self,asEntryList:list[BuildingEntry],icons:list[BlueprintIcon],binaryVersion:int) -> None:
        self.asEntryList = asEntryList
        self.asTileDict = _getTileDictFromEntryList(asEntryList)
        self.icons = icons
        self.binaryVersion = binaryVersion

    def getSize(self) -> Size:
        return _genericGetSize(self)

    def getBuildingCount(self) -> int:
        return len(self.asEntryList)

    def getBuildingCounts(self) -> dict[str,int]:
        return _genericGetCounts(self)

    def getTileCount(self) -> int:
        return len(self.asTileDict)

    def getValidIcons(self) -> list[BlueprintIcon]:
        return _genericGetValidIcons(self)

    def _encode(self) -> dict:
        return {
            "$type" : BUILDING_BP_TYPE,
            "Icon" : {
                "Data" : [i._encode() for i in self.icons]
            },
            "Entries" : [e._encode() for e in self.asEntryList],
            "BinaryVersion" : self.binaryVersion
        }

class IslandEntry:

    def __init__(self,pos:Pos,rotation:Rotation,type:gameInfos.islands.Island,buildingBP:BuildingBlueprint|None,extra:typing.Any) -> None:
        self.pos = pos
        self.rotation = rotation
        self.type = type
        self.buildingBP = buildingBP
        if extra is None:
            self.extra = _getDefaultEntryExtraData(type.id)
        else:
            self.extra = extra

    def _encode(self) -> dict:
        toReturn = {
            "T" : self.type.id
        }
        _omitKeyIfDefault(toReturn,"X",self.pos.x)
        _omitKeyIfDefault(toReturn,"Y",self.pos.y)
        _omitKeyIfDefault(toReturn,"R",self.rotation.value)
        _omitKeyIfDefault(toReturn,"C",_encodeEntryExtraData(self.extra,self.type.id,True),("AA==",))
        if self.buildingBP is not None:
            toReturn["B"] = self.buildingBP._encode()
        return toReturn

class IslandBlueprint:

    def __init__(self,asEntryList:list[IslandEntry],icons:list[BlueprintIcon]) -> None:
        self.asEntryList = asEntryList
        self.asTileDict = _getTileDictFromEntryList(asEntryList)
        self.icons = icons

    def getSize(self) -> Size:
        return _genericGetSize(self)

    def getIslandCount(self) -> int:
        return len(self.asEntryList)

    def getIslandCounts(self) -> dict[str,int]:
        return _genericGetCounts(self)

    def getTileCount(self) -> int:
        return len(self.asTileDict)

    def getValidIcons(self) -> list[BlueprintIcon]:
        return _genericGetValidIcons(self)

    def _encode(self) -> dict:
        return {
            "$type" : ISLAND_BP_TYPE,
            "Icons" : {
                "Data" : [i._encode() for i in self.icons]
            },
            "Entries" : [e._encode() for e in self.asEntryList]
        }

class Blueprint:

    def __init__(self,majorVersion:int,version:int,type_:str,blueprint:BuildingBlueprint|IslandBlueprint) -> None:
        self.majorVersion = majorVersion
        self.version = version
        self.type = type_
        self.islandBP:IslandBlueprint|None
        self.buildingBP:BuildingBlueprint|None
        if type(blueprint) == BuildingBlueprint:
            self.buildingBP = blueprint
            self.islandBP = None
        else:
            self.islandBP = blueprint
            tempBuildingList = []
            for island in blueprint.asEntryList:
                if island.buildingBP is None:
                    continue
                for building in island.buildingBP.asEntryList:
                    tempBuildingList.append(BuildingEntry(
                        Pos(
                            (island.pos.x*gameInfos.islands.ISLAND_SIZE) + building.pos.x,
                            (island.pos.y*gameInfos.islands.ISLAND_SIZE) + building.pos.y,
                            building.pos.z
                        ),
                        building.rotation,
                        building.type,
                        building.extra
                    ))
            if tempBuildingList == []:
                self.buildingBP = None
            else:
                self.buildingBP = BuildingBlueprint(tempBuildingList,blueprint.icons,gameInfos.versions.LATEST_GAME_VERSION)

    def getCost(self) -> int:
        # bp cost formula : last updated : alpha 15.2
        # note to self : dnSpy > BuildingBlueprint > ComputeCost() / ComputeTotalCost()
        if self.buildingBP is None:
            return 0
        buildingCount = self.buildingBP.getBuildingCount()
        if buildingCount <= 1:
            return 0
        try:
            return math.ceil((buildingCount-1) ** 1.3)
        except OverflowError:
            raise BlueprintError("Failed to compute blueprint cost")

    def getIslandUnitCost(self) -> int:
        if self.islandBP is None:
            return 0
        return sum(island.type.islandUnitCost for island in self.islandBP.asEntryList)

    def _encode(self) -> tuple[dict,int]:
        return {
            "V" : self.version,
            "BP" : (self.buildingBP if self.islandBP is None else self.islandBP)._encode()
        }, self.majorVersion

def _genericGetSize(bp:BuildingBlueprint|IslandBlueprint) -> Size:
    (minX,minY,minZ), (maxX,maxY,maxZ) = [[func(e.__dict__[k] for e in bp.asTileDict.keys()) for k in ("x","y","z")] for func in (min,max)]
    return Size(
        maxX - minX + 1,
        maxY - minY + 1,
        maxZ - minZ + 1
    )

def _genericGetCounts(bp:BuildingBlueprint|IslandBlueprint) -> dict[str,int]:
    output = {}
    for entry in bp.asEntryList:
        entryType = entry.type.id
        if output.get(entryType) is None:
            output[entryType] = 1
        else:
            output[entryType] += 1
    return output

def _genericGetValidIcons(bp:BuildingBlueprint|IslandBlueprint) -> list[BlueprintIcon]:
    validIcons = []
    for icon in bp.icons[:NUM_BP_ICONS]:
        if icon.type == "empty":
            validIcons.append(icon)
            continue
        if icon.type == "icon":
            if icon.value in VALID_BP_ICONS:
                validIcons.append(icon)
            else:
                validIcons.append(BlueprintIcon(None))
            continue
        if shapeCodeGenerator.isShapeCodeValid(icon.value,None,True)[1]:
            validIcons.append(icon)
        else:
            validIcons.append(BlueprintIcon(None))
    validIcons += [BlueprintIcon(None)] * (NUM_BP_ICONS-len(validIcons))
    return validIcons

def _omitKeyIfDefault(dict:dict,key:str,value:int|str,defaults:tuple[typing.Any,...]=(0,"")) -> None:
    if value not in defaults:
        dict[key] = value

def _decodeEntryExtraData(raw:str,entryType:str,isIsland:bool) -> typing.Any:

    def standardDecode(rawDecoded:bytes,emptyIsLengthNegative1:bool) -> str:
        try:
            decodedBytes = utils.decodeStringWithLen(rawDecoded,emptyIsLengthNegative1=emptyIsLengthNegative1)
        except ValueError as e:
            raise BlueprintError(f"Error while decoding string : {e}")
        try:
            return decodedBytes.decode()
        except UnicodeDecodeError:
            raise BlueprintError(f"Can't decode from bytes")

    def getValidShapeGenerator(rawString:bytes) -> dict[str,str]:

        if len(rawString) < 1:
            raise BlueprintError("String must be at least 1 byte long")

        if rawString[0] == 0:
            return {"type":"empty"}

        if len(rawString) < 2:
            raise BlueprintError("String must be at least 2 bytes long")

        if (rawString[0] != 1) or (rawString[1] != 1):
            raise BlueprintError("First two bytes of shape generation string aren't '\\x01'")

        shapeCode = standardDecode(rawString[2:],True)
        error, valid = shapeCodeGenerator.isShapeCodeValid(shapeCode,None,True)

        if not valid:
            raise BlueprintError(f"Invalid shape code : {error}")

        return {"type":"shape","value":shapeCode}

    def getValidFluidGenerator(rawString:bytes) -> dict[str,str]:

        if len(rawString) < 1:
            raise BlueprintError("String must be at least 1 byte long")

        if rawString[0] == 0:
            return {"type":"empty"}

        if len(rawString) < 2:
            raise BlueprintError("String must be at least 2 bytes long")

        if rawString[0] != 1:
            raise BlueprintError("First byte of fluid generation string isn't '\\x01'")

        try:
            color = rawString[1:2].decode()
        except UnicodeDecodeError:
            raise BlueprintError("Invalid color")

        if color not in globalInfos.SHAPE_COLORS:
            raise BlueprintError(f"Unknown color : '{color}'")

        return {"type":"paint","value":color}

    try:
        rawDecoded = base64.b64decode(raw,validate=True)
    except binascii.Error:
        raise BlueprintError(f"Can't decode from base64")

    if entryType == BUILDING_IDS["label"]:
        return standardDecode(rawDecoded,False)

    if entryType == BUILDING_IDS["constantSignal"]:

        if len(rawDecoded) < 1:
            raise BlueprintError("String must be at least 1 byte long")
        signalType = rawDecoded[0]

        if signalType > 7:
            raise BlueprintError(f"Unknown signal type : {signalType}")

        if signalType in (0,1,2): # empty, null, conflict
            return {
                "type" : {
                    0 : "empty",
                    1 : "null",
                    2 : "conflict"
                }[signalType]
            }

        if signalType in (4,5): # bool
            return {"type":"bool","value":signalType==5}

        signalValue = rawDecoded[1:]

        if signalType == 3: # integer
            if len(signalValue) != 4:
                raise BlueprintError("Signal value must be 4 bytes long for integer signal type")
            return {"type":"int","value":int.from_bytes(signalValue,"little",signed=True)}

        if signalType == 6: # shape
            try:
                return {"type":"shape","value":getValidShapeGenerator(signalValue)}
            except BlueprintError as e:
                raise BlueprintError(f"Error while decoding shape signal value : {e}")

        # fluid
        try:
            return {"type":"fluid","value":getValidFluidGenerator(signalValue)}
        except BlueprintError as e:
            raise BlueprintError(f"Error while decoding fluid signal value : {e}")

    if entryType == BUILDING_IDS["itemProducer"]:
        try:
            return getValidShapeGenerator(rawDecoded)
        except BlueprintError as e:
            raise BlueprintError(f"Error while decoding shape generation string : {e}")

    if entryType == BUILDING_IDS["fluidProducer"]:
        try:
            return getValidFluidGenerator(rawDecoded)
        except BlueprintError as e:
            raise BlueprintError(f"Error while decoding fluid generation string : {e}")

    # same color encoding format is used in rails, keeping code for that in case it can be useful in the future

    # if entryType in ("TrainStationLoaderInternalVariant","TrainStationUnloaderInternalVariant"):

    #     defaultReturn = {"r":True,"g":True,"b":True,"w":True}

    #     if rawDecoded == b"": # support for pre-alpha 15.2 blueprints
    #         return defaultReturn

    #     if len(rawDecoded) == 4:
    #         encodedColor = int.from_bytes(rawDecoded,"little")

    #     if (len(rawDecoded) != 4) or (encodedColor > 15): # support for pre-alpha 16 blueprints
    #         try:
    #             oldColorText = standardDecode(rawDecoded,True)
    #         except BlueprintError as e:
    #             raise BlueprintError(f"Error while attempting to decode old format train station : {e}")
    #         if oldColorText == "":
    #             return defaultReturn
    #         return {
    #             "r" : "r" in oldColorText,
    #             "g" : "g" in oldColorText,
    #             "b" : "b" in oldColorText,
    #             "w" : "w" in oldColorText
    #         }

    #     return {
    #         "w" : (encodedColor & 8) != 0,
    #         "r" : (encodedColor & 4) != 0,
    #         "g" : (encodedColor & 2) != 0,
    #         "b" : (encodedColor & 1) != 0
    #     }

    if entryType == BUILDING_IDS["button"]:

        if len(rawDecoded) < 1:
            raise BlueprintError("String must be at least 1 byte long")

        return rawDecoded[0] != 0

    if entryType == BUILDING_IDS["compareGate"]:

        if len(rawDecoded) < 1:
            raise BlueprintError("String must be at least 1 byte long")

        compareMode = rawDecoded[0]

        if (compareMode < 1) or (compareMode > 6):
            raise BlueprintError(f"Unknown compare mode : {compareMode}")

        return [
            "Equal",
            "GreaterEqual",
            "Greater",
            "Less",
            "LessEqual",
            "NotEqual"
        ][compareMode-1]

    if entryType in (BUILDING_IDS["wireGlobalSender"],BUILDING_IDS["wireGlobalReceiver"]):
        isReceiver = entryType == BUILDING_IDS["wireGlobalReceiver"]
        stringLen = 5 if isReceiver else 4
        if len(rawDecoded) < stringLen:
            raise BlueprintError(f"String must be at least {stringLen} bytes long")
        channel = int.from_bytes(rawDecoded[:4],"little",signed=True)
        if channel < 0:
            raise BlueprintError("Wire transmitter channel can't be negative")
        if isReceiver:
            return rawDecoded[4] == 1, channel
        return channel

    if (
        (entryType in (ISLAND_IDS["spaceBelt"],ISLAND_IDS["spacePipe"],ISLAND_IDS["rail"]))
        or (entryType in ISLANDS_WITH_RAIL_EXTRA_DATA)
    ):

        if len(rawDecoded) < 2:
            raise BlueprintError("String must be at least 2 bytes long")

        layoutHeader = rawDecoded[0]
        if (entryType in (ISLAND_IDS["spaceBelt"],ISLAND_IDS["spacePipe"])) and (layoutHeader != 20):
            raise BlueprintError("First byte of space belt/pipe layout isn't '\\x14'")
        if ((entryType == ISLAND_IDS["rail"]) or (entryType in ISLANDS_WITH_RAIL_EXTRA_DATA)) and (layoutHeader != 10):
            raise BlueprintError("First byte of rail layout isn't '\\x0a'")

        layoutType = rawDecoded[1]
        if layoutType > 3:
            raise BlueprintError(f"Unknown space belt/pipe/rail layout type : {layoutType}")

        return {"type":layoutType,"layout":rawDecoded[2:]}

    if isIsland and (rawDecoded != bytes([0])):
        raise BlueprintError("String must be '\\x00'")

    return None

def _encodeEntryExtraData(extra:typing.Any,entryType:str,isIsland:bool) -> str:

    def b64encode(string:bytes) -> str:
        return base64.b64encode(string).decode()

    if extra is None:
        if isIsland:
            return b64encode(bytes([0]))
        return ""

    def standardEncode(string:str,emptyIsLengthNegative1:bool) -> str:
        return b64encode(utils.encodeStringWithLen(string.encode(),emptyIsLengthNegative1=emptyIsLengthNegative1))

    def encodeShapeGen(shapeGen:dict[str,str]) -> bytes:
        if shapeGen["type"] == "empty":
            return bytes([0])
        return bytes([1,1]) + utils.encodeStringWithLen(shapeGen["value"].encode())

    def encodeFluidGen(fluidGen:dict[str,str]) -> bytes:
        if fluidGen["type"] == "empty":
            return bytes([0])
        return bytes([1]) + fluidGen["value"].encode()

    if entryType == BUILDING_IDS["label"]:
        return standardEncode(extra,False)

    if entryType == BUILDING_IDS["constantSignal"]:

        if extra["type"] in ("empty","null","conflict"):
            return b64encode(bytes([{"empty":0,"null":1,"conflict":2}[extra["type"]]]))

        if extra["type"] == "bool":
            return b64encode(bytes([5 if extra["value"] else 4]))

        if extra["type"] == "int":
            return b64encode(bytes([3])+extra["value"].to_bytes(4,"little",signed=True))

        if extra["type"] == "shape":
            return b64encode(bytes([6])+encodeShapeGen(extra["value"]))

        if extra["type"] == "fluid":
            return b64encode(bytes([7])+encodeFluidGen(extra["value"]))

    if entryType == BUILDING_IDS["itemProducer"]:
        return b64encode(encodeShapeGen(extra))

    if entryType == BUILDING_IDS["fluidProducer"]:
        return b64encode(encodeFluidGen(extra))

    # if entryType in ("TrainStationLoaderInternalVariant","TrainStationUnloaderInternalVariant"):
    #     encodedColor = 0
    #     if extra["w"]:
    #         encodedColor += 8
    #     if extra["r"]:
    #         encodedColor += 4
    #     if extra["g"]:
    #         encodedColor += 2
    #     if extra["b"]:
    #         encodedColor += 1
    #     return b64encode(encodedColor.to_bytes(4,"little"))

    if entryType == BUILDING_IDS["button"]:
        return b64encode(bytes([int(extra)]))

    if entryType == BUILDING_IDS["compareGate"]:
        return b64encode(bytes([{
            "Equal" : 1,
            "GreaterEqual" : 2,
            "Greater" : 3,
            "Less" : 4,
            "LessEqual" : 5,
            "NotEqual" : 6
        }[extra]]))

    if entryType in (BUILDING_IDS["wireGlobalSender"],BUILDING_IDS["wireGlobalReceiver"]):
        if entryType == BUILDING_IDS["wireGlobalReceiver"]:
            extraExtra, channel = extra
            extraExtra = bytes([1]) if extraExtra else bytes([2])
        else:
            channel = extra
            extraExtra = b""
        return b64encode(channel.to_bytes(4,"little",signed=True)+extraExtra)

    if (
        (entryType in (ISLAND_IDS["spaceBelt"],ISLAND_IDS["spacePipe"],ISLAND_IDS["rail"]))
        or (entryType in ISLANDS_WITH_RAIL_EXTRA_DATA)
    ):
        return b64encode(
            (b"\x14" if entryType in (ISLAND_IDS["spaceBelt"],ISLAND_IDS["spacePipe"]) else b"\x0a")
            + bytes([extra["type"]])
            + extra["layout"]
        )

    raise ValueError(f"Attempt to encode extra data of entry that shouldn't have any ({entryType})")

def _getDefaultEntryExtraData(entryType:str) -> typing.Any:

    if entryType == BUILDING_IDS["label"]:
        return "Label"

    if entryType == BUILDING_IDS["constantSignal"]:
        return {"type":"null"}

    if entryType == BUILDING_IDS["itemProducer"]:
        return {"type":"shape","value":"CuCuCuCu"}

    if entryType == BUILDING_IDS["fluidProducer"]:
        return {"type":"paint","value":"r"}

    # if entryType in ("TrainStationLoaderInternalVariant","TrainStationUnloaderInternalVariant"):
    #     return {"r":True,"g":True,"b":True,"w":True}

    if entryType == BUILDING_IDS["button"]:
        return False

    if entryType == BUILDING_IDS["compareGate"]:
        return "Equal"

    if entryType == BUILDING_IDS["wireGlobalSender"]:
        return 0

    if entryType == BUILDING_IDS["wireGlobalReceiver"]:
        return (False,0)

    if (
        (entryType in (ISLAND_IDS["spaceBelt"],ISLAND_IDS["spacePipe"],ISLAND_IDS["rail"]))
        or (entryType in ISLANDS_WITH_RAIL_EXTRA_DATA)
    ):
        return {
            "type" : 1,
            "layout" : bytes([0,0]) + (
                bytes([15,0,0,0])
                if (entryType == ISLAND_IDS["rail"]) or (entryType in ISLANDS_WITH_RAIL_EXTRA_DATA) else
                bytes()
            )
        }

    return None

def _getTileDictFromEntryList(entryList:list[BuildingEntry]|list[IslandEntry]) -> dict[Pos,TileEntry]:
    tileDict:dict[Pos,TileEntry] = {}
    for entry in entryList:
        if type(entry) == BuildingEntry:
            curTiles = entry.type.tiles
        else:
            curTiles = [t.pos for t  in entry.type.tiles]
        curTiles = [t.rotateCW(entry.rotation) for t in curTiles]
        curTiles = [Pos(entry.pos.x+t.x,entry.pos.y+t.y,entry.pos.z+t.z) for t in curTiles]
        for curTile in curTiles:
            tileDict[curTile] = TileEntry(entry)
    return tileDict

def _getDefaultRawIcons(bpType:str) -> list[str|None]:
    return [
        "icon:" + ("Buildings" if bpType == BUILDING_BP_TYPE else "Platforms"),
        None,
        None,
        "shape:" + ("Cu"*4 if bpType == BUILDING_BP_TYPE else "Ru"*4)
    ]

def _loadIcons() -> list[str]:
    with open(globalInfos.GI_ICONS_PATH,encoding="utf-8") as f:
        return json.load(f)["Icons"]
VALID_BP_ICONS = _loadIcons()





_ERR_MSG_PATH_SEP = ">"
_ERR_MSG_PATH_START = "'"
_ERR_MSG_PATH_END = "' : "
_defaultObj = object()

def _getKeyValue(dict:dict,key:str,expectedValueType:type,default:typing.Any=_defaultObj) -> typing.Any:

    value = dict.get(key,_defaultObj)

    if value is _defaultObj:
        if default is _defaultObj:
            raise BlueprintError(f"{_ERR_MSG_PATH_END}Missing '{key}' key")
        return default

    valueType = type(value)
    if valueType != expectedValueType:
        raise BlueprintError(
            f"{_ERR_MSG_PATH_SEP}{key}{_ERR_MSG_PATH_END}Incorrect value type, expected '{expectedValueType.__name__}', got '{valueType.__name__}'")

    return value

def _decodeBlueprintFirstPart(rawBlueprint:str) -> tuple[dict,int]:

    try:

        sepCount = rawBlueprint.count(SEPARATOR)
        if sepCount != 2:
            raise BlueprintError(f"Expected 2 separators, got {sepCount}")

        prefix, majorVersion, codeAndSuffix = rawBlueprint.split(SEPARATOR)

        if prefix != PREFIX:
            raise BlueprintError("Incorrect prefix")

        if not utils.isNumber(majorVersion):
            raise BlueprintError("Version not a number")
        majorVersion = int(majorVersion)

        if not codeAndSuffix.endswith(SUFFIX):
            raise BlueprintError("Doesn't end with suffix")

        encodedBP = codeAndSuffix.removesuffix(SUFFIX)

        if encodedBP == "":
            raise BlueprintError("Empty encoded section")

        try:
            encodedBP = base64.b64decode(encodedBP,validate=True)
        except binascii.Error:
            raise BlueprintError(f"Can't decode from base64")
        try:
            encodedBP = gzip.decompress(encodedBP)
        except Exception as e:
            raise BlueprintError(f"Can't gzip decompress ({e.__class__.__name__})")
        try:
            decodedBP = json.loads(encodedBP)
        except Exception as e:
            raise BlueprintError(f"Can't parse json ({e.__class__.__name__})")

        if type(decodedBP) != dict:
            raise BlueprintError("Decoded value isn't a json object")

        try:
            _getKeyValue(decodedBP,"V",int)
            _getKeyValue(decodedBP,"BP",dict)
        except BlueprintError as e:
            raise BlueprintError(f"Error in {_ERR_MSG_PATH_START}blueprint json object{e}")

    except BlueprintError as e:
        raise BlueprintError(f"Error while decoding blueprint string : {e}")

    return decodedBP, majorVersion

def _encodeBlueprintLastPart(blueprint:dict,majorVersion:int) -> str:
    blueprint = base64.b64encode(gzip.compress(json.dumps(blueprint,separators=(",",":")).encode())).decode()
    blueprint = PREFIX + SEPARATOR + str(majorVersion) + SEPARATOR + blueprint + SUFFIX
    return blueprint

def _getValidBlueprint(blueprint:dict,mustBeBuildingBP:bool=False) -> dict:

    validBP = {}

    bpType = _getKeyValue(blueprint,"$type",str)

    if bpType not in (BUILDING_BP_TYPE,ISLAND_BP_TYPE):
        raise BlueprintError(f"{_ERR_MSG_PATH_SEP}$type{_ERR_MSG_PATH_END}Unknown blueprint type : '{bpType}'")

    if mustBeBuildingBP and (bpType != BUILDING_BP_TYPE):
        raise BlueprintError(f"{_ERR_MSG_PATH_SEP}$type{_ERR_MSG_PATH_END}Must be a building blueprint")

    validBP["$type"] = bpType

    bpIcons = _getKeyValue(blueprint,"Icon",dict,{"Data":_getDefaultRawIcons(bpType)})

    try:

        bpIconsData = _getKeyValue(bpIcons,"Data",list,[])

        validIcons = []

        for i,icon in enumerate(bpIconsData):
            try:

                iconType = type(icon)

                if iconType in (dict,list):
                    raise BlueprintError(f"{_ERR_MSG_PATH_END}Incorrect value type")

                if iconType in (bool,int,float):
                    continue

                if icon == "":
                    icon = None

                if icon is None:
                    validIcons.append(icon)
                    continue

                icon:str

                if not icon.startswith(("icon:","shape:")):
                    continue

                if icon.startswith("icon:") and (len(icon.removeprefix("icon:")) in (0,1)):
                    continue

                validIcons.append(icon)

            except BlueprintError as e:
                raise BlueprintError(f"{_ERR_MSG_PATH_SEP}Data{_ERR_MSG_PATH_SEP}{i}{e}")

    except BlueprintError as e:
        raise BlueprintError(f"{_ERR_MSG_PATH_SEP}Icon{e}")

    validBP["Icon"] = {
        "Data" : validIcons
    }

    bpEntries = _getKeyValue(blueprint,"Entries",list)

    if bpEntries == []:
        raise BlueprintError(f"{_ERR_MSG_PATH_SEP}Entries{_ERR_MSG_PATH_END}Empty list")

    allowedEntryTypes = (
        gameInfos.buildings.allBuildings.keys()
        if bpType == BUILDING_BP_TYPE else
        gameInfos.islands.allIslands.keys()
    )

    validBPEntries = []

    for i,entry in enumerate(bpEntries):
        try:

            entryType = type(entry)
            if entryType != dict:
                raise BlueprintError(f"{_ERR_MSG_PATH_END}Incorrect value type, expected 'dict', got '{entryType.__name__}'")

            x, y, l, r = (_getKeyValue(entry,k,int,0) for k in ("X","Y","L","R"))

            if (r < 0) or (r > 3):
                raise BlueprintError(f"{_ERR_MSG_PATH_SEP}R{_ERR_MSG_PATH_END}Rotation must be in range from 0 to 3")

            t = _getKeyValue(entry,"T",str)

            if t not in allowedEntryTypes:
                raise BlueprintError(f"{_ERR_MSG_PATH_SEP}T{_ERR_MSG_PATH_END}Unknown entry type '{t}'")

            validEntry = {
                "X" : x,
                "Y" : y,
                "L" : l,
                "R" : r,
                "T" : t
            }

            c = _getKeyValue(entry,"C",str,"AA==" if bpType == ISLAND_BP_TYPE else "")
            try:
                c = _decodeEntryExtraData(c,t,bpType == ISLAND_BP_TYPE)
            except BlueprintError as e:
                raise BlueprintError(f"{_ERR_MSG_PATH_SEP}C{_ERR_MSG_PATH_END}{e}")
            validEntry["C"] = c

            if bpType == ISLAND_BP_TYPE:
                b = entry.get("B",_defaultObj)
                if b is not _defaultObj:
                    b = _getKeyValue(entry,"B",dict)
                    try:
                        validB = _getValidBlueprint(b,True)
                    except BlueprintError as e:
                        raise BlueprintError(f"{_ERR_MSG_PATH_SEP}B{e}")
                    validEntry["B"] = validB

            validBPEntries.append(validEntry)

        except BlueprintError as e:
            raise BlueprintError(f"{_ERR_MSG_PATH_SEP}Entries{_ERR_MSG_PATH_SEP}{i}{e}")

    validBP["Entries"] = validBPEntries

    if bpType == BUILDING_BP_TYPE:
        validBP["BinaryVersion"] = _getKeyValue(blueprint,"BinaryVersion",int,gameInfos.versions.LATEST_GAME_VERSION)

    return validBP

def _decodeBuildingBP(buildings:list[dict[str,typing.Any]],icons:list[str|None],binaryVersion:int) -> BuildingBlueprint:

    entryList:list[BuildingEntry] = []
    occupiedTiles:set[Pos] = set()

    for building in buildings:

        curTiles = [t.rotateCW(building["R"]) for t in gameInfos.buildings.allBuildings[building["T"]].tiles]
        curTiles = [Pos(building["X"]+t.x,building["Y"]+t.y,building["L"]+t.z) for t in curTiles]

        for curTile in curTiles:

            if curTile in occupiedTiles:
                raise BlueprintError(f"Error while placing tile of '{building['T']}' at {curTile} : another tile is already placed there")

            occupiedTiles.add(curTile)

    minZ = min(e.z for e in occupiedTiles)
    maxZ = max(e.z for e in occupiedTiles)

    if maxZ-minZ+1 > NUM_LAYERS:
        raise BlueprintError(f"Cannot have more than {NUM_LAYERS} layers")

    for b in buildings:
        entryList.append(BuildingEntry(
            Pos(b["X"],b["Y"],b["L"]),
            Rotation(b["R"]),
            gameInfos.buildings.allBuildings[b["T"]],
            b["C"]
        ))

    return BuildingBlueprint(entryList,[BlueprintIcon(i) for i in icons],binaryVersion)

def _decodeIslandBP(islands:list[dict[str,typing.Any]],icons:list[str|None]) -> IslandBlueprint:

    entryList:list[IslandEntry] = []
    occupiedTiles:set[Pos] = set()

    for island in islands:

        curTiles = [t.pos.rotateCW(island["R"]) for t in gameInfos.islands.allIslands[island["T"]].tiles]
        curTiles = [Pos(island["X"]+t.x,island["Y"]+t.y) for t in curTiles]

        for curTile in curTiles:

            if curTile in occupiedTiles:
                raise BlueprintError(f"Error while placing tile of '{island['T']}' at {curTile} : another tile is already placed there")

            occupiedTiles.add(curTile)

    for island in islands:

        islandEntryInfos:dict[str,Pos|int|gameInfos.islands.Island|typing.Any] = {
            "pos" : Pos(island["X"],island["Y"]),
            "r" : island["R"],
            "t" : gameInfos.islands.allIslands[island["T"]],
            "c" : island["C"]
        }

        if island.get("B") is None:
            entryList.append(IslandEntry(
                islandEntryInfos["pos"],
                Rotation(islandEntryInfos["r"]),
                islandEntryInfos["t"],
                None,
                islandEntryInfos["c"]
            ))
            continue

        try:
            curBuildingBP = _decodeBuildingBP(island["B"]["Entries"],island["B"]["Icon"]["Data"],island["B"]["BinaryVersion"])
        except BlueprintError as e:
            raise BlueprintError(
                f"Error while creating building blueprint representation of '{islandEntryInfos['t'].id}' at {islandEntryInfos['pos']} : {e}")

        curIslandBuildArea = [a.rotateCW(islandEntryInfos["r"],ISLAND_ROTATION_CENTER) for a in islandEntryInfos["t"].totalBuildArea]

        for pos,b in curBuildingBP.asTileDict.items():

            curBuilding:BuildingEntry = b.referTo

            inArea = False
            for area in curIslandBuildArea:
                if area.containsPos(pos):
                    inArea = True
                    break
            if not inArea:
                raise BlueprintError(
                    f"Error in '{islandEntryInfos['t'].id}' at {islandEntryInfos['pos']} : tile of building '{curBuilding.type.id}' at {pos} is not inside its platform build area")

        entryList.append(IslandEntry(
            islandEntryInfos["pos"],
            Rotation(islandEntryInfos["r"]),
            islandEntryInfos["t"],
            curBuildingBP,
            islandEntryInfos["c"]
        ))

    return IslandBlueprint(entryList,[BlueprintIcon(i) for i in icons])





def changeBlueprintVersion(blueprint:str,version:int) -> str:
    blueprint, majorVersion = _decodeBlueprintFirstPart(blueprint)
    blueprint["V"] = version
    blueprint = _encodeBlueprintLastPart(blueprint,majorVersion)
    return blueprint

def getBlueprintVersion(blueprint:str) -> int:
    return _decodeBlueprintFirstPart(blueprint)[0]["V"]

def decodeBlueprint(rawBlueprint:str) -> Blueprint:
    decodedBP, majorVersion = _decodeBlueprintFirstPart(rawBlueprint)
    version = decodedBP["V"]

    try:
        validBP = _getValidBlueprint(decodedBP["BP"])
    except BlueprintError as e:
        raise BlueprintError(f"Error in {_ERR_MSG_PATH_START}blueprint json object{_ERR_MSG_PATH_SEP}BP{e}")

    bpType = validBP["$type"]

    if bpType == BUILDING_BP_TYPE:
        func = _decodeBuildingBP
        text = "building"
        kwargs = {"binaryVersion":validBP["BinaryVersion"]}
    else:
        func = _decodeIslandBP
        text = "platform"
        kwargs = {}

    try:
        decodedDecodedBP = func(validBP["Entries"],validBP["Icon"]["Data"],**kwargs)
    except BlueprintError as e:
        raise BlueprintError(f"Error while creating {text} blueprint representation : {e}")
    return Blueprint(majorVersion,version,bpType,decodedDecodedBP)

def encodeBlueprint(blueprint:Blueprint) -> str:
    encodedBP, majorVersion = blueprint._encode()
    return _encodeBlueprintLastPart(encodedBP,majorVersion)

def getPotentialBPCodesInString(string:str) -> list[str]:

    if PREFIX not in string:
        return []

    bps = string.split(PREFIX)[1:]

    bpCodes = []

    for bp in bps:

        if SUFFIX not in bp:
            continue

        bp = bp.split(SUFFIX)[0]

        bpCodes.append(PREFIX+bp+SUFFIX)

    return bpCodes

def getDefaultBlueprintIcons(bpType:str) -> list[BlueprintIcon]:
    return [BlueprintIcon(i) for i in _getDefaultRawIcons(bpType)]