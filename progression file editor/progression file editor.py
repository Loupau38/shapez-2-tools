DEFAULT_VALUES_PATH = "./defaultValues.json"

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
del os
import json
import pygame
import typing
import shapeViewer
import sys

# Put the file to edit's path here if you can't use drag and drop
FILE_PATH_OVERRIDE = None
# Disable this if there is issues with the window
SET_DPI_AWARE = True
FPS = 60
DEBUG = False

SAVE_KEY = pygame.K_s
SAVE_KEY_STR = "s"
SAVE_KEY_MOD = [pygame.K_LCTRL,pygame.K_RCTRL]
PASTE_KEY = pygame.K_v
PASTE_KEY_STR = "v"
PASTE_KEY_MOD = [pygame.K_LCTRL,pygame.K_RCTRL]
SCROLL_KEY_MOD = [pygame.K_LSHIFT,pygame.K_RSHIFT]
SCROLL_SPEED = 100
SHAPE_SIZE = 75
VALUE_INPUT_SHAPE_SIZE = 100
KEY_PRESS_REPEAT = (500,25)

INT_MAX_STR_DIGITS = sys.get_int_max_str_digits()
STR_MAX_INT_DIGITS = (10**INT_MAX_STR_DIGITS) - 1

CUR_SUPPORTED_FORMAT = 1

pygame.font.init()
DEFAULT_FONT = pygame.font.SysFont("arial",25)
DEFAULT_FONT_BOLD = pygame.font.SysFont("arial",25,True)
BIG_FONT = pygame.font.SysFont("arial",30)
BIG_FONT_UNDERLINED = pygame.font.SysFont("arial",30)
BIG_FONT_UNDERLINED.set_underline(True)
SMALL_FONT = pygame.font.SysFont("arial",20)

DEFAULT_TEXT_COLOR = (255,255,255)
INPUT_FILE_BG_COLOR = (0,0,0)
BG_COLOR = (50,50,50)
FIXED_UI_BG_COLOR = (40,40,40)
ELEM_COLOR = (75,75,75)
HIGHLIGHTED_COLOR = (127,127,127)
REMOVE_COLOR = (255,0,0)
NONE_COLOR = (0,0,255)
TEXT_INPUT_BG_COLOR = (100,100,100)
ELEM_ON_ELEM_COLOR = (100,100,100)
ELEM_ON_ELEM_ON_ELEM_COLOR = (115,115,115)

ADD_TEXT = DEFAULT_FONT.render("+",1,DEFAULT_TEXT_COLOR)
REMOVE_TEXT = SMALL_FONT.render("X",1,REMOVE_COLOR)
REMOVE_TEXT_HOVER = SMALL_FONT.render("X",1,DEFAULT_TEXT_COLOR)
NONE_TEXT = DEFAULT_FONT.render("None",1,NONE_COLOR)
MOVE_LEFT_TEXT = DEFAULT_FONT.render("\u2190",1,DEFAULT_TEXT_COLOR)
MOVE_UP_TEXT = DEFAULT_FONT.render("\u2191",1,DEFAULT_TEXT_COLOR)
MOVE_RIGHT_TEXT = DEFAULT_FONT.render("\u2192",1,DEFAULT_TEXT_COLOR)
MOVE_DOWN_TEXT = DEFAULT_FONT.render("\u2193",1,DEFAULT_TEXT_COLOR)
INVALID_SHAPE_TEXT = BIG_FONT.render("?",1,DEFAULT_TEXT_COLOR)
NO_MOVE_SURF = pygame.Surface((0,0))
DEFAULT_REMOVE_BUTTON_KWARGS = {
    "elem" : REMOVE_TEXT,
    "hoverable" : True,
    "hoverColor" : REMOVE_COLOR,
    "hoverSurface" : REMOVE_TEXT_HOVER
}

DEFAULT_PADDING = 5
DEFAULT_MARGIN = 5
DEFAULT_MAIN_H_MARGIN = 5 * DEFAULT_MARGIN

SCREEN_IDS_AND_NAMES:list[tuple[str,str]] = [
    ("config","Config"),
    ("levels","Milestones"),
    ("sideUpgrades","Shop"),
    ("sideQuests","Tasks"),
    ("linearUpgrades","Upgrades"),
    ("mechanics","Mechanics")
]

DEFAULT_SHAPE = "CuCuCuCu"

number = int|float
direction = typing.Literal["h","v"]

class OptionalValueFormat:
    def __init__(self,type_:typing.Any,default:typing.Any) -> None:
        self.type_ = type_
        self.default = default
class RestrictedStrFormat:
    def __init__(self,allowedValues:list[str]) -> None:
        self.allowedValues = allowedValues
noFormatCheck = object()

REWARD_TYPES = [
    "BuildingReward",
    "IslandLayoutReward",
    "MechanicReward",
    "WikiEntryReward",
    "BlueprintCurrencyReward",
    "ChunkLimitReward",
    "ResearchPointsReward",
]
COST_TYPES = [
    "ResearchPointsCost"
]
SHAPES_CONFIG_IDS = [
    "DefaultShapesQuadConfiguration",
    "DefaultShapesHexagonalConfiguration"
]
COLOR_SCHEME_IDS = [ # to extend
    "DefaultColorSchemeRGBFlex"
]

SHAPE_COSTS_FORMAT = [
    {
        "Shape" : str,
        "Amount" : int
    }
]
COST_FORMAT = {
    "$type" : RestrictedStrFormat(COST_TYPES),
    "Amount" : OptionalValueFormat(int,None)
}
REWARDS_FORMAT = [
    {
        "$type" : RestrictedStrFormat(REWARD_TYPES),
        "BuildingVariantId" : OptionalValueFormat(str,None),
        "LayoutId" : OptionalValueFormat(str,None),
        "MechanicId" : OptionalValueFormat(str,None),
        "EntryId" : OptionalValueFormat(str,None),
        "Amount" : OptionalValueFormat(int,0), # when 0 chunk limit reward is fixed, change default to None
    }
]
PROGRESSION_FORMAT = {
    "FormatVersion" : int,
    "GameVersion" : int,
    "UniqueId" : str,
    "GameMode" : str,
    "Config" : {
        "BaseChunkLimitMultiplier" : int,
        "LayerMechanicIds" : [str],
        "BlueprintsMechanicId" : str,
        "RailsMechanicId" : str,
        "IslandManagementMechanicId" : str,
        "BlueprintCurrencyShapes" : [
            {
                "Shape" : str,
                "RequiredUpgradeId" : str,
                "Amount" : int
            }
        ],
        "BlueprintDiscountUpgradeId" : str,
        "HubInputSizeUpgradeId" : str,
        "ShapesConfigurationId" : str,
        "ColorSchemeConfigurationId" : str,
        "SpeedsToLinearUpgradeMappings" : {
            "BeltSpeed" : str,
            "CutterSpeed" : str,
            "StackerSpeed" : str,
            "PainterSpeed" : str
        },
        "IntroductionWikiEntryId" : str
    },
    "Progression" : {
        "Levels" : [
            {
                "Id" : str,
                "Rewards" : REWARDS_FORMAT,
                "VideoId" : OptionalValueFormat(str,None),
                "PreviewImageId" : str,
                "Title" : str,
                "Description" : str,
                "Lines" : [
                    {
                        "Shapes" : SHAPE_COSTS_FORMAT
                    }
                ]
            }
        ],
        "SideQuestGroups" : [
            {
                "Title" : str,
                "RequiredUpgradeIds" : [str],
                "SideQuests" : [
                    {
                        "Id" : str,
                        "Rewards" : REWARDS_FORMAT,
                        "Costs" : SHAPE_COSTS_FORMAT
                    }
                ]
            }
        ],
        "SideUpgrades" : [
            {
                "Id" : str,
                "PreviewImageId" : str,
                "VideoId" : OptionalValueFormat(str,None),
                "Title" : str,
                "Description" : str,
                "RequiredUpgradeIds" : [str],
                "Rewards" : REWARDS_FORMAT,
                "Costs" : [COST_FORMAT]
            }
        ],
        "LinearUpgrades" : [
            {
                "Id" : str,
                "Title" : str,
                "Levels" : [
                    {
                        "Value" : int,
                        "Cost" : OptionalValueFormat(COST_FORMAT,None)
                    }
                ],
                "RequiredUpgradeId" : OptionalValueFormat(str,None)
            }
        ],
        "Mechanics" : [
            {
                "Id" : str,
                "Title" : str,
                "Description" : str,
                "IconId" : str
            }
        ]
    },
    "StartingLocation" : noFormatCheck
}

class ProgressionDecodeError(Exception): ...

def decodeProgressionFile(filePath:str) -> tuple[dict,list[str]]:

    try:
        with open(filePath,encoding="utf-8") as f:
            try:
                fileContent = json.load(f)
            except Exception as e:
                raise ProgressionDecodeError("Couldn't parse json") from e
    except OSError as e:
        raise ProgressionDecodeError("Couldn't open file") from e

    warningMsgs = []

    def decodeObjWithFormat(obj:typing.Any,format:typing.Any) -> typing.Any:

        formatType = type(format)
        objType = type(obj)

        if formatType == dict:

            if objType != dict:
                raise ProgressionDecodeError(f"Incorrect object type (expected 'dict' got '{objType.__name__}')")

            newObj = {}

            for formatKey,formatValue in format.items():

                objValue = obj.get(formatKey)

                if type(formatValue) == OptionalValueFormat:
                    if objValue is None:
                        newObj[formatKey] = formatValue.default
                    else:
                        newObj[formatKey] = decodeObjWithFormat(objValue,formatValue.type_)
                else:
                    if objValue is None:
                        raise ProgressionDecodeError(f"Missing dict key ('{formatKey}')")
                    newObj[formatKey] = decodeObjWithFormat(objValue,formatValue)

            for key in obj.keys():
                if format.get(key) is None:
                    warningMsgs.append(f"Skipping key '{key}'")

            return newObj

        if formatType == list:

            if objType != list:
                raise ProgressionDecodeError(f"Incorrect object type (expected 'list' got '{objType.__name__}')")

            newObj = []
            elemFormat = format[0]

            for objElem in obj:

                newObj.append(decodeObjWithFormat(objElem,elemFormat))

            return newObj

        if formatType == RestrictedStrFormat:

            if objType != str:
                raise ProgressionDecodeError(f"Incorrect object type (expected 'str' got '{objType.__name__}')")

            if obj not in format.allowedValues:
                raise ProgressionDecodeError(f"'{obj}' is not part of {format.allowedValues}")

            return obj

        if format is noFormatCheck:
            return obj

        if objType != format:
            raise ProgressionDecodeError(f"Incorrect object type (expected '{format.__name__}' got '{objType.__name__}')")

        return obj

    decodedObj = decodeObjWithFormat(fileContent,PROGRESSION_FORMAT)

    if decodedObj["FormatVersion"] != CUR_SUPPORTED_FORMAT:
        warningMsgs.append(f"Format version ({decodedObj['FormatVersion']}) not supported ({CUR_SUPPORTED_FORMAT})")

    toCheckRewardLists = []

    for level in decodedObj["Progression"]["Levels"]:
        toCheckRewardLists.append(level["Rewards"])
    for sideQuestGroup in decodedObj["Progression"]["SideQuestGroups"]:
        for sideQuest in sideQuestGroup["SideQuests"]:
            toCheckRewardLists.append(sideQuest["Rewards"])
    for sideUpgrade in decodedObj["Progression"]["SideUpgrades"]:
        toCheckRewardLists.append(sideUpgrade["Rewards"])

    for list_ in toCheckRewardLists:
        for reward in list_:
            for rewardType,rewardKey in [
                ("BuildingReward","BuildingVariantId"),
                ("IslandLayoutReward","LayoutId"),
                ("MechanicReward","MechanicId"),
                ("WikiEntryReward","EntryId"),
                ("BlueprintCurrencyReward","Amount"),
                ("ChunkLimitReward","Amount"),
                ("ResearchPointsReward","Amount")
            ]:
                if (reward["$type"] == rewardType) and (reward[rewardKey] is None):
                    raise ProgressionDecodeError(f"Missing '{rewardKey}' key in '{rewardType}'")

    toCheckCostLists = []

    for sideUpgrade in decodedObj["Progression"]["SideUpgrades"]:
        toCheckCostLists.append(sideUpgrade["Costs"])
    for linearUpgrade in decodedObj["Progression"]["LinearUpgrades"]:
        toCheckCostLists.append([l["Cost"] for l in linearUpgrade["Levels"] if l["Cost"] is not None])

    for list_ in toCheckCostLists:
        for cost in list_:
            for costType,costKey in [
                ("ResearchPointsCost","Amount")
            ]:
                if (cost["$type"] == costType) and (cost[costKey] is None):
                    raise ProgressionDecodeError(f"Missing '{costKey}' key in '{costType}'")

    return decodedObj, warningMsgs

def encodeProgressionFile(progression:dict,filePath:str) -> None:

    defaultObj = object()

    def encodeObjWithFormat(obj:typing.Any,format:typing.Any) -> typing.Any:

        formatType = type(format)

        if formatType == dict:

            newObj = {}

            for formatKey,formatValue in format.items():

                objValue = obj.get(formatKey,defaultObj)

                if type(formatValue) == OptionalValueFormat:
                    if (objValue == formatValue.default) or (objValue is defaultObj):
                        continue
                    newObj[formatKey] = encodeObjWithFormat(objValue,formatValue.type_)
                else:
                    newObj[formatKey] = encodeObjWithFormat(objValue,formatValue)

            return newObj

        if formatType == list:

            newObj = []

            for objElem in obj:

                newObj.append(encodeObjWithFormat(objElem,format[0]))

            return newObj

        return obj

    encodedObj = encodeObjWithFormat(progression,PROGRESSION_FORMAT)

    with open(filePath,"w",encoding="utf-8") as f:
        json.dump(encodedObj,f,ensure_ascii=True,indent=4)

