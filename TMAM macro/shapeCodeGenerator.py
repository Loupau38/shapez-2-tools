import globalInfos
import math

SHAPE_CONFIG_QUAD = globalInfos.SHAPE_CONFIG_QUAD
SHAPE_CONFIG_HEX = globalInfos.SHAPE_CONFIG_HEX
COLOR_SHAPES = {
    SHAPE_CONFIG_QUAD : ["C","R","S","W","c"],
    SHAPE_CONFIG_HEX : ["H","F","G","c"]
}
NO_COLOR_SHAPES = {
    SHAPE_CONFIG_QUAD : ["P"],
    SHAPE_CONFIG_HEX : ["P"]
}
COLORS = globalInfos.SHAPE_COLORS
NOTHING_CHAR = globalInfos.SHAPE_NOTHING_CHAR
COLOR_SHAPES_DEFAULT_COLOR = COLORS[0]
NO_COLOR_SHAPES_DEFAULT_COLOR = NOTHING_CHAR
STRUCT_COLORS = ["r","g","b","w"]
STRUCT_SHAPE = {
    SHAPE_CONFIG_QUAD : "C",
    SHAPE_CONFIG_HEX : "H"
}

PARAM_PREFIX = "+"
DISPLAY_PARAM_PREFIX = "/"
DISPLAY_PARAM_EXIT_CHAR = " "
DISPLAY_PARAM_KEY_VALUE_SEPARATOR = ":"
SHAPE_CODE_OPENING = "{"
SHAPE_CODE_CLOSING = "}"
INGNORE_CHARS_IN_SHAPE_CODE = ["`"]


def getPotentialShapeCodesFromMessage(message:str) -> list[str]:
    if (message == "") or (SHAPE_CODE_OPENING not in message):
        return []
    openingSplits = message.split(SHAPE_CODE_OPENING)[1:]
    potentialShapeCodes = []
    for split in openingSplits:
        if SHAPE_CODE_CLOSING in split:
            potentialShapeCode = split.split(SHAPE_CODE_CLOSING)[0]
            if potentialShapeCode != "":
                potentialShapeCodes.append(potentialShapeCode)
    return potentialShapeCodes

def getPotentialDisplayParamsFromMessage(message:str) -> list[tuple]:
    if (message == "") or (DISPLAY_PARAM_PREFIX not in message):
        return []
    prefixSplits = message.split(DISPLAY_PARAM_PREFIX)[1:]
    potentialDisplayParams = []
    for split in prefixSplits:
        if DISPLAY_PARAM_EXIT_CHAR in split:
            potentialDisplayParam = split.split(DISPLAY_PARAM_EXIT_CHAR)[0]
        else:
            potentialDisplayParam = split
        if DISPLAY_PARAM_KEY_VALUE_SEPARATOR in potentialDisplayParam:
            potentialDisplayParams.append(tuple(potentialDisplayParam.split(DISPLAY_PARAM_KEY_VALUE_SEPARATOR)[:2]))
        else:
            potentialDisplayParams.append((potentialDisplayParam,))
    return potentialDisplayParams

def _separateInLayers(potentialShapeCode:str) -> tuple[str|list[str],bool]:
    if globalInfos.SHAPE_LAYER_SEPARATOR in potentialShapeCode:
        layers = potentialShapeCode.split(globalInfos.SHAPE_LAYER_SEPARATOR)
        for i,layer in enumerate(layers):
            if layer == "":
                return f"Layer {i+1} empty",False
    else:
        if potentialShapeCode == "":
            return "Empty shape code",False
        layers = [potentialShapeCode]
    return layers,True

def _verifyOnlyValidChars(layers:list[str],shapeConfig:str) -> tuple[str|None,bool]:
    for layerIndex,layer in enumerate(layers):
        for charIndex,char in enumerate(layer):
            if char not in [*COLOR_SHAPES[shapeConfig],*NO_COLOR_SHAPES[shapeConfig],*COLORS,NOTHING_CHAR]:
                return f"Invalid char in layer {layerIndex+1} ({layer}), at char {charIndex+1} : '{char}'",False
    return None,True

def _verifyShapesAndColorsInRightPos(layers:list[str],shapeConfig:str) -> tuple[str|None,bool]:
    for layerIndex,layer in enumerate(layers):
        shapeMode = True
        lastChar = len(layer)-1
        for charIndex,char in enumerate(layer):
            errorMsgStart = f"Char in layer {layerIndex+1} ({layer}) at char {charIndex+1} ({char})"
            if shapeMode:
                if char not in [*COLOR_SHAPES[shapeConfig],*NO_COLOR_SHAPES[shapeConfig],NOTHING_CHAR]:
                    return f"{errorMsgStart} must be a shape or empty",False
                if charIndex == lastChar:
                    return f"{errorMsgStart} should have a color but is end of layer",False
                if char in [*NO_COLOR_SHAPES[shapeConfig],NOTHING_CHAR]:
                    nextMustBeColor = False
                else:
                    nextMustBeColor = True
                shapeMode = False
            else:
                if char not in [*COLORS,NOTHING_CHAR]:
                    return f"{errorMsgStart} must be a color or empty",False
                if nextMustBeColor and (char not in COLORS):
                    return f"{errorMsgStart} must be a color",False
                if (not nextMustBeColor) and (char != NOTHING_CHAR):
                    return f"{errorMsgStart} must be empty",False
                shapeMode = True
    return None,True

