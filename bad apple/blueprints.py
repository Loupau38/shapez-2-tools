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

PREFIX = "SHAPEZ2"
SEPARATOR = "-"
SUFFIX = "$"

BUILDING_BP_TYPE = "Building"
ISLAND_BP_TYPE = "Island"

NUM_LAYERS = 3
ISLAND_ROTATION_CENTER = utils.FloatPos(*([(gameInfos.islands.ISLAND_SIZE/2)-.5]*2))

COLOR_PREFIX = "color-"

class BlueprintError(Exception): ...

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
        _omitKeyIfDefault(toReturn,"C",_encodeEntryExtraData(self.extra,self.type.id))
        return toReturn

class BuildingBlueprint:
    def __init__(self,asEntryList:list[BuildingEntry]) -> None:
        self.asEntryList = asEntryList
        self.asTileDict = _getTileDictFromEntryList(asEntryList)

    def getSize(self) -> Size:
        return _genericGetSize(self)

    def getBuildingCount(self) -> int:
        return len(self.asEntryList)

    def getBuildingCounts(self) -> dict[str,int]:
        return _genericGetCounts(self)

    def _encode(self) -> dict:
        return {
            "$type" : BUILDING_BP_TYPE,
            "Entries" : [e._encode() for e in self.asEntryList]
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
        _omitKeyIfDefault(toReturn,"C",_encodeEntryExtraData(self.extra,self.type.id))
        if self.buildingBP is not None:
            toReturn["B"] = self.buildingBP._encode()
        return toReturn

class IslandBlueprint:
    def __init__(self,asEntryList:list[IslandEntry]) -> None:
        self.asEntryList = asEntryList
        self.asTileDict = _getTileDictFromEntryList(asEntryList)

    def getSize(self) -> Size:
        return _genericGetSize(self)

    def getIslandCount(self) -> int:
        return len(self.asEntryList)

    def getIslandCounts(self) -> dict[str,int]:
        return _genericGetCounts(self)

    def getTileCount(self) -> int:
        return len(self.asTileDict)

    def _encode(self) -> dict:
        return {
            "$type" : ISLAND_BP_TYPE,
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
                self.buildingBP = BuildingBlueprint(tempBuildingList)

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
        except Exception as e:
            raise BlueprintError("Failed to compute blueprint cost") from e

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

def _omitKeyIfDefault(dict:dict,key:str,value:int|str) -> None:
    if value not in (0,""):
        dict[key] = value

def _decodeEntryExtraData(raw:str,entryType:str) -> typing.Any:

    def standardDecode(rawDecoded:bytes,emptyIsLengthNegative1:bool) -> str:
        try:
            decodedBytes = utils.decodeStringWithLen(rawDecoded,emptyIsLengthNegative1=emptyIsLengthNegative1)
        except ValueError as e:
            raise BlueprintError(f"Error while decoding string : {e}")
        try:
            return decodedBytes.decode()
        except Exception as e:
            raise BlueprintError(f"Can't decode from bytes ({e.__class__.__name__})")

    def checkIfValidColor(color:str) -> None:
        if not color.startswith(COLOR_PREFIX):
            raise BlueprintError(f"Doesn't start with '{COLOR_PREFIX}' prefix")
        color = color.removeprefix(COLOR_PREFIX)
        if color not in globalInfos.SHAPE_COLORS:
            raise BlueprintError(f"Unknown color : '{color}'")

    def getValidShapeGenerator(string:str) -> dict[str,str]:
        for crateOrNot in ("","crate"):
            if string.startswith(f"shape{crateOrNot}:"):
                string = string.removeprefix(f"shape{crateOrNot}:")
                error, valid = shapeCodeGenerator.isShapeCodeValid(string)
                if not valid:
                    raise BlueprintError(f"Invalid shape code : {error}")
                return {"type":f"shape{crateOrNot}","value":string}
        if string.startswith("fluidcrate:"):
            string = string.removeprefix("fluidcrate:")
            try:
                checkIfValidColor(string)
            except BlueprintError as e:
                raise BlueprintError(f"Invalid color code : {e}")
            return {"type":"fluidcrate","value":string}
        raise BlueprintError("Invalid shape creation string")

    try:
        rawDecoded = base64.b64decode(raw)
    except Exception as e:
        raise BlueprintError(f"Can't decode from base64 ({e.__class__.__name__})")

    if entryType == "LabelDefaultInternalVariant":
        return standardDecode(rawDecoded,False)

    if entryType == "ConstantSignalDefaultInternalVariant":

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

        # shape or fluid
        try:
            signalValueDecoded = standardDecode(signalValue,True)
        except BlueprintError as e:
            raise BlueprintError(f"Error while decoding signal value : {e}")

        if signalType == 6: # shape
            try:
                return {"type":"shape","value":getValidShapeGenerator(signalValueDecoded)}
            except BlueprintError as e:
                raise BlueprintError(f"Error while decoding shape signal value : {e}")

        # fluid
        try:
            checkIfValidColor(signalValueDecoded)
        except BlueprintError as e:
            raise BlueprintError(f"Invalid fluid signal value : {e}")
        return {"type":"fluid","value":{"type":"paint","value":signalValueDecoded}}

    if entryType == "SandboxItemProducerDefaultInternalVariant":
        shapeCode = standardDecode(rawDecoded,True)
        if shapeCode == "":
            return {"type":"empty"}
        try:
            return getValidShapeGenerator(shapeCode)
        except BlueprintError as e:
            raise BlueprintError(f"Error while decoding shape generation string : {e}")

    if entryType == "SandboxFluidProducerDefaultInternalVariant":
        fluidCode = standardDecode(rawDecoded,True)
        if fluidCode == "":
            return {"type":"empty"}
        try:
            checkIfValidColor(fluidCode)
        except BlueprintError as e:
            raise BlueprintError(f"Invalid fluid : {e}")
        return {"type":"paint","value":fluidCode}

    if entryType in ("TrainStationLoaderInternalVariant","TrainStationUnloaderInternalVariant"):

        if rawDecoded == b"": # support for pre-alpha 15.2 blueprints
            return {"r":True,"g":True,"b":True}

        if len(rawDecoded) == 4:
            encodedColor = int.from_bytes(rawDecoded,"little")

        if (len(rawDecoded) != 4) or (encodedColor > 7): # support for pre-alpha 16 blueprints
            try:
                oldColorText = standardDecode(rawDecoded,True)
            except BlueprintError as e:
                raise BlueprintError(f"Error while attempting to decode old format train station : {e}")
            if oldColorText == "":
                return {"r":True,"g":True,"b":True}
            return {
                "r" : "r" in oldColorText,
                "g" : "g" in oldColorText,
                "b" : "b" in oldColorText
            }

        return {
            "r" : (encodedColor & 4) != 0,
            "g" : (encodedColor & 2) != 0,
            "b" : (encodedColor & 1) != 0
        }

    if entryType == "ButtonDefaultInternalVariant":

        if len(rawDecoded) < 1:
            raise BlueprintError("String must be at least 1 byte long")

        return rawDecoded[0] != 0

    if entryType in ("Layout_SpaceBeltNode","Layout_RailNode"):
        if len(rawDecoded) < 1:
            raise BlueprintError("String must be at least 1 byte long")
        layoutType = rawDecoded[0]
        if layoutType > 3:
            raise BlueprintError(f"Unknown space belt/rail layout type : {layoutType}")
        return {"type":layoutType,"layout":rawDecoded[1:]}

    return None

def _encodeEntryExtraData(extra:typing.Any,entryType:str) -> str:

    if extra is None:
        return ""

    def b64encode(string:bytes) -> str:
        return base64.b64encode(string).decode()

    def standardEncode(string:str,emptyIsLengthNegative1:bool) -> str:
        return b64encode(utils.encodeStringWithLen(string.encode(),emptyIsLengthNegative1=emptyIsLengthNegative1))

    if entryType == "LabelDefaultInternalVariant":
        return standardEncode(extra,False)

    if entryType == "ConstantSignalDefaultInternalVariant":

        if extra["type"] in ("empty","null","conflict"):
            return b64encode(bytes([{"empty":0,"null":1,"conflict":2}[extra["type"]]]))

        if extra["type"] == "bool":
            return b64encode(bytes([5 if extra["value"] else 4]))

        if extra["type"] == "int":
            return b64encode(bytes([3])+extra["value"].to_bytes(4,"little",signed=True))

        if extra["type"] == "shape":
            return b64encode(bytes([6])+utils.encodeStringWithLen(f"{extra['value']['type']}:{extra['value']['value']}".encode()))

        if extra["type"] == "fluid":
            return b64encode(bytes([7])+utils.encodeStringWithLen(extra["value"].encode()))

    if entryType == "SandboxItemProducerDefaultInternalVariant":
        if extra["type"] == "empty":
            shapeCode = ""
        else:
            shapeCode = f"{extra['type']}:{extra['value']}"
        return standardEncode(shapeCode,True)

    if entryType == "SandboxFluidProducerDefaultInternalVariant":
        if extra["type"] == "empty":
            fluidCode = ""
        else:
            fluidCode = extra["value"]
        return standardEncode(fluidCode,True)

    if entryType in ("TrainStationLoaderInternalVariant","TrainStationUnloaderInternalVariant"):
        encodedColor = 0
        if extra["r"]:
            encodedColor += 4
        if extra["g"]:
            encodedColor += 2
        if extra["b"]:
            encodedColor += 1
        return b64encode(encodedColor.to_bytes(4,"little"))

    if entryType == "ButtonDefaultInternalVariant":
        return b64encode(bytes([int(extra)]))

    if entryType in ("Layout_SpaceBeltNode","Layout_RailNode"):
        return b64encode(bytes([extra["type"]])+extra["layout"])

    raise ValueError(f"Attempt to encode extra data of entry that shouldn't have any ({entryType})")

def _getDefaultEntryExtraData(entryType:str) -> typing.Any:

    if entryType == "LabelDefaultInternalVariant":
        return "Click to change text"

    if entryType == "ConstantSignalDefaultInternalVariant":
        return {"type":"null"}

    if entryType == "SandboxItemProducerDefaultInternalVariant":
        return {"type":"shape","value":"CuCuCuCu"}

    if entryType == "SandboxFluidProducerDefaultInternalVariant":
        return {"type":"paint","value":f"{COLOR_PREFIX}r"}

    if entryType in ("TrainStationLoaderInternalVariant","TrainStationUnloaderInternalVariant"):
        return {"r":True,"g":True,"b":True}

    if entryType == "ButtonDefaultInternalVariant":
        return False

    if entryType in ("Layout_SpaceBeltNode","Layout_RailNode"):
        return {
            "type" : 1,
            "layout" : bytes([0,0]) + (bytes([7,0,0,0]) if entryType == "Layout_RailNode" else bytes())
        }

    return None

def _getTileDictFromEntryList(entryList:list[BuildingEntry|IslandEntry]) -> dict[Pos,TileEntry]:
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
            encodedBP = encodedBP.encode()
        except Exception as e:
            raise BlueprintError(f"Can't encode in bytes ({e.__class__.__name__})")
        try:
            encodedBP = base64.b64decode(encodedBP)
        except Exception as e:
            raise BlueprintError(f"Can't decode from base64 ({e.__class__.__name__})")
        try:
            encodedBP = gzip.decompress(encodedBP)
        except Exception as e:
            raise BlueprintError(f"Can't gzip decompress ({e.__class__.__name__})")
        try:
            decodedBP = json.loads(encodedBP)
        except Exception as e:
            raise BlueprintError(f"Can't parse json ({e.__class__.__name__})")

        try:
            _getKeyValue(decodedBP,"V",int)
            _getKeyValue(decodedBP,"BP",dict)
        except BlueprintError as e:
            raise BlueprintError(f"Error in {_ERR_MSG_PATH_START}blueprint json object{e}")

    except BlueprintError as e:
        raise BlueprintError(f"Error while decoding blueprint string : {e}")

    return decodedBP, majorVersion

def _encodeBlueprintLastPart(blueprint:dict,majorVersion:int) -> str:
    blueprint = base64.b64encode(gzip.compress(json.dumps(blueprint,indent=2).encode())).decode()
    blueprint = PREFIX + SEPARATOR + str(majorVersion) + SEPARATOR + blueprint + SUFFIX
    return blueprint

def _getValidBlueprint(blueprint:dict,mustBeBuildingBP:bool=False) -> dict:

    validBP = {}

    bpType = _getKeyValue(blueprint,"$type",str,BUILDING_BP_TYPE) # default to building instead of nothing : support for pre-alpha 8 blueprints

    if bpType not in (BUILDING_BP_TYPE,ISLAND_BP_TYPE):
        raise BlueprintError(f"{_ERR_MSG_PATH_SEP}$type{_ERR_MSG_PATH_END}Unknown blueprint type : '{bpType}'")

    if mustBeBuildingBP and (bpType != BUILDING_BP_TYPE):
        raise BlueprintError(f"{_ERR_MSG_PATH_SEP}$type{_ERR_MSG_PATH_END}Must be a building blueprint")

    validBP["$type"] = bpType

    allowedEntryTypes = (
        gameInfos.buildings.allBuildings.keys()
        if bpType == BUILDING_BP_TYPE else
        gameInfos.islands.allIslands.keys()
    )

    bpEntries = _getKeyValue(blueprint,"Entries",list)

    if bpEntries == []:
        raise BlueprintError(f"{_ERR_MSG_PATH_SEP}Entries{_ERR_MSG_PATH_END}Empty list")

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

            c = _getKeyValue(entry,"C",str,"")
            try:
                c = _decodeEntryExtraData(c,t)
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

    return validBP

def _decodeBuildingBP(buildings:list[dict[str,typing.Any]],moveBPCenter:bool=True) -> BuildingBlueprint:

    entryList:list[BuildingEntry] = []
    occupiedTiles:set[Pos] = set()

    for building in buildings:

        curTiles = [t.rotateCW(building["R"]) for t in gameInfos.buildings.allBuildings[building["T"]].tiles]
        curTiles = [Pos(building["X"]+t.x,building["Y"]+t.y,building["L"]+t.z) for t in curTiles]

        for curTile in curTiles:

            if curTile in occupiedTiles:
                raise BlueprintError(f"Error while placing tile of '{building['T']}' at {curTile} (raw) : another tile is already placed there")

            occupiedTiles.add(curTile)

    minX, minY, minZ = [min(e.__dict__[k] for e in occupiedTiles) for k in ("x","y","z")]
    maxZ = max(e.z for e in occupiedTiles)

    if maxZ-minZ+1 > NUM_LAYERS:
        raise BlueprintError(f"Cannot have more than {NUM_LAYERS} layers")

    for b in buildings:
        if moveBPCenter:
            b["X"] -= minX
            b["Y"] -= minY
            b["L"] -= minZ
        entryList.append(BuildingEntry(
            Pos(b["X"],b["Y"],b["L"]),
            Rotation(b["R"]),
            gameInfos.buildings.allBuildings[b["T"]],
            b["C"]
        ))

    return BuildingBlueprint(entryList)

def _decodeIslandBP(islands:list[dict[str,typing.Any]]) -> IslandBlueprint:

    entryList:list[IslandEntry] = []
    occupiedTiles:set[Pos] = set()

    for island in islands:

        curTiles = [t.pos.rotateCW(island["R"]) for t in gameInfos.islands.allIslands[island["T"]].tiles]
        curTiles = [Pos(island["X"]+t.x,island["Y"]+t.y) for t in curTiles]

        for curTile in curTiles:

            if curTile in occupiedTiles:
                raise BlueprintError(f"Error while placing tile of '{island['T']}' at {curTile} (raw) : another tile is already placed there")

            occupiedTiles.add(curTile)

    minX, minY = [min(e.__dict__[k] for e in occupiedTiles) for k in ("x","y")]

    for i in islands:
        i["X"] -= minX
        i["Y"] -= minY

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
            curBuildingBP = _decodeBuildingBP(island["B"]["Entries"],False)
        except BlueprintError as e:
            raise BlueprintError(
                f"Error while creating building blueprint representation of '{islandEntryInfos['t'].id}' at {islandEntryInfos['pos']} (rectified) : {e}")

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
                    f"Error in '{islandEntryInfos['t'].id}' at {islandEntryInfos['pos']} (rectified) : tile of building '{curBuilding.type.id}' at {pos} (raw) is not inside its platform build area")

        entryList.append(IslandEntry(
            islandEntryInfos["pos"],
            Rotation(islandEntryInfos["r"]),
            islandEntryInfos["t"],
            curBuildingBP,
            islandEntryInfos["c"]
        ))

    return IslandBlueprint(entryList)





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
    else:
        func = _decodeIslandBP
        text = "platform"

    try:
        decodedDecodedBP = func(validBP["Entries"])
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