def convertProgressionObjToInternalFormat(progressionObj:dict) -> None:

    toConvertRewards:list[tuple[dict,str]] = []
    toConvertRewards.extend((level,"Rewards") for level in progressionObj["Progression"]["Levels"])
    for sideQuestGroup in progressionObj["Progression"]["SideQuestGroups"]:
        toConvertRewards.extend((sideQuest,"Rewards") for sideQuest in sideQuestGroup["SideQuests"])
    toConvertRewards.extend((sideUpgrade,"Rewards") for sideUpgrade in progressionObj["Progression"]["SideUpgrades"])

    for obj,rewardsKey in toConvertRewards:
        curRewards = obj.pop(rewardsKey)
        obj["UnlockBuildingVariants"] = []
        obj["UnlockLayouts"] = []
        obj["UnlockMechanics"] = []
        obj["UnlockWikiEntries"] = []
        obj["RewardBlueprintCurrency"] = 0
        obj["RewardChunkLimit"] = 0
        obj["RewardResearchPoints"] = 0
        for reward in curRewards:
            for rewardType,rewardOldKey,rewardNewKey in [
                ("BuildingReward","BuildingVariantId","UnlockBuildingVariants"),
                ("IslandLayoutReward","LayoutId","UnlockLayouts"),
                ("MechanicReward","MechanicId","UnlockMechanics"),
                ("WikiEntryReward","EntryId","UnlockWikiEntries")
            ]:
                if reward["$type"] == rewardType:
                    obj[rewardNewKey].append(reward[rewardOldKey])
            for rewardType,rewardOldKey,rewardNewKey in [
                ("BlueprintCurrencyReward","Amount","RewardBlueprintCurrency"),
                ("ChunkLimitReward","Amount","RewardChunkLimit"),
                ("ResearchPointsReward","Amount","RewardResearchPoints")
            ]:
                if reward["$type"] == rewardType:
                    obj[rewardNewKey] += reward[rewardOldKey]

    toConvertCosts:list[tuple[dict,str]] = []
    toConvertCosts.extend((sideUpgrade,"Costs") for sideUpgrade in progressionObj["Progression"]["SideUpgrades"])
    for linearUpgrade in progressionObj["Progression"]["LinearUpgrades"]:
        for level in linearUpgrade["Levels"]:
            level["Costs"] = [level.pop("Cost")]
            toConvertCosts.append((level,"Costs"))

    for obj,costsKey in toConvertCosts:
        curCosts = obj.pop(costsKey)
        obj["ResearchPointsCost"] = 0
        for cost in curCosts:
            if cost is None:
                obj["ResearchPointsCost"] = None
            else:
                for costType,costOldKey,costNewKey in [
                    ("ResearchPointsCost","Amount","ResearchPointsCost")
                ]:
                    if cost["$type"] == costType:
                        obj[costNewKey] += cost[costOldKey]

def convertProgressionObjFromInternalFormat(progressionObj:dict) -> None:

    toConvertRewards:list[tuple[dict,str]] = []
    toConvertRewards.extend((level,"Rewards") for level in progressionObj["Progression"]["Levels"])
    for sideQuestGroup in progressionObj["Progression"]["SideQuestGroups"]:
        toConvertRewards.extend((sideQuest,"Rewards") for sideQuest in sideQuestGroup["SideQuests"])
    toConvertRewards.extend((sideUpgrade,"Rewards") for sideUpgrade in progressionObj["Progression"]["SideUpgrades"])

    for obj,rewardsKey in toConvertRewards:
        curRewards = []
        for rewardOldKey,rewardType,rewardNewKey in [
            ("UnlockBuildingVariants","BuildingReward","BuildingVariantId"),
            ("UnlockLayouts","IslandLayoutReward","LayoutId"),
            ("UnlockMechanics","MechanicReward","MechanicId"),
            ("UnlockWikiEntries","WikiEntryReward","EntryId")
        ]:
            for reward in obj[rewardOldKey]:
                curRewards.append({
                    "$type" : rewardType,
                    rewardNewKey : reward
                })
        for rewardOldKey,rewardType,rewardNewKey in [
            ("RewardBlueprintCurrency","BlueprintCurrencyReward","Amount"),
            ("RewardChunkLimit","ChunkLimitReward","Amount"),
            ("RewardResearchPoints","ResearchPointsReward","Amount")
        ]:
            curValue = obj[rewardOldKey]
            if curValue == 0:
                continue
            curRewards.append({
                "$type" : rewardType,
                rewardNewKey : curValue
            })
        obj[rewardsKey] = curRewards

    toConvertCosts:list[tuple[dict,str]] = []
    toConvertCosts.extend((sideUpgrade,"Costs") for sideUpgrade in progressionObj["Progression"]["SideUpgrades"])
    for linearUpgrade in progressionObj["Progression"]["LinearUpgrades"]:
        toConvertCosts.extend((level,"Costs") for level in linearUpgrade["Levels"])

    for obj,costsKey in toConvertCosts:
        curCosts = []
        if obj["ResearchPointsCost"] is None:
            curCosts = [None]
        else:
            for costOldKey,costType,costNewKey in [
                ("ResearchPointsCost","ResearchPointsCost","Amount")
            ]:
                curCosts.append({
                    "$type" : costType,
                    costNewKey : obj[costOldKey]
                })
        obj[costsKey] = curCosts

    for linearUpgrade in progressionObj["Progression"]["LinearUpgrades"]:
        for level in linearUpgrade["Levels"]:
            level["Cost"] = level.pop("Costs")[0]

class ContentBoxElem:

    def __init__(self,
        elem,
        hoverable:bool = False,
        hAlignment:typing.Literal["l","c","r"] = "c",
        vAlignment:typing.Literal["t","c","b"] = "c",
        hPadding:int|None = None,
        vPadding:int|None = None,
        hMargin:int = 0,
        vMargin:int = 0,
        bgColor:tuple[int,int,int]|None = None,
        hoverColor:tuple[int,int,int] = HIGHLIGHTED_COLOR,
        hoverSurface:pygame.Surface|None = None) -> None:

        self.elem:ContentBox|pygame.Surface = elem
        self.elemType:type = type(elem)
        self.hoverable = hoverable
        self.hAlignment:typing.Literal["l","c","r"] = hAlignment
        self.vAlignment:typing.Literal["t","c","b"] = vAlignment
        self.hPadding:int
        self.vPadding:int
        if hPadding is None:
            if self.elemType == ContentBox:
                self.hPadding = 0
            else:
                self.hPadding = DEFAULT_PADDING
        else:
            self.hPadding = hPadding
        if vPadding is None:
            if self.elemType == ContentBox:
                self.vPadding = 0
            else:
                self.vPadding = DEFAULT_PADDING
        else:
            self.vPadding = vPadding
        self.hMargin = hMargin
        self.vMargin = vMargin
        self.bgColor = bgColor
        self.hoverColor = hoverColor
        if hoverSurface is not None:
            if self.elemType != pygame.Surface:
                raise ValueError("Hover surface for non surface elem not supported in ContentBoxElem")
            if elem.get_size() != hoverSurface.get_size():
                raise ValueError("Hover surface not the same size as elem surface in ContentBoxElem")
        self.hoverSurface = hoverSurface
        self.widthWithoutPadding:int
        self.heightWithoutPadding:int
        if self.elemType == ContentBox:
            self.widthWithoutPadding = elem.width
            self.heightWithoutPadding = elem.height
        else:
            self.widthWithoutPadding = elem.get_width()
            self.heightWithoutPadding = elem.get_height()
        self.widthWithPadding:int = self.widthWithoutPadding + (2*self.hPadding)
        self.heightWithPadding:int = self.heightWithoutPadding + (2*self.vPadding)
        self.widthWithPaddingWithMargin:int = self.widthWithPadding + (2*self.hMargin)
        self.heightWithPaddingWithMargin:int = self.heightWithPadding + (2*self.vMargin)
        self.boundingRect:pygame.Rect
        self.pos:tuple[number,number]

class ContentBox:

    def __init__(self,elems:list[ContentBoxElem],elemsDirection:direction) -> None:
        self.elems = elems
        self.elemsDirection:direction = elemsDirection
        widths = [elem.widthWithPaddingWithMargin for elem in elems]
        heights = [elem.heightWithPaddingWithMargin for elem in elems]
        self.width:int
        self.height:int
        if elemsDirection == "h":
            self.width = sum(widths)
            self.height = max(heights)
        else:
            self.width = max(widths)
            self.height = sum(heights)

    def calculateBoundingRects(self,x:number=0,y:number=0) -> None:

        if self.elemsDirection == "h":
            curCoord = x
        else:
            curCoord = y

        for elem in self.elems:

            curBoundingRect = pygame.Rect(
                (curCoord if self.elemsDirection == "h" else x) + elem.hMargin,
                (curCoord if self.elemsDirection == "v" else y) + elem.vMargin,
                elem.widthWithPadding if self.elemsDirection == "h" else self.width - (2*elem.hMargin),
                elem.heightWithPadding if self.elemsDirection == "v" else self.height - (2*elem.vMargin)
            )

            if elem.hAlignment == "c":
                curElemX = curBoundingRect.x + (curBoundingRect.width/2) - (elem.widthWithoutPadding/2)
            elif elem.hAlignment == "l":
                curElemX = curBoundingRect.x + elem.hPadding
            else:
                curElemX = curBoundingRect.x + curBoundingRect.width - elem.hPadding - elem.widthWithoutPadding

            if elem.vAlignment == "c":
                curElemY = curBoundingRect.y + (curBoundingRect.height/2) - (elem.heightWithoutPadding/2)
            elif elem.vAlignment == "t":
                curElemY = curBoundingRect.y + elem.vPadding
            else:
                curElemY = curBoundingRect.y + curBoundingRect.height - elem.vPadding - elem.heightWithoutPadding

            elem.boundingRect = curBoundingRect
            elem.pos = (curElemX,curElemY)

            if elem.elemType == ContentBox:
                elem.elem.calculateBoundingRects(curElemX,curElemY)

            if self.elemsDirection == "h":
                curCoord += curBoundingRect.width + (2*elem.hMargin)
            else:
                curCoord += curBoundingRect.height + (2*elem.vMargin)

    def render(
        self,
        surf:pygame.Surface,
        mousePosX:int,
        mousePosY:int,
        isFixedUI:bool=False,
        cullInfo:tuple[tuple[int,int],tuple[int,int]]|None=None
    ) -> None:

        global debugCulled, debugNotCulled

        if not isFixedUI:
            curWinRect = pygame.Rect(
                -cullInfo[0][0],
                -cullInfo[0][1],
                cullInfo[1][0],
                cullInfo[1][1]
            )

        for elem in self.elems:

            if (not isFixedUI) and (not elem.boundingRect.colliderect(curWinRect)):
                if DEBUG:
                    debugCulled += 1
                continue
            if DEBUG and (not isFixedUI):
                debugNotCulled += 1

            if (not isFixedUI) and (isMouseOverFixedUI):
                curElemHovered = False
            else:
                curElemHovered = elem.boundingRect.collidepoint(mousePosX,mousePosY)

            if curElemHovered and elem.hoverable:
                curElemBgColor = elem.hoverColor
            else:
                curElemBgColor = elem.bgColor

            if curElemBgColor is not None:
                pygame.draw.rect(surf,curElemBgColor,elem.boundingRect)

            if elem.elemType == ContentBox:
                elem.elem.render(surf,mousePosX,mousePosY,isFixedUI,cullInfo)
            else:
                surf.blit(
                    elem.hoverSurface if (elem.hoverSurface is not None) and curElemHovered else elem.elem,
                    elem.pos
                )

            if DEBUG:
                pygame.draw.rect(surf,(0,255,0),elem.boundingRect,1)