def _verifyAllLayersHaveSameLen(layers:list[str]) -> tuple[str|None,bool]:
    expectedLayerLen = len(layers[0])
    for layerIndex,layer in enumerate(layers[1:]):
        if len(layer) != expectedLayerLen:
            return f"Layer {layerIndex+2} ({layer}){f' (or 1 ({layers[0]}))' if layerIndex == 0 else ''} doesn't have the expected number of quadrants",False
    return None,True

def _isShapeEmpty(layers:list[str]) -> bool:
    return all(all(c == NOTHING_CHAR for c in l) for l in layers)

def generateShapeCodes(potentialShapeCode:str) -> tuple[tuple[list[str],str]|str,bool]:
    """Returns (``([shapeCode0,shapeCode1,...], shapeConfig)`` or ``errorMsg``), ``isShapeCodeValid``"""

    def getStructColor(layer:int) -> str:
        return STRUCT_COLORS[min(layer,len(STRUCT_COLORS)-1)]

    for char in INGNORE_CHARS_IN_SHAPE_CODE:
        potentialShapeCode = potentialShapeCode.replace(char,"")

    if PARAM_PREFIX in potentialShapeCode:
        params = potentialShapeCode.split(PARAM_PREFIX)
        potentialShapeCode = params[0]
        params = params[1:]
    else:
        params = []

    cutInParams = "cut" in params
    qcutInParams = "qcut" in params
    if cutInParams and qcutInParams:
        return "Mutualy exclusive 'cut' and 'qcut' parameters present",False

    hexInParams = "hex" in params
    curShapeConfig = SHAPE_CONFIG_HEX if hexInParams else SHAPE_CONFIG_QUAD

    structInParams = "struct" in params

    # separate in layers
    layersResult = _separateInLayers(potentialShapeCode)
    if not layersResult[1]:
        return layersResult[0],False
    layers:list[str] = layersResult[0]

    # handle lfill
    if "lfill" in params:
        layersLen = len(layers)
        if layersLen == 1:
            layers = [layers[0]] * 4
        elif layersLen == 2:
            layers = [layers[0],layers[1]] * 2

    # handle struct
    if structInParams:
        for i,layer in enumerate(layers):
            newLayer = ""
            color = getStructColor(i)
            for char in layer:
                if char == "1":
                    newLayer += STRUCT_SHAPE[curShapeConfig] + color
                elif char == "0":
                    newLayer += NOTHING_CHAR * 2
                else:
                    newLayer += char
            layers[i] = newLayer

    # replace some characters
    for old,new in globalInfos.SHAPE_CHAR_REPLACEMENT.items():
        for layerIndex,layer in enumerate(layers):
            layers[layerIndex] = layer.replace(old,new)

    # verify if only valid chars
    validCharsResult = _verifyOnlyValidChars(layers,curShapeConfig)
    if not validCharsResult[1]:
        return validCharsResult[0],False

    # handle {C} -> {Cu} transformation
    for layerIndex,layer in enumerate(layers):
        newLayer = ""
        lastChar = len(layer)-1
        skipNext = False
        for charIndex,char in enumerate(layer):
            if skipNext:
                newLayer += char
                skipNext = False
                continue
            expand = False
            isLastChar = charIndex == lastChar
            if (char in COLOR_SHAPES[curShapeConfig]) and ((isLastChar) or (layer[charIndex+1] not in COLORS)):
                expand = True
            elif (char in [*NO_COLOR_SHAPES[curShapeConfig],NOTHING_CHAR]) and ((isLastChar) or (layer[charIndex+1] != NOTHING_CHAR)):
                expand = True
            if expand:
                if char in [*NO_COLOR_SHAPES[curShapeConfig],NOTHING_CHAR]:
                    newLayer += char + NO_COLOR_SHAPES_DEFAULT_COLOR
                else:
                    newLayer += char + (getStructColor(layerIndex) if structInParams else COLOR_SHAPES_DEFAULT_COLOR)
            else:
                skipNext = True
                newLayer += char
        layers[layerIndex] = newLayer

    # verify if shapes and colors are in the right positions
    shapesAndColorsInRightPosResult = _verifyShapesAndColorsInRightPos(layers,curShapeConfig)
    if not shapesAndColorsInRightPosResult[1]:
        return shapesAndColorsInRightPosResult[0],False

    # handle fill
    if "fill" in params:
        for layerIndex,layer in enumerate(layers):
            newLayer = ""
            layerLen = len(layer)
            if hexInParams:
                if layerLen == 2:
                    newLayer = layer * 6
                elif layerLen == 4:
                    newLayer = layer * 3
                elif layerLen == 6:
                    newLayer = layer * 2
                else:
                    newLayer = layer
            else:
                if layerLen == 2:
                    newLayer = layer * 4
                elif layerLen == 4:
                    newLayer = layer * 2
                else:
                    newLayer = layer
            layers[layerIndex] = newLayer

    # verify all layers have the same length
    allLayersHaveSameLenResult = _verifyAllLayersHaveSameLen(layers)
    if not allLayersHaveSameLenResult[1]:
        return allLayersHaveSameLenResult[0],False

    # handle lsep
    if "lsep" in params:
        shapeCodes = [[layer] for layer in layers]
    else:
        shapeCodes = [layers]

    # handle cut
    if cutInParams:
        newShapeCodes = []
        for shape in shapeCodes:
            numQuads = round(len(shape[0])/2)
            takeQuads = math.ceil(numQuads/2)
            shape1 = []
            shape2 = []
            for layer in shape:
                shape1.append(f"{NOTHING_CHAR*((numQuads-takeQuads)*2)}{layer[-(takeQuads*2):]}")
                shape2.append(f"{layer[:-(takeQuads*2)]}{NOTHING_CHAR*(takeQuads*2)}")
            newShapeCodes.extend([shape1,shape2])

    # handle qcut
    elif qcutInParams:
        newShapeCodes = []
        for shape in shapeCodes:
            numQuads = round(len(shape[0])/2)
            takeQuads = math.ceil(numQuads/2)
            takeQuads1 = math.ceil(takeQuads/2)
            takeQuads2 = takeQuads - takeQuads1
            takeQuads3 = math.ceil((numQuads-takeQuads)/2)
            takeQuads4 = numQuads - takeQuads - takeQuads3
            shape1 = []
            shape2 = []
            shape3 = []
            shape4 = []
            for layer in shape:
                shape1.append(f"{layer[:takeQuads1*2]}{NOTHING_CHAR*((takeQuads2+takeQuads3+takeQuads4)*2)}")
                shape2.append(f"{NOTHING_CHAR*(takeQuads1*2)}{layer[takeQuads1*2:(takeQuads1+takeQuads2)*2]}{NOTHING_CHAR*((takeQuads3+takeQuads4)*2)}")
                shape3.append(f"{NOTHING_CHAR*((takeQuads1+takeQuads2)*2)}{layer[(takeQuads1+takeQuads2)*2:(takeQuads1+takeQuads2+takeQuads3)*2]}{NOTHING_CHAR*(takeQuads4*2)}")
                shape4.append(f"{NOTHING_CHAR*((takeQuads1+takeQuads2+takeQuads3)*2)}{layer[(takeQuads1+takeQuads2+takeQuads3)*2:]}")
            newShapeCodes.extend([shape1,shape2,shape3,shape4])
    else:
        newShapeCodes = shapeCodes

    noEmptyShapeCodes = []
    for shape in newShapeCodes:
        if not _isShapeEmpty(shape):
            noEmptyShapeCodes.append(globalInfos.SHAPE_LAYER_SEPARATOR.join(shape))

    return (noEmptyShapeCodes,curShapeConfig),True