def main() -> None:

    global isMouseOverFixedUI, debugCulled, debugNotCulled

    def logMsg(msg:str) -> None:
        print(msg)

    def decodeInputtedFilePath(filePath:str) -> None:
        nonlocal curProgression, curProgressionFilePath, curInputFileError
        nonlocal curBPCurrencyShapesList, curLevelsList, curSideQuestGroupsList, curSideUpgradesList, curLinearUpgradesList, curMechanicsList
        try:
            curProgression, warningMsgs = decodeProgressionFile(filePath)
        except ProgressionDecodeError as e:
            curInputFileError = e
            return
        for msg in warningMsgs:
            logMsg(f"Warning : {msg}")
        convertProgressionObjToInternalFormat(curProgression)
        curProgressionFilePath = filePath
        curInputFileError = None
        curBPCurrencyShapesList = curProgression["Config"]["BlueprintCurrencyShapes"]
        curLevelsList = curProgression["Progression"]["Levels"]
        curSideQuestGroupsList = curProgression["Progression"]["SideQuestGroups"]
        curSideUpgradesList = curProgression["Progression"]["SideUpgrades"]
        curLinearUpgradesList = curProgression["Progression"]["LinearUpgrades"]
        curMechanicsList = curProgression["Progression"]["Mechanics"]
        changeScreen("config")
        logMsg(f"Decoded progression file : {filePath}")

    def askForInput(
        inputType:typing.Literal["int","str","shape"],
        putValueInObj:dict|list,
        putValueInKey:str|int,
        presets:list[str]|None = None,
        canBeNone:bool = False,
        line2Callable:typing.Callable[[str],pygame.Surface]|None = None
    ) -> None:
        nonlocal curValueInputInfos
        previousValue = putValueInObj[putValueInKey]
        curValueInputInfos = {
            "type" : inputType,
            "putValueInObj" : putValueInObj,
            "putValueInKey" : putValueInKey,
            "presets" : presets,
            "canBeNone" : canBeNone,
            "line2Callable" : line2Callable,
            "valueInputInTopBar" : presets is not None,
            "curInputText" : str(previousValue) if (inputType == "int") and (previousValue is not None) else previousValue,
            "previousScreen" : screen,
            "previousScrollOffsets" : (hScrollOffset,vScrollOffset)
        }
        changeScreen("valueInput")

    def saveChanges(autoTriggered:bool=True) -> None:
        if (not autoSave) and autoTriggered:
            return
        convertProgressionObjFromInternalFormat(curProgression)
        encodeProgressionFile(curProgression,curProgressionFilePath)
        logMsg("Saved changes")

    def renderShape(shapeCode:str,size:int=SHAPE_SIZE) -> pygame.Surface:
        curKey = (shapeCode,size,shapesColorSkin)
        if renderedShapesCache.get(curKey) is None:
            if DEBUG:
                print(f"Rendering {shapeCode=}, {size=}, {shapesColorSkin=}")
            try:
                shapeSurf = shapeViewer.renderShape(shapeCode,size,shapesColorSkin)
            except Exception:
                shapeSurf = INVALID_SHAPE_TEXT
            renderedShapesCache[curKey] = shapeSurf
        return renderedShapesCache[curKey]

    def getValidScrollOffsets() -> None:

        nonlocal hScrollOffset, vScrollOffset

        winWidth, winHeight = win.get_size()

        hScrollOffset = max(hScrollOffset,-curScrollableSurf.get_width()+winWidth)
        vScrollOffset = max(vScrollOffset,-curScrollableSurf.get_height()+winHeight-curBottomBarSurf.get_height())

        hScrollOffset = min(hScrollOffset,0)
        vScrollOffset = min(vScrollOffset,curTopBarSurf.get_height())

    def getRectifiedMousePos(mousePosX:int,mousePosY:int) -> tuple[int,int]:
        return mousePosX-hScrollOffset, mousePosY-vScrollOffset

    global getScrollSurfBlitPos
    def getScrollSurfBlitPos() -> tuple[int,int]:
        return hScrollOffset, vScrollOffset

    def changeScreen(newValue:str,hScrollOffsetOverride:int|None=None,vScrollOffsetOverride:int|None=None) -> None:
        nonlocal screen, hScrollOffset, vScrollOffset, checkScrollOffsets, createCurContentBoxes
        if hScrollOffsetOverride is None:
            hScrollOffset = 0
        else:
            hScrollOffset = hScrollOffsetOverride
        if vScrollOffsetOverride is None:
            if screen == "inputFile":
                vScrollOffset = winHeight
            else:
                vScrollOffset = curTopBarSurf.get_height()
        else:
            vScrollOffset = vScrollOffsetOverride
        checkScrollOffsets = True
        createCurContentBoxes = True
        screen = newValue

    def moveElemForward(list_:list,index:int) -> None:
        list_.insert(index+1,list_.pop(index))
        fileChanged()

    def moveElemBackward(list_:list,index:int) -> None:
        list_.insert(index-1,list_.pop(index))
        fileChanged()

    def checkForMoveElem(moveArrows:list[ContentBoxElem],list_:list,index:int,mousePos:tuple[int,int]) -> bool:
        if moveArrows[0].boundingRect.collidepoint(mousePos):
            if index == 0:
                moveElemForward(list_,index)
            else:
                moveElemBackward(list_,index)
            return True
        if (
            (index not in (0,len(list_)-1))
            and (moveArrows[1].boundingRect.collidepoint(mousePos))
        ):
            moveElemForward(list_,index)
            return True
        return False

    def getMoveArrowsList(list_:list,index:int,elemsDir:direction) -> list[ContentBoxElem]:
        moveArrows = []
        if index != 0:
            moveArrows.append(ContentBoxElem(
                MOVE_LEFT_TEXT if elemsDir == "h" else MOVE_UP_TEXT,
                True
            ))
        if index != len(list_)-1:
            moveArrows.append(ContentBoxElem(
                MOVE_RIGHT_TEXT if elemsDir == "h" else MOVE_DOWN_TEXT,
                True
            ))
        if moveArrows == []:
            moveArrows.append(ContentBoxElem(NO_MOVE_SURF,hPadding=0,vPadding=0))
        return moveArrows

    DIGITS = [str(i) for i in range(10)]
    def isDigit(char:str):
        return char in DIGITS

    def addValueInputText(text:str) -> None:
        if curValueInputInfos["curInputText"] is None:
            newValue = text
        else:
            if (curValueInputInfos["type"] == "int") and any((not isDigit(c)) for c in text):
                return
            newValue = curValueInputInfos["curInputText"] + text
        if (curValueInputInfos["type"] != "int") or (len(newValue.removeprefix("-")) <= INT_MAX_STR_DIGITS):
            if curValueInputInfos["type"] == "int":
                curValueInputInfos["curInputText"] = str(int(newValue))
            else:
                curValueInputInfos["curInputText"] = newValue

    def renderCanBeNoneText(renderFunc:typing.Callable[...,pygame.Surface],*args) -> pygame.Surface:
        if args[0] is None:
            return NONE_TEXT
        return renderFunc(*args)

    def confirmValueInputChanges() -> None:
        nonlocal curValueInputInfos
        if (curValueInputInfos["type"] == "int") and (curValueInputInfos["curInputText"] is not None):
            newValue = int(curValueInputInfos["curInputText"])
        else:
            newValue = curValueInputInfos["curInputText"]
        curValueInputInfos["putValueInObj"][curValueInputInfos["putValueInKey"]] = newValue
        fileChanged()
        changeScreen(curValueInputInfos["previousScreen"],*curValueInputInfos["previousScrollOffsets"])
        curValueInputInfos = None

    def addAddButtons(list_:list[ContentBoxElem],elemsDir:direction) -> list[ContentBoxElem]:
        newList = []
        marginKey = "hMargin" if elemsDir == "h" else "vMargin"
        for elem in list_+[None]:
            newList.append(ContentBoxElem(ADD_TEXT,True,**{marginKey:DEFAULT_MARGIN}))
            if elem is not None:
                newList.append(elem)
        return newList

    def defaultRenderText(text:str,bold:bool=False) -> pygame.Surface:
        curKey = (text,bold)
        if renderedTextsCache.get(curKey) is None:
            if DEBUG:
                print(f"Rendering {bold=}, {text=}")
            renderedTextsCache[curKey] = (DEFAULT_FONT_BOLD if bold else DEFAULT_FONT).render(text,1,DEFAULT_TEXT_COLOR)
        return renderedTextsCache[curKey]

    def getDefaultEditableListContentBoxes(list_:list[str]) -> list[ContentBoxElem]:
        return [
            ContentBoxElem(ContentBox([
                ContentBoxElem(defaultRenderText(elem),True),
                ContentBoxElem(**DEFAULT_REMOVE_BUTTON_KWARGS)
            ],"h")) for elem in list_
        ]+[
            ContentBoxElem(ADD_TEXT,True)
        ]

    def handleClicksForDefaultEditableList(contentBox:ContentBox,list_:list[str],mousePos:tuple[int,int],presets:list[str]|None=None) -> bool:
        for i,elem in enumerate(contentBox.elems):
            if i == len(list_):
                if elem.boundingRect.collidepoint(mousePos):
                    list_.append("")
                    askForInput("str",list_,i,presets)
                    return True
            else:
                if elem.elem.elems[0].boundingRect.collidepoint(mousePos):
                    askForInput("str",list_,i,presets)
                    return True
                if elem.elem.elems[1].boundingRect.collidepoint(mousePos):
                    list_.pop(i)
                    fileChanged()
                    return True
        return False

    def getMultipliedChunkLimitReward(rawReward:int) -> str:
        try:
            mulValue = str(rawReward*curProgression["Config"]["BaseChunkLimitMultiplier"])
        except ValueError:
            mulValue = "?"
        return mulValue

    def fileChanged() -> None:
        nonlocal createCurContentBoxes, checkScrollOffsets
        saveChanges()
        createCurContentBoxes = True
        checkScrollOffsets = True

    def handleClickEvent(clickPos:tuple[int,int]) -> None:

        nonlocal curValueInputInfos, autoSave, shapesColorSkin, createCurContentBoxes

        if screen == "inputFile":
            return

        rectifiedMousePos = getRectifiedMousePos(*clickPos)

        def valueInputNoneClickedCheck() -> bool:
            if curValueInputInfos["canBeNone"]:
                if curValueInputNoneContentBox.elems[1].boundingRect.collidepoint(
                    mousePos[0] - curValueInputX - curValueInputNoneXOffset,
                    mousePos[1] - curValueInputY - curValueInputNoneYOffset
                ):
                    curValueInputInfos["curInputText"] = None
                    return True
            return False

        if isMouseOverFixedUI:

            if (curValueInputInfos is None) or (not curValueInputInfos["valueInputInTopBar"]):
                for i,elem in enumerate(curTopBarContentBox.elems):
                    if elem.boundingRect.collidepoint(mousePos[0]-curTopBarOffset,mousePos[1]):
                        changeScreen(SCREEN_IDS_AND_NAMES[i][0])
                        curValueInputInfos = None
                        return
            else:
                if valueInputNoneClickedCheck():
                    return

            if (
                curBottomBarLeftContentBox
                .elems[0]
                .boundingRect
                .collidepoint(mousePos[0]-curBottomBarLeftOffset,mousePos[1]-curBottomBarY)
            ):
                autoSave = not autoSave
                return

            if (screen == "valueInput") and (
                curBottomBarMiddleContentBox
                .elems[0]
                .boundingRect
                .collidepoint(mousePos[0]-curBottomBarMiddleOffset,mousePos[1]-curBottomBarY)
            ):
                confirmValueInputChanges()
                return

            if (
                curBottomBarRightContentBox
                .elems[0]
                .boundingRect
                .collidepoint(mousePos[0]-curBottomBarRightOffset,mousePos[1]-curBottomBarY)
            ):
                shapesColorSkin = shapeViewer.EXTERNAL_COLOR_SKINS[
                    (shapeViewer.EXTERNAL_COLOR_SKINS.index(shapesColorSkin)+1)
                    % len(shapeViewer.EXTERNAL_COLOR_SKINS)
                ]
                createCurContentBoxes = True
                return

            return

        if screen == "config":

            curElemIndex = 0

            for inputType,key in [
                ("int","GameVersion"),
                ("str","UniqueId"),
                ("str","GameMode")
            ]:
                if configScreenContentBox.elems[curElemIndex].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                    askForInput(inputType,curProgression,key)
                    return
                curElemIndex += 1

            if configScreenContentBox.elems[curElemIndex].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                askForInput("int",curProgression["Config"],"BaseChunkLimitMultiplier")
                return
            curElemIndex += 2

            if handleClicksForDefaultEditableList(
                configScreenContentBox.elems[curElemIndex].elem,
                curProgression["Config"]["LayerMechanicIds"],
                rectifiedMousePos,
                defaultValues["mechanicIds"]
            ):
                return
            curElemIndex += 1

            for key in ["BlueprintsMechanicId","RailsMechanicId","IslandManagementMechanicId"]:
                if configScreenContentBox.elems[curElemIndex].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                    askForInput(
                        "str",
                        curProgression["Config"],
                        key,
                        defaultValues["mechanicIds"]
                    )
                    return
                curElemIndex += 1

            curElemIndex += 1
            for i,elem in enumerate(configScreenContentBox.elems[curElemIndex].elem.elems):
                curActualIndex,isNotAddButton = divmod(i,2)
                if not isNotAddButton:
                    if elem.boundingRect.collidepoint(rectifiedMousePos):
                        curBPCurrencyShapesList.insert(curActualIndex,{
                            "Shape": DEFAULT_SHAPE,
                            "RequiredUpgradeId": defaultValues["nodeIds"][0],
                            "Amount": 0
                        })
                        fileChanged()
                        return
                else:
                    if checkForMoveElem(
                        elem.elem.elems[0].elem.elems,
                        curBPCurrencyShapesList,
                        curActualIndex,
                        rectifiedMousePos
                    ):
                        return
                    if elem.elem.elems[1].elem.elems[0].boundingRect.collidepoint(rectifiedMousePos):
                        askForInput("shape",curBPCurrencyShapesList[curActualIndex],"Shape")
                        return
                    if elem.elem.elems[1].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                        askForInput("int",curBPCurrencyShapesList[curActualIndex],"Amount")
                        return
                    if elem.elem.elems[2].boundingRect.collidepoint(rectifiedMousePos):
                        askForInput(
                            "str",
                            curBPCurrencyShapesList[curActualIndex],
                            "RequiredUpgradeId",
                            defaultValues["nodeIds"]
                        )
                        return
                    if elem.elem.elems[3].boundingRect.collidepoint(rectifiedMousePos):
                        curBPCurrencyShapesList.pop(curActualIndex)
                        fileChanged()
                        return
            curElemIndex += 1

            for key in ["BlueprintDiscountUpgradeId","HubInputSizeUpgradeId"]:
                if configScreenContentBox.elems[curElemIndex].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                    askForInput(
                        "str",
                        curProgression["Config"],
                        key,
                        defaultValues["linearUpgradeIds"]
                    )
                    return
                curElemIndex += 1

            for key,_ in speedsToLinearUpgradeMappings:
                if configScreenContentBox.elems[curElemIndex].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                    askForInput(
                        "str",
                        curProgression["Config"]["SpeedsToLinearUpgradeMappings"],
                        key,
                        defaultValues["linearUpgradeIds"]
                    )
                    return
                curElemIndex += 1

            if configScreenContentBox.elems[curElemIndex].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                askForInput(
                    "str",
                    curProgression["Config"],
                    "ShapesConfigurationId",
                    SHAPES_CONFIG_IDS
                )
                return
            curElemIndex += 1

            if configScreenContentBox.elems[curElemIndex].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                askForInput(
                    "str",
                    curProgression["Config"],
                    "ColorSchemeConfigurationId",
                    COLOR_SCHEME_IDS
                )
                return
            curElemIndex += 1

            if configScreenContentBox.elems[curElemIndex].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                askForInput(
                    "str",
                    curProgression["Config"],
                    "IntroductionWikiEntryId",
                    defaultValues["wikiEntries"]
                )
                return
            curElemIndex += 1

        elif screen == "levels":

            for levelIndex,level in enumerate(levelsScreenContentBox.elems):
                curActualLevelIndex,isNotLevelAddButton = divmod(levelIndex,2)
                if not isNotLevelAddButton:
                    if level.boundingRect.collidepoint(rectifiedMousePos):
                        curLevelsList.insert(curActualLevelIndex,{
                            "Id" : defaultValues["nodeIds"][0],
                            "VideoId" : None,
                            "PreviewImageId" : defaultValues["images"][0],
                            "Title" : defaultValues["nodeTitles"][0],
                            "Description" : defaultValues["nodeDescriptions"][0],
                            "Lines" : [],
                            "UnlockBuildingVariants" : [],
                            "UnlockLayouts" : [],
                            "UnlockMechanics" : [],
                            "UnlockWikiEntries" : [],
                            "RewardBlueprintCurrency" : 0,
                            "RewardChunkLimit" : 0,
                            "RewardResearchPoints" : 0
                        })
                        fileChanged()
                        return
                else:

                    curElemIndex = 1

                    if checkForMoveElem(
                        level.elem.elems[curElemIndex].elem.elems,
                        curLevelsList,
                        curActualLevelIndex,
                        rectifiedMousePos
                    ):
                        return
                    curElemIndex += 1

                    for key,presets,canBeNone in [
                        ("Id",defaultValues["nodeIds"],False),
                        ("VideoId",defaultValues["videos"],True),
                        ("PreviewImageId",defaultValues["images"],False),
                        ("Title",defaultValues["nodeTitles"],False),
                        ("Description",defaultValues["nodeDescriptions"],False),
                    ]:
                        if level.elem.elems[curElemIndex].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                            askForInput("str",curLevelsList[curActualLevelIndex],key,presets,canBeNone)
                            return
                        curElemIndex += 1

                    curElemIndex += 1
                    for shapeLineIndex,shapeLine in enumerate(level.elem.elems[curElemIndex].elem.elems):
                        curActualShapeLineIndex,isNotShapeLineAddButton = divmod(shapeLineIndex,2)
                        curShapeLinesList = curLevelsList[curActualLevelIndex]["Lines"]
                        if not isNotShapeLineAddButton:
                            if shapeLine.boundingRect.collidepoint(rectifiedMousePos):
                                curShapeLinesList.insert(curActualShapeLineIndex,{
                                    "Shapes" : []
                                })
                                fileChanged()
                                return
                        else:

                            if checkForMoveElem(
                                shapeLine.elem.elems[0].elem.elems,
                                curShapeLinesList,
                                curActualShapeLineIndex,
                                rectifiedMousePos
                            ):
                                return

                            for shapeIndex,shape in enumerate(shapeLine.elem.elems[1].elem.elems):
                                curActualShapeIndex,isNotShapeAddButton = divmod(shapeIndex,2)
                                curShapesList = curShapeLinesList[curActualShapeLineIndex]["Shapes"]
                                if not isNotShapeAddButton:
                                    if shape.boundingRect.collidepoint(rectifiedMousePos):
                                        curShapesList.insert(curActualShapeIndex,{
                                            "Shape" : DEFAULT_SHAPE,
                                            "Amount" : 0
                                        })
                                        fileChanged()
                                        return
                                else:

                                    if checkForMoveElem(
                                        shape.elem.elems[0].elem.elems,
                                        curShapesList,
                                        curActualShapeIndex,
                                        rectifiedMousePos
                                    ):
                                        return

                                    if shape.elem.elems[1].elem.elems[0].boundingRect.collidepoint(rectifiedMousePos):
                                        askForInput("shape",curShapesList[curActualShapeIndex],"Shape")
                                        return
                                    if shape.elem.elems[1].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                                        askForInput("int",curShapesList[curActualShapeIndex],"Amount")
                                        return
                                    if shape.elem.elems[2].boundingRect.collidepoint(rectifiedMousePos):
                                        curShapesList.pop(curActualShapeIndex)
                                        fileChanged()
                                        return

                            if shapeLine.elem.elems[2].boundingRect.collidepoint(rectifiedMousePos):
                                curShapeLinesList.pop(curActualShapeLineIndex)
                                fileChanged()
                                return

                    curElemIndex += 1

                    for key,presets in [
                        ("UnlockBuildingVariants",defaultValues["buildingVariants"]),
                        ("UnlockLayouts",defaultValues["islandLayouts"]),
                        ("UnlockWikiEntries",defaultValues["wikiEntries"]),
                        ("UnlockMechanics",defaultValues["mechanicIds"])
                    ]:
                        curElemIndex += 1
                        if handleClicksForDefaultEditableList(
                            level.elem.elems[curElemIndex].elem,
                            curLevelsList[curActualLevelIndex][key],
                            rectifiedMousePos,
                            presets
                        ):
                            return
                        curElemIndex += 1

                    for key in [
                        "RewardChunkLimit",
                        "RewardResearchPoints",
                        "RewardBlueprintCurrency"
                    ]:
                        if level.elem.elems[curElemIndex].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                            askForInput(
                                "int",
                                curLevelsList[curActualLevelIndex],
                                key,
                                line2Callable = (
                                    (lambda n: defaultRenderText(getMultipliedChunkLimitReward(int(n))))
                                    if key == "RewardChunkLimit" else
                                    None
                                )
                            )
                            return
                        curElemIndex += 1

                    if level.elem.elems[curElemIndex].boundingRect.collidepoint(rectifiedMousePos):
                        curLevelsList.pop(curActualLevelIndex)
                        fileChanged()
                        return

        elif screen == "sideUpgrades":

            for sideUpgradeIndex,sideUpgrade in enumerate(sideUpgradesScreenContentBox.elems):
                curActualSideUpgradeIndex,isNotSideUpgradeAddButton = divmod(sideUpgradeIndex,2)
                if not isNotSideUpgradeAddButton:
                    if sideUpgrade.boundingRect.collidepoint(rectifiedMousePos):
                        curSideUpgradesList.insert(curActualSideUpgradeIndex,{
                            "Id" : defaultValues["nodeIds"][0],
                            "VideoId" : None,
                            "PreviewImageId" : defaultValues["images"][0],
                            "Title" : defaultValues["nodeTitles"][0],
                            "Description" : defaultValues["nodeDescriptions"][0],
                            "RequiredUpgradeIds" : [],
                            "UnlockBuildingVariants" : [],
                            "UnlockLayouts" : [],
                            "UnlockMechanics" : [],
                            "UnlockWikiEntries" : [],
                            "RewardBlueprintCurrency" : 0,
                            "RewardChunkLimit" : 0,
                            "RewardResearchPoints" : 0,
                            "ResearchPointsCost" : 0
                        })
                        fileChanged()
                        return
                else:

                    if checkForMoveElem(
                        sideUpgrade.elem.elems[0].elem.elems,
                        curSideUpgradesList,
                        curActualSideUpgradeIndex,
                        rectifiedMousePos
                    ):
                        return

                    for i,(key,presets,canBeNone) in enumerate([
                        ("Id",defaultValues["nodeIds"],False),
                        ("VideoId",defaultValues["videos"],True),
                        ("PreviewImageId",defaultValues["images"],False),
                        ("Title",defaultValues["nodeTitles"],False),
                        ("Description",defaultValues["nodeDescriptions"],False),
                    ]):
                        if sideUpgrade.elem.elems[1].elem.elems[i].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                            askForInput("str",curSideUpgradesList[curActualSideUpgradeIndex],key,presets,canBeNone)
                            return

                    if handleClicksForDefaultEditableList(
                        sideUpgrade.elem.elems[3].elem.elems[1].elem,
                        curSideUpgradesList[curActualSideUpgradeIndex]["RequiredUpgradeIds"],
                        rectifiedMousePos,
                        defaultValues["nodeIds"]
                    ):
                        return

                    if sideUpgrade.elem.elems[3].elem.elems[2].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                        askForInput("int",curSideUpgradesList[curActualSideUpgradeIndex],"ResearchPointsCost")
                        return

                    for i,(key,presets) in enumerate([
                        ("UnlockBuildingVariants",defaultValues["buildingVariants"]),
                        ("UnlockLayouts",defaultValues["islandLayouts"]),
                        ("UnlockWikiEntries",defaultValues["wikiEntries"]),
                        ("UnlockMechanics",defaultValues["mechanicIds"])
                    ]):
                        if handleClicksForDefaultEditableList(
                            sideUpgrade.elem.elems[5].elem.elems[(i*2)+1].elem,
                            curSideUpgradesList[curActualSideUpgradeIndex][key],
                            rectifiedMousePos,
                            presets
                        ):
                            return

                    for i,key in enumerate([
                        "RewardChunkLimit",
                        "RewardResearchPoints",
                        "RewardBlueprintCurrency"
                    ]):
                        if sideUpgrade.elem.elems[7].elem.elems[i].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                            askForInput(
                                "int",
                                curSideUpgradesList[curActualSideUpgradeIndex],
                                key,
                                line2Callable = (
                                    (lambda n: defaultRenderText(getMultipliedChunkLimitReward(int(n))))
                                    if key == "RewardChunkLimit" else
                                    None
                                )
                            )
                            return

                    if sideUpgrade.elem.elems[8].boundingRect.collidepoint(rectifiedMousePos):
                        curSideUpgradesList.pop(curActualSideUpgradeIndex)
                        fileChanged()
                        return

        elif screen == "sideQuests":

            for sideQuestGroupIndex,sideQuestGroup in enumerate(sideQuestsScreenContentBox.elems):
                curActualSideQuestGroupIndex,isNotSideQuestGroupAddButton = divmod(sideQuestGroupIndex,2)
                if not isNotSideQuestGroupAddButton:
                    if sideQuestGroup.boundingRect.collidepoint(rectifiedMousePos):
                        curSideQuestGroupsList.insert(curActualSideQuestGroupIndex,{
                            "Title" : defaultValues["sideQuestGroupTitles"][0],
                            "RequiredUpgradeIds" : [],
                            "SideQuests" : []
                        })
                        fileChanged()
                        return
                else:

                    if checkForMoveElem(
                        sideQuestGroup.elem.elems[0].elem.elems,
                        curSideQuestGroupsList,
                        curActualSideQuestGroupIndex,
                        rectifiedMousePos
                    ):
                        return

                    if sideQuestGroup.elem.elems[1].elem.elems[0].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                        askForInput(
                            "str",
                            curSideQuestGroupsList[curActualSideQuestGroupIndex],
                            "Title",
                            defaultValues["sideQuestGroupTitles"]
                        )
                        return

                    if handleClicksForDefaultEditableList(
                        sideQuestGroup.elem.elems[1].elem.elems[2].elem,
                        curSideQuestGroupsList[curActualSideQuestGroupIndex]["RequiredUpgradeIds"],
                        rectifiedMousePos,
                        defaultValues["nodeIds"]
                    ):
                        return

                    for sideQuestIndex,sideQuest in enumerate(sideQuestGroup.elem.elems[1].elem.elems[4].elem.elems):
                        curActualSideQuestIndex,isNotSideQuestAddButton = divmod(sideQuestIndex,2)
                        curSideQuestsList = curSideQuestGroupsList[curActualSideQuestGroupIndex]["SideQuests"]
                        if not isNotSideQuestAddButton:
                            if sideQuest.boundingRect.collidepoint(rectifiedMousePos):
                                curSideQuestsList.insert(curActualSideQuestIndex,{
                                    "Id" : defaultValues["sideQuestIds"][0],
                                    "RequiredUpgradeIds" : [],
                                    "UnlockBuildingVariants" : [],
                                    "UnlockLayouts" : [],
                                    "UnlockMechanics" : [],
                                    "UnlockWikiEntries" : [],
                                    "RewardBlueprintCurrency" : 0,
                                    "RewardChunkLimit" : 0,
                                    "RewardResearchPoints" : 0,
                                    "Costs" : []
                                })
                                fileChanged()
                                return
                        else:

                            if checkForMoveElem(
                                sideQuest.elem.elems[0].elem.elems,
                                curSideQuestsList,
                                curActualSideQuestIndex,
                                rectifiedMousePos
                            ):
                                return

                            if (
                                sideQuest.elem.elems[1]
                                .elem.elems[0]
                                .elem.elems[0]
                                .elem.elems[1]
                                .boundingRect.collidepoint(rectifiedMousePos)
                            ):
                                askForInput("str",curSideQuestsList[curActualSideQuestIndex],"Id",defaultValues["sideQuestIds"])
                                return

                            for shapeCostIndex,shapeCost in enumerate(sideQuest.elem.elems[1].elem.elems[0].elem.elems[2].elem.elems):
                                curActualShapeCostIndex,isNotShapeCostAddButton = divmod(shapeCostIndex,2)
                                curShapeCostsList = curSideQuestsList[curActualSideQuestIndex]["Costs"]
                                if not isNotShapeCostAddButton:
                                    if shapeCost.boundingRect.collidepoint(rectifiedMousePos):
                                        curShapeCostsList.insert(curActualShapeCostIndex,{
                                            "Shape" : DEFAULT_SHAPE,
                                            "Amount" : 0
                                        })
                                        fileChanged()
                                        return
                                else:

                                    if checkForMoveElem(
                                        shapeCost.elem.elems[0].elem.elems,
                                        curShapeCostsList,
                                        curActualShapeCostIndex,
                                        rectifiedMousePos
                                    ):
                                        return

                                    if shapeCost.elem.elems[1].elem.elems[0].boundingRect.collidepoint(rectifiedMousePos):
                                        askForInput("shape",curShapeCostsList[curActualShapeCostIndex],"Shape")
                                        return
                                    if shapeCost.elem.elems[1].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                                        askForInput("int",curShapeCostsList[curActualShapeCostIndex],"Amount")
                                        return

                                    if shapeCost.elem.elems[2].boundingRect.collidepoint(rectifiedMousePos):
                                        curShapeCostsList.pop(curActualShapeCostIndex)
                                        fileChanged()
                                        return

                            for i,(key,presets) in enumerate([
                                ("UnlockBuildingVariants",defaultValues["buildingVariants"]),
                                ("UnlockLayouts",defaultValues["islandLayouts"]),
                                ("UnlockWikiEntries",defaultValues["wikiEntries"]),
                                ("UnlockMechanics",defaultValues["mechanicIds"])
                            ]):
                                if handleClicksForDefaultEditableList(
                                    sideQuest.elem.elems[1].elem.elems[2].elem.elems[(i*2)+1].elem,
                                    curSideQuestsList[curActualSideQuestIndex][key],
                                    rectifiedMousePos,
                                    presets
                                ):
                                    return

                            for i,key in enumerate([
                                "RewardChunkLimit",
                                "RewardResearchPoints",
                                "RewardBlueprintCurrency"
                            ]):
                                if (
                                    sideQuest.elem.elems[1]
                                    .elem.elems[4]
                                    .elem.elems[i]
                                    .elem.elems[1]
                                    .boundingRect.collidepoint(rectifiedMousePos)
                                ):
                                    askForInput(
                                        "int",
                                        curSideQuestsList[curActualSideQuestIndex],
                                        key,
                                        line2Callable = (
                                            (lambda n: defaultRenderText(getMultipliedChunkLimitReward(int(n))))
                                            if key == "RewardChunkLimit" else
                                            None
                                        )
                                    )
                                    return

                            if sideQuest.elem.elems[2].boundingRect.collidepoint(rectifiedMousePos):
                                curSideQuestsList.pop(curActualSideQuestIndex)
                                fileChanged()
                                return

                    if sideQuestGroup.elem.elems[2].boundingRect.collidepoint(rectifiedMousePos):
                        curSideQuestGroupsList.pop(curActualSideQuestGroupIndex)
                        fileChanged()
                        return

        elif screen == "linearUpgrades":

            for linearUpgradeIndex,linearUpgrade in enumerate(linearUpgradesScreenContentBox.elems):
                curActualLinearUpgradeIndex,isNotLinearUpgradeAddButton = divmod(linearUpgradeIndex,2)
                if not isNotLinearUpgradeAddButton:
                    if linearUpgrade.boundingRect.collidepoint(rectifiedMousePos):
                        curLinearUpgradesList.insert(curActualLinearUpgradeIndex,{
                            "Id" : defaultValues["linearUpgradeIds"][0],
                            "Title" : defaultValues["linearUpgradeTitles"][0],
                            "Levels" : [],
                            "RequiredUpgradeId" : None
                        })
                        fileChanged()
                        return
                else:

                    if checkForMoveElem(
                        linearUpgrade.elem.elems[0].elem.elems,
                        curLinearUpgradesList,
                        curActualLinearUpgradeIndex,
                        rectifiedMousePos
                    ):
                        return

                    if linearUpgrade.elem.elems[1].elem.elems[0].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                        askForInput(
                            "str",
                            curLinearUpgradesList[curActualLinearUpgradeIndex],
                            "Id",
                            defaultValues["linearUpgradeIds"]
                        )
                        return
                    if linearUpgrade.elem.elems[1].elem.elems[1].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                        askForInput(
                            "str",
                            curLinearUpgradesList[curActualLinearUpgradeIndex],
                            "Title",
                            defaultValues["linearUpgradeTitles"]
                        )
                        return
                    if linearUpgrade.elem.elems[1].elem.elems[2].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                        askForInput(
                            "str",
                            curLinearUpgradesList[curActualLinearUpgradeIndex],
                            "RequiredUpgradeId",
                            defaultValues["nodeIds"],
                            True
                        )
                        return

                    for levelIndex,level in enumerate(linearUpgrade.elem.elems[1].elem.elems[4].elem.elems):
                        curActualLevelIndex,isNotLevelAddButton = divmod(levelIndex,2)
                        curLinearUpgradeLevelsList = curLinearUpgradesList[curActualLinearUpgradeIndex]["Levels"]
                        if not isNotLevelAddButton:
                            if level.boundingRect.collidepoint(rectifiedMousePos):
                                curLinearUpgradeLevelsList.insert(curActualLevelIndex,{
                                    "Value" : 0,
                                    "ResearchPointsCost" : None
                                })
                                fileChanged()
                                return
                        else:

                            if checkForMoveElem(
                                level.elem.elems[1].elem.elems,
                                curLinearUpgradeLevelsList,
                                curActualLevelIndex,
                                rectifiedMousePos
                            ):
                                return

                            if level.elem.elems[2].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                                askForInput("int",curLinearUpgradeLevelsList[curActualLevelIndex],"Value")
                                return
                            if level.elem.elems[3].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                                askForInput(
                                    "int",
                                    curLinearUpgradeLevelsList[curActualLevelIndex],
                                    "ResearchPointsCost",
                                    canBeNone = True
                                )
                                return
                            if level.elem.elems[4].boundingRect.collidepoint(rectifiedMousePos):
                                curLinearUpgradeLevelsList.pop(curActualLevelIndex)
                                fileChanged()
                                return

                    if linearUpgrade.elem.elems[2].boundingRect.collidepoint(rectifiedMousePos):
                        curLinearUpgradesList.pop(curActualLinearUpgradeIndex)
                        fileChanged()
                        return

        elif screen == "mechanics":

            for mechanicIndex,mechanic in enumerate(mechanicsScreenContentBox.elems):
                curActualMechanicIndex,isNotMechanicAddButton = divmod(mechanicIndex,2)
                if not isNotMechanicAddButton:
                    if mechanic.boundingRect.collidepoint(rectifiedMousePos):
                        curMechanicsList.insert(curActualMechanicIndex,{
                            "Id" : defaultValues["mechanicIds"][0],
                            "Title" : defaultValues["mechanicTitles"][0],
                            "Description" : defaultValues["mechanicDescriptions"][0],
                            "IconId" : defaultValues["mechanicIcons"][0]
                        })
                        fileChanged()
                        return
                else:

                    if checkForMoveElem(
                        mechanic.elem.elems[0].elem.elems,
                        curMechanicsList,
                        curActualMechanicIndex,
                        rectifiedMousePos
                    ):
                        return

                    for i,(key,presets) in enumerate([
                        ("Id",defaultValues["mechanicIds"]),
                        ("Title",defaultValues["mechanicTitles"]),
                        ("Description",defaultValues["mechanicDescriptions"]),
                        ("IconId",defaultValues["mechanicIcons"])
                    ]):
                        if mechanic.elem.elems[1].elem.elems[i].elem.elems[1].boundingRect.collidepoint(rectifiedMousePos):
                            askForInput("str",curMechanicsList[curActualMechanicIndex],key,presets)
                            return

                    if mechanic.elem.elems[2].boundingRect.collidepoint(rectifiedMousePos):
                        curMechanicsList.pop(curActualMechanicIndex)
                        fileChanged()
                        return

        elif screen == "valueInput":
            if curValueInputInfos["presets"] is not None:
                for i,rect in enumerate(curPresetRects):
                    if rect.collidepoint(rectifiedMousePos):
                        curValueInputInfos["curInputText"] = curValueInputKeptPresets[i]
                        return
            if valueInputNoneClickedCheck():
                return

    with open(DEFAULT_VALUES_PATH,encoding="utf-8") as f:
        defaultValues = json.load(f)

    if SET_DPI_AWARE:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()

    win = pygame.display.set_mode((700,700),pygame.RESIZABLE)
    winWidth, winHeight = win.get_size()
    clock = pygame.time.Clock()
    pygame.key.set_repeat(*KEY_PRESS_REPEAT)
    pygame.scrap.init()

    screen = "inputFile"
    curProgression = None
    curProgressionFilePath = None
    curInputFileError = None
    autoSave = True
    renderedShapesCache:dict[tuple[str,int,shapeViewer.EXTERNAL_COLOR_SKINS_ANNOTATION],pygame.Surface] = {}
    renderedTextsCache:dict[tuple[str,bool],pygame.Surface] = {}
    shapesColorSkin = shapeViewer.EXTERNAL_COLOR_SKINS[0]
    hScrollOffset = 0
    vScrollOffset = 0
    curValueInputInfos = None
    checkScrollOffsets = False
    curBPCurrencyShapesList = []
    curLevelsList = []
    curSideQuestGroupsList = []
    curSideUpgradesList = []
    curLinearUpgradesList = []
    curMechanicsList = []
    createCurContentBoxes = True
    run = True

    if FILE_PATH_OVERRIDE is not None:
        decodeInputtedFilePath(FILE_PATH_OVERRIDE)

    while run:

        clock.tick(FPS)
        pygame.display.set_caption(f"Progression file editor | {clock.get_fps():.0f} fps")

        keysPressed = pygame.key.get_pressed()
        mousePos = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.DROPFILE:
                decodeInputtedFilePath(event.file)

            elif event.type == pygame.KEYDOWN:
                if (screen != "inputFile") and (event.key == SAVE_KEY) and any(keysPressed[k] for k in SAVE_KEY_MOD):
                    saveChanges(False)
                if curValueInputInfos is not None:
                    if event.key == pygame.K_BACKSPACE:
                        if curValueInputInfos["curInputText"] is None:
                            curValueInputInfos["curInputText"] = ""
                        else:
                            curValueInputInfos["curInputText"] = curValueInputInfos["curInputText"][:-1]
                        if (curValueInputInfos["type"] == "int") and (curValueInputInfos["curInputText"] in ("","-")):
                            curValueInputInfos["curInputText"] = "0"
                    elif (event.key == PASTE_KEY) and any(keysPressed[k] for k in PASTE_KEY_MOD):
                        clipboardValue = pygame.scrap.get(pygame.SCRAP_TEXT)
                        if clipboardValue is not None:
                            clipboardValue = clipboardValue.replace(b"\x00",b"")
                            try:
                                clipboardValue = clipboardValue.decode()
                            except Exception as e:
                                logMsg(f"Couldn't paste {clipboardValue} : {e}")
                            else:
                                addValueInputText(clipboardValue)
                    elif event.key in (pygame.K_RETURN,pygame.K_KP_ENTER):
                        confirmValueInputChanges()

            elif event.type == pygame.MOUSEWHEEL:
                if (screen == "valueInput") and (curValueInputInfos["presets"] is None):
                    if curValueInputInfos["type"] == "int":
                        if curValueInputInfos["curInputText"] is None:
                            curValueInputInfos["curInputText"] = "0"
                        else:
                            curValueInt = int(curValueInputInfos["curInputText"])
                            curValueInt += event.y
                            if abs(curValueInt) <= STR_MAX_INT_DIGITS:
                                curValueInputInfos["curInputText"] = str(curValueInt)
                elif screen != "inputFile":
                    if any(keysPressed[k] for k in SCROLL_KEY_MOD):
                        hScrollOffset += event.y * SCROLL_SPEED
                    else:
                        vScrollOffset += event.y * SCROLL_SPEED
                    getValidScrollOffsets()

            elif event.type == pygame.WINDOWRESIZED:
                if screen != "inputFile":
                    getValidScrollOffsets()

            elif (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1):

                handleClickEvent(event.pos)

            elif event.type == pygame.TEXTINPUT:
                if (
                    (curValueInputInfos is not None)
                    and (
                        not (
                            ((event.text == SAVE_KEY_STR) and any(keysPressed[k] for k in SAVE_KEY_MOD))
                            or ((event.text == PASTE_KEY_STR) and any(keysPressed[k] for k in PASTE_KEY_MOD))
                        )
                    )
                ):
                    addValueInputText(event.text)

        winWidth, winHeight = win.get_size()

        win.fill(INPUT_FILE_BG_COLOR if screen == "inputFile" else BG_COLOR)

        curCullInfo = (getScrollSurfBlitPos(),(winWidth,winHeight))
        if DEBUG:
            curCullInfo = (
                (
                    curCullInfo[0][0]-200,
                    curCullInfo[0][1]-200
                ),
                (
                    curCullInfo[1][0]-400,
                    curCullInfo[1][1]-400
                )
            )
            debugCulled = 0
            debugNotCulled = 0

        if screen != "inputFile":

            if (curValueInputInfos is None) or (not curValueInputInfos["valueInputInTopBar"]):

                curTopBarContentBox = ContentBox([
                    ContentBoxElem(
                        (BIG_FONT_UNDERLINED if screen == id else BIG_FONT).render(name,1,DEFAULT_TEXT_COLOR),
                        True,
                        hMargin = DEFAULT_MARGIN,
                        vMargin = DEFAULT_MARGIN
                    ) for id,name in SCREEN_IDS_AND_NAMES
                ],"h")

                curTopBarContentBox.calculateBoundingRects()

                curTopBarTempSurf = pygame.Surface((
                    curTopBarContentBox.width,
                    curTopBarContentBox.height
                ))
                curTopBarTempSurf.fill(FIXED_UI_BG_COLOR)
                curTopBarSurf = pygame.Surface((
                    winWidth,
                    curTopBarTempSurf.get_height()
                ))
                curTopBarSurf.fill(FIXED_UI_BG_COLOR)

                curTopBarOffset = (curTopBarSurf.get_width()/2) - (curTopBarTempSurf.get_width()/2)
                curTopBarContentBox.render(curTopBarTempSurf,mousePos[0]-curTopBarOffset,mousePos[1],True)
                curTopBarSurf.blit(curTopBarTempSurf,(curTopBarOffset,0))
                curTopBarRect = pygame.Rect(0,0,*curTopBarSurf.get_size())


            curBottomBarHeights = []
            renderBottomBarMiddleButton = screen == "valueInput"

            curBottomBarLeftContentBox = ContentBox([
                ContentBoxElem(
                    defaultRenderText("Autosave : "+("Yes" if autoSave else "No")),
                    True,
                    hMargin = DEFAULT_MARGIN,
                    vMargin = DEFAULT_MARGIN
                )
            ],"h")
            curBottomBarLeftContentBox.calculateBoundingRects()
            curBottomBarLeftTempSurf = pygame.Surface((
                curBottomBarLeftContentBox.width,
                curBottomBarLeftContentBox.height
            ))
            curBottomBarLeftTempSurf.fill(FIXED_UI_BG_COLOR)
            curBottomBarHeights.append(curBottomBarLeftTempSurf.get_height())

            if renderBottomBarMiddleButton:
                curBottomBarMiddleContentBox = ContentBox([
                    ContentBoxElem(BIG_FONT.render("Done",1,DEFAULT_TEXT_COLOR),True,hMargin=DEFAULT_MARGIN,vMargin=DEFAULT_MARGIN)
                ],"h")
                curBottomBarMiddleContentBox.calculateBoundingRects()
                curBottomBarMiddleTempSurf = pygame.Surface((
                    curBottomBarMiddleContentBox.width,
                    curBottomBarMiddleContentBox.height
                ))
                curBottomBarMiddleTempSurf.fill(FIXED_UI_BG_COLOR)
                curBottomBarHeights.append(curBottomBarMiddleTempSurf.get_height())

            curBottomBarRightContentBox = ContentBox([
                ContentBoxElem(
                    defaultRenderText(f"Shape colors : {shapesColorSkin}"),
                    True,
                    hMargin = DEFAULT_MARGIN,
                    vMargin = DEFAULT_MARGIN
                )
            ],"h")
            curBottomBarRightContentBox.calculateBoundingRects()
            curBottomBarRightTempSurf = pygame.Surface((
                curBottomBarRightContentBox.width,
                curBottomBarRightContentBox.height
            ))
            curBottomBarRightTempSurf.fill(FIXED_UI_BG_COLOR)
            curBottomBarHeights.append(curBottomBarRightTempSurf.get_height())

            curBottomBarSurf = pygame.Surface((
                winWidth,
                max(curBottomBarHeights)
            ))
            curBottomBarSurf.fill(FIXED_UI_BG_COLOR)
            curBottomBarY = winHeight - curBottomBarSurf.get_height()

            curBottomBarLeftOffset = 0
            curBottomBarLeftContentBox.render(
                curBottomBarLeftTempSurf,
                mousePos[0]-curBottomBarLeftOffset,
                mousePos[1]-curBottomBarY,
                True
            )
            curBottomBarSurf.blit(curBottomBarLeftTempSurf,(
                curBottomBarLeftOffset,
                (curBottomBarSurf.get_height()/2) - (curBottomBarLeftTempSurf.get_height()/2)
            ))

            if renderBottomBarMiddleButton:
                curBottomBarMiddleOffset = (curBottomBarSurf.get_width()/2) - (curBottomBarMiddleTempSurf.get_width()/2)
                curBottomBarMiddleContentBox.render(
                    curBottomBarMiddleTempSurf,
                    mousePos[0]-curBottomBarMiddleOffset,
                    mousePos[1]-curBottomBarY,
                    True
                )
                curBottomBarSurf.blit(curBottomBarMiddleTempSurf,(
                    curBottomBarMiddleOffset,
                    (curBottomBarSurf.get_height()/2) - (curBottomBarMiddleTempSurf.get_height()/2)
                ))

            curBottomBarRightOffset = curBottomBarSurf.get_width() - curBottomBarRightTempSurf.get_width()
            curBottomBarRightContentBox.render(
                curBottomBarRightTempSurf,
                mousePos[0]-curBottomBarRightOffset,
                mousePos[1]-curBottomBarY,
                True
            )
            curBottomBarSurf.blit(curBottomBarRightTempSurf,(
                curBottomBarRightOffset,
                (curBottomBarSurf.get_height()/2) - (curBottomBarRightTempSurf.get_height()/2)
            ))

            curBottomBarRect = pygame.Rect(0,curBottomBarY,*curBottomBarSurf.get_size())

            isMouseOverFixedUI = curTopBarRect.collidepoint(mousePos) or curBottomBarRect.collidepoint(mousePos)

        if screen == "inputFile":

            textLines = ["Drag and drop a file in this window at any time to open it"]
            if curInputFileError is not None:
                textLines.append(f"Error while decoding file : {curInputFileError}")
                if curInputFileError.__cause__ is not None:
                    textLines.append(f"{curInputFileError.__cause__.__class__.__name__}: {curInputFileError.__cause__}")
            textLinesRendered = [BIG_FONT.render(line,1,DEFAULT_TEXT_COLOR) for line in textLines]
            totalHeight = sum(line.get_height() for line in textLinesRendered)
            curY = (winHeight/2) - (totalHeight/2)
            for line in textLinesRendered:
                win.blit(line,((winWidth/2)-(line.get_width()/2),curY))
                curY += line.get_height()

        elif screen == "config":

            speedsToLinearUpgradeMappings:list[tuple[str,str]] = [
                ("BeltSpeed","Belt speed"),
                ("CutterSpeed","Cutter speed"),
                ("StackerSpeed","Stacker speed"),
                ("PainterSpeed","Painter speed")
            ]

            if createCurContentBoxes:

                bpCurrencyShapesContentBoxes = []
                for i,shape in enumerate(curBPCurrencyShapesList):
                    bpCurrencyShapesContentBoxes.append(ContentBoxElem(ContentBox([
                        ContentBoxElem(ContentBox(
                            getMoveArrowsList(curBPCurrencyShapesList,i,"h")
                        ,"h")),
                        ContentBoxElem(ContentBox([
                            ContentBoxElem(renderShape(shape["Shape"]),True),
                            ContentBoxElem(defaultRenderText(str(shape["Amount"])),True)
                        ],"h")),
                        ContentBoxElem(defaultRenderText(shape["RequiredUpgradeId"]),True),
                        ContentBoxElem(**DEFAULT_REMOVE_BUTTON_KWARGS)
                    ],"v"),bgColor=ELEM_COLOR))
                bpCurrencyShapesContentBoxes = addAddButtons(bpCurrencyShapesContentBoxes,"h")

                configScreenContentBoxElemStyle = {"hAlignment":"l","hMargin":DEFAULT_MAIN_H_MARGIN,"vMargin":DEFAULT_MARGIN}

                configScreenContentBox = ContentBox([
                    ContentBoxElem(ContentBox([
                        ContentBoxElem(defaultRenderText("Game version :",True)),
                        ContentBoxElem(defaultRenderText(str(curProgression["GameVersion"])),True)
                    ],"h"),**configScreenContentBoxElemStyle),
                    ContentBoxElem(ContentBox([
                        ContentBoxElem(defaultRenderText("Unique Id :",True)),
                        ContentBoxElem(defaultRenderText(curProgression["UniqueId"]),True)
                    ],"h"),**configScreenContentBoxElemStyle),
                    ContentBoxElem(ContentBox([
                        ContentBoxElem(defaultRenderText("Game mode :",True)),
                        ContentBoxElem(defaultRenderText(curProgression["GameMode"]),True)
                    ],"h"),**configScreenContentBoxElemStyle),
                    ContentBoxElem(ContentBox([
                        ContentBoxElem(defaultRenderText("Base chunk limit multiplier :",True)),
                        ContentBoxElem(defaultRenderText(str(curProgression["Config"]["BaseChunkLimitMultiplier"])),True)
                    ],"h"),**configScreenContentBoxElemStyle),
                    ContentBoxElem(
                        defaultRenderText("Layer mechanics :",True),
                        **configScreenContentBoxElemStyle
                    ),
                    ContentBoxElem(ContentBox(
                        getDefaultEditableListContentBoxes(curProgression["Config"]["LayerMechanicIds"])
                    ,"v"),**configScreenContentBoxElemStyle),
                ]+[
                    ContentBoxElem(ContentBox([
                        ContentBoxElem(defaultRenderText(f"{text} mechanic :",True)),
                        ContentBoxElem(defaultRenderText(curProgression["Config"][id]),True)
                    ],"h"),**configScreenContentBoxElemStyle) for id,text in [
                        ("BlueprintsMechanicId","Blueprints"),
                        ("RailsMechanicId","Rails"),
                        ("IslandManagementMechanicId","Island management")
                    ]
                ]+[
                    ContentBoxElem(
                        defaultRenderText("Blueprint currency shapes :",True),
                        **configScreenContentBoxElemStyle
                    ),
                    ContentBoxElem(ContentBox(
                        bpCurrencyShapesContentBoxes
                    ,"h"),**configScreenContentBoxElemStyle)
                ]+[
                    ContentBoxElem(ContentBox([
                        ContentBoxElem(defaultRenderText(f"{text} upgrade :",True)),
                        ContentBoxElem(defaultRenderText(curProgression["Config"][id]),True)
                    ],"h"),**configScreenContentBoxElemStyle) for id,text in [
                        ("BlueprintDiscountUpgradeId","Blueprint discount"),
                        ("HubInputSizeUpgradeId","Hub input size")
                    ]
                ]+[
                    ContentBoxElem(ContentBox([
                        ContentBoxElem(defaultRenderText(f"{text} upgrade :",True)),
                        ContentBoxElem(defaultRenderText(curProgression["Config"]["SpeedsToLinearUpgradeMappings"][id]),True)
                    ],"h"),**configScreenContentBoxElemStyle) for id,text in speedsToLinearUpgradeMappings
                ]+[
                    ContentBoxElem(ContentBox([
                        ContentBoxElem(defaultRenderText(f"{text} :",True)),
                        ContentBoxElem(defaultRenderText(curProgression["Config"][id]),True)
                    ],"h"),**configScreenContentBoxElemStyle) for id,text in [
                        ("ShapesConfigurationId","Shapes configuration"),
                        ("ColorSchemeConfigurationId","Color scheme"),
                        ("IntroductionWikiEntryId","Introduction wiki entry")
                    ]
                ],"v")

                configScreenContentBox.calculateBoundingRects()

                curScrollableSurf = pygame.Surface((
                    configScreenContentBox.width,
                    configScreenContentBox.height
                ))

                createCurContentBoxes = False

            curScrollableSurf.fill(BG_COLOR)
            configScreenContentBox.render(curScrollableSurf,*getRectifiedMousePos(*mousePos),cullInfo=curCullInfo)

        elif screen == "levels":

            if createCurContentBoxes:

                levelsContentBoxes = []
                for levelIndex,level in enumerate(curLevelsList):

                    linesContentBoxes = []
                    for lineIndex,line in enumerate(level["Lines"]):

                        lineShapesContentBoxes = []
                        for shapeIndex,shape in enumerate(line["Shapes"]):
                            lineShapesContentBoxes.append(ContentBoxElem(ContentBox([
                                ContentBoxElem(ContentBox(
                                    getMoveArrowsList(line["Shapes"],shapeIndex,"h")
                                ,"h")),
                                ContentBoxElem(ContentBox([
                                    ContentBoxElem(renderShape(shape["Shape"]),True),
                                    ContentBoxElem(defaultRenderText(str(shape["Amount"])),True)
                                ],"h")),
                                ContentBoxElem(**DEFAULT_REMOVE_BUTTON_KWARGS)
                            ],"v"),bgColor=ELEM_ON_ELEM_ON_ELEM_COLOR))

                        lineShapesContentBoxes = addAddButtons(lineShapesContentBoxes,"h")

                        linesContentBoxes.append(ContentBoxElem(ContentBox([
                            ContentBoxElem(ContentBox(
                                getMoveArrowsList(level["Lines"],lineIndex,"v")
                            ,"v")),
                            ContentBoxElem(ContentBox(
                                lineShapesContentBoxes
                            ,"h")),
                            ContentBoxElem(**DEFAULT_REMOVE_BUTTON_KWARGS)
                        ],"h"),bgColor=ELEM_ON_ELEM_COLOR))

                    linesContentBoxes = addAddButtons(linesContentBoxes,"v")

                    unlocksContentBoxes = []
                    for unlockId, unlockName in [
                        ("UnlockBuildingVariants","buidings"),
                        ("UnlockLayouts","islands"),
                        ("UnlockWikiEntries","wiki entries"),
                        ("UnlockMechanics","mechanics")
                    ]:
                        unlocksContentBoxes.append(
                            ContentBoxElem(defaultRenderText(f"Reward {unlockName} :",True))
                        )
                        unlocksContentBoxes.append(ContentBoxElem(ContentBox(
                            getDefaultEditableListContentBoxes(level[unlockId])
                        ,"v")))

                    levelsContentBoxes.append(ContentBoxElem(ContentBox([
                        ContentBoxElem(defaultRenderText(f"Milestone {levelIndex}",True)),
                        ContentBoxElem(ContentBox(
                            getMoveArrowsList(curLevelsList,levelIndex,"h")
                        ,"h")),
                        ContentBoxElem(ContentBox([
                            ContentBoxElem(defaultRenderText("Id :",True)),
                            ContentBoxElem(defaultRenderText(level["Id"]),True)
                        ],"h"),hAlignment="l"),
                        ContentBoxElem(ContentBox([
                            ContentBoxElem(defaultRenderText("Video :",True)),
                            ContentBoxElem(renderCanBeNoneText(defaultRenderText,level["VideoId"]),True)
                        ],"h"),hAlignment="l"),
                        ContentBoxElem(ContentBox([
                            ContentBoxElem(defaultRenderText("Image :",True)),
                            ContentBoxElem(defaultRenderText(level["PreviewImageId"]),True)
                        ],"h"),hAlignment="l"),
                        ContentBoxElem(ContentBox([
                            ContentBoxElem(defaultRenderText("Title :",True)),
                            ContentBoxElem(defaultRenderText(level["Title"]),True)
                        ],"h"),hAlignment="l"),
                        ContentBoxElem(ContentBox([
                            ContentBoxElem(defaultRenderText("Description :",True)),
                            ContentBoxElem(defaultRenderText(level["Description"]),True)
                        ],"h"),hAlignment="l"),
                        ContentBoxElem(defaultRenderText("Shape lines :",True),hAlignment="l"),
                        ContentBoxElem(ContentBox(
                            linesContentBoxes
                        ,"v"),hAlignment="l")
                    ]+
                        unlocksContentBoxes
                    +[
                        ContentBoxElem(ContentBox([
                            ContentBoxElem(defaultRenderText(f"Reward {rewardName} :",True)),
                            ContentBoxElem(defaultRenderText(
                                f"{level[rewardId]} ({getMultipliedChunkLimitReward(level[rewardId])})"
                                if rewardId == "RewardChunkLimit" else
                                str(level[rewardId])
                            ),True)
                        ],"h"),hAlignment="l") for rewardId,rewardName in [
                            ("RewardChunkLimit","chunk limit"),
                            ("RewardResearchPoints","research points"),
                            ("RewardBlueprintCurrency","blueprint currency")
                        ]
                    ]+[
                        ContentBoxElem(**DEFAULT_REMOVE_BUTTON_KWARGS)
                    ]
                    ,"v"),bgColor=ELEM_COLOR,vAlignment="t"))

                levelsContentBoxes = addAddButtons(levelsContentBoxes,"h")

                levelsScreenContentBox = ContentBox(levelsContentBoxes,"h")
                levelsScreenContentBox.calculateBoundingRects(DEFAULT_MAIN_H_MARGIN,DEFAULT_MARGIN)

                curScrollableSurf = pygame.Surface((
                    levelsScreenContentBox.width + (2*DEFAULT_MAIN_H_MARGIN),
                    levelsScreenContentBox.height + (2*DEFAULT_MARGIN)
                ))

                createCurContentBoxes = False

            curScrollableSurf.fill(BG_COLOR)
            levelsScreenContentBox.render(curScrollableSurf,*getRectifiedMousePos(*mousePos),cullInfo=curCullInfo)

        elif screen == "sideUpgrades":

            if createCurContentBoxes:

                sideUpgradesContentBoxes = []
                for sideUpgradeIndex,sideUpgrade in enumerate(curSideUpgradesList):

                    unlocksContentBoxes = []
                    for unlockId, unlockName in [
                        ("UnlockBuildingVariants","buidings"),
                        ("UnlockLayouts","islands"),
                        ("UnlockWikiEntries","wiki entries"),
                        ("UnlockMechanics","mechanics")
                    ]:
                        unlocksContentBoxes.append(
                            ContentBoxElem(defaultRenderText(f"Reward {unlockName} :",True))
                        )
                        unlocksContentBoxes.append(ContentBoxElem(ContentBox(
                            getDefaultEditableListContentBoxes(sideUpgrade[unlockId])
                        ,"v")))

                    sideUpgradesContentBoxes.append(ContentBoxElem(ContentBox([
                        ContentBoxElem(ContentBox(
                            getMoveArrowsList(curSideUpgradesList,sideUpgradeIndex,"v")
                        ,"v")),
                        ContentBoxElem(ContentBox([
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Id :",True)),
                                ContentBoxElem(defaultRenderText(sideUpgrade["Id"]),True)
                            ],"h"),hAlignment="l"),
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Video :",True)),
                                ContentBoxElem(renderCanBeNoneText(defaultRenderText,sideUpgrade["VideoId"]),True)
                            ],"h"),hAlignment="l"),
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Image :",True)),
                                ContentBoxElem(defaultRenderText(sideUpgrade["PreviewImageId"]),True)
                            ],"h"),hAlignment="l"),
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Title :",True)),
                                ContentBoxElem(defaultRenderText(sideUpgrade["Title"]),True)
                            ],"h"),hAlignment="l"),
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Description :",True)),
                                ContentBoxElem(defaultRenderText(sideUpgrade["Description"]),True)
                            ],"h"),hAlignment="l"),
                        ],"v"),vAlignment="t"),
                        ContentBoxElem(defaultRenderText(""),bgColor=ELEM_ON_ELEM_COLOR),
                        ContentBoxElem(ContentBox([
                            ContentBoxElem(defaultRenderText("Required upgrades :",True)),
                            ContentBoxElem(ContentBox(
                                getDefaultEditableListContentBoxes(sideUpgrade["RequiredUpgradeIds"])
                            ,"v")),
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Research points cost :",True)),
                                ContentBoxElem(defaultRenderText(str(sideUpgrade["ResearchPointsCost"])),True)
                            ],"h"),hAlignment="l")
                        ],"v"),vAlignment="t"),
                        ContentBoxElem(defaultRenderText(""),bgColor=ELEM_ON_ELEM_COLOR),
                        ContentBoxElem(ContentBox(
                            unlocksContentBoxes
                        ,"v"),vAlignment="t"),
                        ContentBoxElem(defaultRenderText(""),bgColor=ELEM_ON_ELEM_COLOR),
                        ContentBoxElem(ContentBox([
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText(f"Reward {rewardName} :",True)),
                                ContentBoxElem(defaultRenderText(
                                    f"{sideUpgrade[rewardId]} ({getMultipliedChunkLimitReward(sideUpgrade[rewardId])})"
                                    if rewardId == "RewardChunkLimit" else
                                    str(sideUpgrade[rewardId])
                                ),True)
                            ],"h"),hAlignment="l") for rewardId,rewardName in [
                                ("RewardChunkLimit","chunk limit"),
                                ("RewardResearchPoints","research points"),
                                ("RewardBlueprintCurrency","blueprint currency")
                            ]
                        ],"v"),vAlignment="t"),
                        ContentBoxElem(**DEFAULT_REMOVE_BUTTON_KWARGS)
                    ],"h"),bgColor=ELEM_COLOR,hAlignment="l"))

                sideUpgradesContentBoxes = addAddButtons(sideUpgradesContentBoxes,"v")

                sideUpgradesScreenContentBox = ContentBox(sideUpgradesContentBoxes,"v")
                sideUpgradesScreenContentBox.calculateBoundingRects(DEFAULT_MAIN_H_MARGIN,DEFAULT_MARGIN)

                curScrollableSurf = pygame.Surface((
                    sideUpgradesScreenContentBox.width + (2*DEFAULT_MAIN_H_MARGIN),
                    sideUpgradesScreenContentBox.height + (2*DEFAULT_MARGIN)
                ))

                createCurContentBoxes = False

            curScrollableSurf.fill(BG_COLOR)
            sideUpgradesScreenContentBox.render(curScrollableSurf,*getRectifiedMousePos(*mousePos),cullInfo=curCullInfo)

        elif screen == "sideQuests":

            if createCurContentBoxes:

                sideQuestGroupsContentBoxes = []
                for sideQuestGroupIndex,sideQuestGroup in enumerate(curSideQuestGroupsList):

                    sideQuestsContentBoxes = []
                    for sideQuestIndex,sideQuest in enumerate(sideQuestGroup["SideQuests"]):

                        shapeCostsContentBoxes = []
                        for shapeCostIndex,shapeCost in enumerate(sideQuest["Costs"]):

                            shapeCostsContentBoxes.append(ContentBoxElem(ContentBox([
                                ContentBoxElem(ContentBox(
                                    getMoveArrowsList(sideQuest["Costs"],shapeCostIndex,"h")
                                ,"h")),
                                ContentBoxElem(ContentBox([
                                    ContentBoxElem(renderShape(shapeCost["Shape"]),True),
                                    ContentBoxElem(defaultRenderText(str(shapeCost["Amount"])),True)
                                ],"h")),
                                ContentBoxElem(**DEFAULT_REMOVE_BUTTON_KWARGS)
                            ],"v"),bgColor=ELEM_ON_ELEM_ON_ELEM_COLOR))

                        shapeCostsContentBoxes = addAddButtons(shapeCostsContentBoxes,"h")

                        unlocksContentBoxes = []
                        for unlockId, unlockName in [
                            ("UnlockBuildingVariants","buidings"),
                            ("UnlockLayouts","islands"),
                            ("UnlockWikiEntries","wiki entries"),
                            ("UnlockMechanics","mechanics")
                        ]:
                            unlocksContentBoxes.append(
                                ContentBoxElem(defaultRenderText(f"Reward {unlockName} :",True))
                            )
                            unlocksContentBoxes.append(ContentBoxElem(ContentBox(
                                getDefaultEditableListContentBoxes(sideQuest[unlockId])
                            ,"v")))

                        sideQuestsContentBoxes.append(ContentBoxElem(ContentBox([
                            ContentBoxElem(ContentBox(
                                getMoveArrowsList(sideQuestGroup["SideQuests"],sideQuestIndex,"h")
                            ,"h")),
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(ContentBox([
                                    ContentBoxElem(ContentBox([
                                        ContentBoxElem(defaultRenderText("Id :",True)),
                                        ContentBoxElem(defaultRenderText(sideQuest["Id"]),True)
                                    ],"h")),
                                    ContentBoxElem(defaultRenderText("Costs :",True)),
                                    ContentBoxElem(ContentBox(
                                        shapeCostsContentBoxes
                                    ,"h"))
                                ],"v"),vAlignment="t"),
                                ContentBoxElem(defaultRenderText(""),bgColor=ELEM_ON_ELEM_ON_ELEM_COLOR),
                                ContentBoxElem(ContentBox(
                                    unlocksContentBoxes
                                ,"v"),vAlignment="t"),
                                ContentBoxElem(defaultRenderText(""),bgColor=ELEM_ON_ELEM_ON_ELEM_COLOR),
                                ContentBoxElem(ContentBox([
                                    ContentBoxElem(ContentBox([
                                        ContentBoxElem(defaultRenderText(f"Reward {rewardName} :",True)),
                                        ContentBoxElem(defaultRenderText(
                                            f"{sideQuest[rewardId]} ({getMultipliedChunkLimitReward(sideQuest[rewardId])})"
                                            if rewardId == "RewardChunkLimit" else
                                            str(sideQuest[rewardId])
                                        ),True)
                                    ],"h"),hAlignment="l") for rewardId,rewardName in [
                                        ("RewardChunkLimit","chunk limit"),
                                        ("RewardResearchPoints","research points"),
                                        ("RewardBlueprintCurrency","blueprint currency")
                                    ]
                                ],"v"),vAlignment="t")
                            ],"h")),
                            ContentBoxElem(**DEFAULT_REMOVE_BUTTON_KWARGS)
                        ],"v"),bgColor=ELEM_ON_ELEM_COLOR))

                    sideQuestsContentBoxes = addAddButtons(sideQuestsContentBoxes,"h")

                    sideQuestGroupsContentBoxes.append(ContentBoxElem(ContentBox([
                        ContentBoxElem(ContentBox(
                            getMoveArrowsList(curSideQuestGroupsList,sideQuestGroupIndex,"v")
                        ,"v")),
                        ContentBoxElem(ContentBox([
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Title :",True)),
                                ContentBoxElem(defaultRenderText(sideQuestGroup["Title"]),True)
                            ],"h"),hAlignment="l"),
                            ContentBoxElem(defaultRenderText("Required upgrades :",True),hAlignment="l"),
                            ContentBoxElem(ContentBox(
                                getDefaultEditableListContentBoxes(sideQuestGroup["RequiredUpgradeIds"])
                            ,"v"),hAlignment="l"),
                            ContentBoxElem(defaultRenderText("Side quests :",True),hAlignment="l"),
                            ContentBoxElem(ContentBox(
                                sideQuestsContentBoxes
                            ,"h"),hAlignment="l")
                        ],"v")),
                        ContentBoxElem(**DEFAULT_REMOVE_BUTTON_KWARGS)
                    ],"h"),hAlignment="l",bgColor=ELEM_COLOR))

                sideQuestGroupsContentBoxes = addAddButtons(sideQuestGroupsContentBoxes,"v")

                sideQuestsScreenContentBox = ContentBox(sideQuestGroupsContentBoxes,"v")
                sideQuestsScreenContentBox.calculateBoundingRects(DEFAULT_MAIN_H_MARGIN,DEFAULT_MARGIN)

                curScrollableSurf = pygame.Surface((
                    sideQuestsScreenContentBox.width + (2*DEFAULT_MAIN_H_MARGIN),
                    sideQuestsScreenContentBox.height + (2*DEFAULT_MARGIN)
                ))

                createCurContentBoxes = False

            curScrollableSurf.fill(BG_COLOR)
            sideQuestsScreenContentBox.render(curScrollableSurf,*getRectifiedMousePos(*mousePos),cullInfo=curCullInfo)

        elif screen == "linearUpgrades":

            if createCurContentBoxes:

                linearUpgradesContentBoxes = []
                for linearUpgradeIndex,linearUpgrade in enumerate(curLinearUpgradesList):

                    levelsContentBoxes = []
                    for levelIndex,level in enumerate(linearUpgrade["Levels"]):

                        levelsContentBoxes.append(ContentBoxElem(ContentBox([
                            ContentBoxElem(defaultRenderText(f"Level {levelIndex+1}",True)),
                            ContentBoxElem(ContentBox(
                                getMoveArrowsList(linearUpgrade["Levels"],levelIndex,"h")
                            ,"h")),
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Value :",True)),
                                ContentBoxElem(defaultRenderText(str(level["Value"])),True)
                            ],"h"),hAlignment="l"),
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Research points cost :",True)),
                                ContentBoxElem(renderCanBeNoneText(lambda t: defaultRenderText(str(t)),level["ResearchPointsCost"]),True)
                            ],"h"),hAlignment="l"),
                            ContentBoxElem(**DEFAULT_REMOVE_BUTTON_KWARGS)
                        ],"v"),bgColor=ELEM_ON_ELEM_COLOR))

                    levelsContentBoxes = addAddButtons(levelsContentBoxes,"h")

                    linearUpgradesContentBoxes.append(ContentBoxElem(ContentBox([
                        ContentBoxElem(ContentBox(
                            getMoveArrowsList(curLinearUpgradesList,linearUpgradeIndex,"v")
                        ,"v")),
                        ContentBoxElem(ContentBox([
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Id :",True)),
                                ContentBoxElem(defaultRenderText(linearUpgrade["Id"]),True)
                            ],"h"),hAlignment="l"),
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Title :",True)),
                                ContentBoxElem(defaultRenderText(linearUpgrade["Title"]),True)
                            ],"h"),hAlignment="l"),
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Required upgrade :",True)),
                                ContentBoxElem(renderCanBeNoneText(defaultRenderText,linearUpgrade["RequiredUpgradeId"]),True)
                            ],"h"),hAlignment="l"),
                            ContentBoxElem(defaultRenderText("Levels :",True),hAlignment="l"),
                            ContentBoxElem(ContentBox(
                                levelsContentBoxes
                            ,"h"),hAlignment="l")
                        ],"v")),
                        ContentBoxElem(**DEFAULT_REMOVE_BUTTON_KWARGS)
                    ],"h"),hAlignment="l",bgColor=ELEM_COLOR))

                linearUpgradesContentBoxes = addAddButtons(linearUpgradesContentBoxes,"v")

                linearUpgradesScreenContentBox = ContentBox(linearUpgradesContentBoxes,"v")
                linearUpgradesScreenContentBox.calculateBoundingRects(DEFAULT_MAIN_H_MARGIN,DEFAULT_MARGIN)

                curScrollableSurf = pygame.Surface((
                    linearUpgradesScreenContentBox.width + (2*DEFAULT_MAIN_H_MARGIN),
                    linearUpgradesScreenContentBox.height + (2*DEFAULT_MARGIN)
                ))

                createCurContentBoxes = False

            curScrollableSurf.fill(BG_COLOR)
            linearUpgradesScreenContentBox.render(curScrollableSurf,*getRectifiedMousePos(*mousePos),cullInfo=curCullInfo)

        elif screen == "mechanics":

            if createCurContentBoxes:

                mechanicsContentBoxes = []
                for mechanicIndex,mechanic in enumerate(curMechanicsList):

                    mechanicsContentBoxes.append(ContentBoxElem(ContentBox([
                        ContentBoxElem(ContentBox(
                            getMoveArrowsList(curMechanicsList,mechanicIndex,"v")
                        ,"v")),
                        ContentBoxElem(ContentBox([
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Id :",True)),
                                ContentBoxElem(defaultRenderText(mechanic["Id"]),True)
                            ],"h"),hAlignment="l"),
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Title :",True)),
                                ContentBoxElem(defaultRenderText(mechanic["Title"]),True)
                            ],"h"),hAlignment="l"),
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Description :",True)),
                                ContentBoxElem(defaultRenderText(mechanic["Description"]),True)
                            ],"h"),hAlignment="l"),
                            ContentBoxElem(ContentBox([
                                ContentBoxElem(defaultRenderText("Icon :",True)),
                                ContentBoxElem(defaultRenderText(mechanic["IconId"]),True)
                            ],"h"),hAlignment="l")
                        ],"v")),
                        ContentBoxElem(**DEFAULT_REMOVE_BUTTON_KWARGS)
                    ],"h"),bgColor=ELEM_COLOR,hAlignment="l"))

                mechanicsContentBoxes = addAddButtons(mechanicsContentBoxes,"v")

                mechanicsScreenContentBox = ContentBox(mechanicsContentBoxes,"v")
                mechanicsScreenContentBox.calculateBoundingRects(DEFAULT_MAIN_H_MARGIN,DEFAULT_MARGIN)

                curScrollableSurf = pygame.Surface((
                    mechanicsScreenContentBox.width + (2*DEFAULT_MAIN_H_MARGIN),
                    mechanicsScreenContentBox.height + (2*DEFAULT_MARGIN)
                ))

                createCurContentBoxes = False

            curScrollableSurf.fill(BG_COLOR)
            mechanicsScreenContentBox.render(curScrollableSurf,*getRectifiedMousePos(*mousePos),cullInfo=curCullInfo)

        elif screen == "valueInput":

            headerTextSearch = "" if curValueInputInfos["presets"] is None else " or search"
            if curValueInputInfos["type"] == "str":
                curValueInputHeaderText = f"Enter{headerTextSearch} a value :"
            elif curValueInputInfos["type"] == "shape":
                curValueInputHeaderText = f"Enter{headerTextSearch} a shape code :"
            else:
                curValueInputHeaderText = f"Enter{headerTextSearch} a number :"
            curValueInputHeaderTextRendered = defaultRenderText(curValueInputHeaderText)

            if curValueInputInfos["canBeNone"]:
                curValueInputNoneContentBox = ContentBox([
                    ContentBoxElem(defaultRenderText("or")),
                    ContentBoxElem(NONE_TEXT,True)
                ],"h")
                curValueInputNoneContentBox.calculateBoundingRects()
                curValueInputNoneWidth = curValueInputNoneContentBox.width
                curValueInputNoneHeight = curValueInputNoneContentBox.height
            else:
                curValueInputNoneWidth = 0
                curValueInputNoneHeight = 0

            if curValueInputInfos["curInputText"] is None:
                curValueInputTextRendered = NONE_TEXT
            else:
                curValueInputTextRendered = DEFAULT_FONT.render(curValueInputInfos["curInputText"],1,DEFAULT_TEXT_COLOR)
            curValueInputTextHeight = curValueInputTextRendered.get_height() + (2*DEFAULT_PADDING)
            curValueInputTextWidth = curValueInputTextRendered.get_width() + (2*DEFAULT_PADDING)
            curValueInputHeaderAndTextAndNoneWidth = winWidth - (2*DEFAULT_MAIN_H_MARGIN)
            curValueInputTextSurf = pygame.Surface((
                (
                    curValueInputHeaderAndTextAndNoneWidth
                    - curValueInputHeaderTextRendered.get_width()
                    - curValueInputNoneWidth
                    - DEFAULT_MARGIN
                ),
                curValueInputTextHeight
            ))
            curValueInputTextSurf.fill(TEXT_INPUT_BG_COLOR)
            curValueInputTextSurf.blit(curValueInputTextRendered,(
                min(DEFAULT_PADDING,curValueInputTextSurf.get_width()-curValueInputTextWidth),
                DEFAULT_PADDING
            ))
            curValueInputHeaderAndTextAndNoneSurf = pygame.Surface((
                curValueInputHeaderAndTextAndNoneWidth,
                max(curValueInputHeaderTextRendered.get_height(),curValueInputTextHeight,curValueInputNoneHeight)
            ),pygame.SRCALPHA)
            curValueInputHeaderAndTextAndNoneSurf.blit(curValueInputHeaderTextRendered,(
                0,
                (curValueInputHeaderAndTextAndNoneSurf.get_height()/2) - (curValueInputHeaderTextRendered.get_height()/2)
            ))
            curValueInputHeaderAndTextAndNoneSurf.blit(curValueInputTextSurf,(
                curValueInputHeaderTextRendered.get_width() + DEFAULT_MARGIN,
                (curValueInputHeaderAndTextAndNoneSurf.get_height()/2) - (curValueInputTextSurf.get_height()/2)
            ))

            if curValueInputInfos["valueInputInTopBar"]:
                curValueInputX = DEFAULT_MAIN_H_MARGIN
                curValueInputY = DEFAULT_MARGIN
            else:
                curValueInputX = DEFAULT_MAIN_H_MARGIN
                curValueInputY = (
                    ((winHeight-curTopBarSurf.get_height()-curBottomBarSurf.get_height())/2)
                    - (curValueInputHeaderAndTextAndNoneSurf.get_height()/2)
                    + curTopBarSurf.get_height()
                )

            if curValueInputInfos["canBeNone"]:
                curValueInputNoneSurf = pygame.Surface((
                    curValueInputNoneWidth,
                    curValueInputNoneHeight
                ),pygame.SRCALPHA)
                curValueInputNoneXOffset = (
                    curValueInputHeaderTextRendered.get_width()
                    + DEFAULT_MARGIN
                    + curValueInputTextSurf.get_width()
                )
                curValueInputNoneYOffset = (
                    (curValueInputHeaderAndTextAndNoneSurf.get_height()/2)
                    - (curValueInputNoneHeight/2)
                )
                curValueInputNoneContentBox.render(
                    curValueInputNoneSurf,
                    mousePos[0] - curValueInputX - curValueInputNoneXOffset,
                    mousePos[1] - curValueInputY - curValueInputNoneYOffset,
                    True
                )
                curValueInputHeaderAndTextAndNoneSurf.blit(
                    curValueInputNoneSurf,
                    (curValueInputNoneXOffset,curValueInputNoneYOffset)
                )

            if curValueInputInfos["valueInputInTopBar"]:

                curTopBarSurf = pygame.Surface((
                    winWidth,
                    curValueInputHeaderAndTextAndNoneSurf.get_height() + (2*DEFAULT_MARGIN)
                ))
                curTopBarSurf.fill(FIXED_UI_BG_COLOR)
                curTopBarSurf.blit(
                    curValueInputHeaderAndTextAndNoneSurf,
                    (curValueInputX,curValueInputY)
                )

                curPresetRects:list[pygame.Rect] = []
                curScrollableSurf = pygame.Surface((0,0))

                if curValueInputInfos["presets"] is not None:

                    if curValueInputInfos["curInputText"] is None:
                        curValueInputKeptPresets = curValueInputInfos["presets"]
                    else:
                        curValueInputKeptPresets = [p for p in curValueInputInfos["presets"] if curValueInputInfos["curInputText"].lower() in p.lower()]
                    renderedPresets = [defaultRenderText(p) for p in curValueInputKeptPresets]

                    if renderedPresets != []:

                        curPresetHeight = max(p.get_height()+(2*DEFAULT_PADDING) for p in renderedPresets)
                        curX = DEFAULT_MAIN_H_MARGIN
                        curY = DEFAULT_MARGIN
                        for preset in renderedPresets:
                            curPresetWidth = preset.get_width() + (2*DEFAULT_PADDING)
                            if (curX+curPresetWidth) > (winWidth-DEFAULT_MAIN_H_MARGIN):
                                curX = DEFAULT_MAIN_H_MARGIN
                                curY += curPresetHeight + DEFAULT_MARGIN
                            curPresetRects.append(pygame.Rect(curX,curY,curPresetWidth,curPresetHeight))
                            curX += curPresetWidth + DEFAULT_MARGIN

                        curScrollableSurf = pygame.Surface((
                            max(r.right for r in curPresetRects),
                            max(r.bottom for r in curPresetRects) + DEFAULT_MARGIN
                        ))
                        curScrollableSurf.fill(BG_COLOR)

                        for preset,rect in zip(renderedPresets,curPresetRects):
                            pygame.draw.rect(
                                curScrollableSurf,
                                (
                                    HIGHLIGHTED_COLOR
                                    if (not isMouseOverFixedUI) and (rect.collidepoint(getRectifiedMousePos(*mousePos))) else
                                    ELEM_COLOR
                                ),
                                rect
                            )
                            curScrollableSurf.blit(preset,(rect.x+DEFAULT_PADDING,rect.y+DEFAULT_PADDING))

            else:

                win.blit(
                    curValueInputHeaderAndTextAndNoneSurf,
                    (curValueInputX,curValueInputY)
                )

                curValueInputLine2 = None
                if curValueInputInfos["line2Callable"] is not None:
                    curValueInputLine2 = curValueInputInfos["line2Callable"](curValueInputInfos["curInputText"])
                elif curValueInputInfos["type"] == "int":
                    curValueInputLine2 = defaultRenderText("Or use the scrollwheel")
                elif curValueInputInfos["type"] == "shape":
                    curValueInputLine2 = renderShape(curValueInputInfos["curInputText"],VALUE_INPUT_SHAPE_SIZE)
                if curValueInputLine2 is not None:
                    win.blit(curValueInputLine2,(
                        (winWidth/2) - (curValueInputLine2.get_width()/2),
                        curValueInputY + curValueInputHeaderAndTextAndNoneSurf.get_height() + DEFAULT_MARGIN
                    ))

        if checkScrollOffsets:
            getValidScrollOffsets()
            checkScrollOffsets = False

        if screen != "inputFile":
            if (curValueInputInfos is None) or (curValueInputInfos["valueInputInTopBar"]):
                win.blit(curScrollableSurf,getScrollSurfBlitPos())

            win.blit(curTopBarSurf,(0,0))
            win.blit(curBottomBarSurf,(0,curBottomBarY))

        if DEBUG:
            pygame.draw.rect(win,(255,0,0),pygame.Rect(200,200,winWidth-400,winHeight-400),1)
            win.blit(DEFAULT_FONT.render(f"{debugNotCulled},{debugCulled}",1,(255,255,255)),(0,0))

        pygame.display.update()

if __name__ == "__main__":
    main()