def isShapeCodeValid(potentialShapeCode:str,shapeConfig:str|None,emptyShapeInvalid:bool=False) -> tuple[None|str,bool]:

    layersResult = _separateInLayers(potentialShapeCode)
    if not layersResult[1]:
        return layersResult[0],False
    layers:list[str] = layersResult[0]

    if shapeConfig is None:
        for testShapeConfig in (SHAPE_CONFIG_QUAD,SHAPE_CONFIG_HEX):
            validCharsResult = _verifyOnlyValidChars(layers,testShapeConfig)
            if validCharsResult[1]:
                shapeConfig = testShapeConfig
                break
        if shapeConfig is None:
            return validCharsResult[0],False
    else:
        validCharsResult = _verifyOnlyValidChars(layers,shapeConfig)
        if not validCharsResult[1]:
            return validCharsResult[0],False

    shapesAndColorsInRightPosResult = _verifyShapesAndColorsInRightPos(layers,shapeConfig)
    if not shapesAndColorsInRightPosResult[1]:
        return shapesAndColorsInRightPosResult[0],False

    allLayersHaveSameLenResult = _verifyAllLayersHaveSameLen(layers)
    if not allLayersHaveSameLenResult[1]:
        return allLayersHaveSameLenResult[0],False

    if emptyShapeInvalid and _isShapeEmpty(layers):
        return "Shape is fully empty",False

    return None,True