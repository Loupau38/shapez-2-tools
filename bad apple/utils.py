import typing
import pygame
import io

_NUMBERS = [str(num) for num in range(10)]
def isNumber(string:str) -> bool:
    if string == "":
        return False
    for char in string:
        if char not in _NUMBERS:
            return False
    return True

def pygameSurfToBytes(surf:pygame.Surface) -> tuple[io.BytesIO,int]:
    with io.BytesIO() as buffer:
        pygame.image.save(surf,buffer,"png")
        bufferValue = buffer.getvalue()
        bytesLen = len(bufferValue)
        finalBytes = io.BytesIO(bufferValue)
    return finalBytes, bytesLen

def decodeUnityFormat(text:str) -> list[dict[str,str|dict[str,bool|str]]]:
    tagNameToKey = {
        "b" : "bold",
        "color" : "color"
    }
    mode = "normal"
    curFormat = {
        "bold" : False,
        "color" : False
    }
    isClosingTag = False
    curText = ""
    decoded = []
    for char in text:
        closeTag = False
        if mode == "normal":
            if char == "<":
                mode = "tagName"
                decoded.append({
                    "format" : curFormat.copy(),
                    "text" : curText
                })
                curText = ""
                curTagName = ""
                curTagValue = ""
            else:
                curText += char
        elif mode == "tagName":
            if char == "/":
                isClosingTag = True
            elif char == ">":
                closeTag = True
            elif char == "=":
                mode = "tagValue"
            else:
                curTagName += char
        elif mode == "tagValue":
            if char == ">":
                closeTag = True
            else:
                curTagValue += char
        if closeTag:
            if isClosingTag:
                curFormat[tagNameToKey[curTagName]] = False
            else:
                if curTagValue == "":
                    curFormat[tagNameToKey[curTagName]] = True
                else:
                    curFormat[tagNameToKey[curTagName]] = curTagValue
            mode = "normal"
            isClosingTag = False
    decoded.append({
        "format" : curFormat.copy(),
        "text" : curText
    })
    return decoded

def decodedFormatToDiscordFormat(decoded:list[dict[str,str|dict[str,bool|str]]]) -> str:
    output = ""
    defaultFormat = {"bold":False,"color":False}
    previousFormat = defaultFormat
    for elem in [*decoded,{"format":defaultFormat,"text":""}]:
        curFormat = elem["format"]
        if curFormat["bold"] != previousFormat["bold"]:
            output += "**"
        elif curFormat["color"] != previousFormat["color"]:
            output += "__"
        output += elem["text"]
        previousFormat = curFormat
    return output

def decodeHexColor(hex:str) -> tuple[int,int,int]:
    return int(hex[:2],16), int(hex[2:4],16), int(hex[4:],16)

def decodedFormatToPygameSurf(decoded:list[dict[str,str|dict[str,bool|str]]],font:pygame.font.Font,
    boldFont:pygame.font.Font,antialias:bool|int,defaultColor:tuple[int,int,int]) -> pygame.Surface:
    texts:list[pygame.Surface] = []
    for elem in decoded:
        curFont = boldFont if elem["format"]["bold"] else font
        args = [elem["text"],antialias]
        if elem["format"]["color"] is False:
            args.append(defaultColor)
        else:
            args.append(decodeHexColor(elem["format"]["color"]))
        texts.append(curFont.render(*args))
    surf = pygame.Surface((sum(t.get_width() for t in texts),max(t.get_height() for t in texts)),pygame.SRCALPHA)
    curX = 0
    for text in texts:
        surf.blit(text,(curX,(surf.get_height()/2)-(text.get_height()/2)))
        curX += text.get_width()
    return surf

def sepInGroupsNumber(num:int) -> str:
    return f"{num:,}"

def decodeStringWithLen(string:bytes,numBytesForLen:int=2,emptyIsLengthNegative1:bool=True) -> bytes:
    stringLen = len(string)
    if stringLen < numBytesForLen:
        raise ValueError(f"String must be at least {numBytesForLen} characters long but is {stringLen}")
    encodedLength, string = string[:numBytesForLen], string[numBytesForLen:]
    decodedLength = int.from_bytes(encodedLength,"little",signed=True)
    if (emptyIsLengthNegative1) and (decodedLength == -1):
        decodedLength = 0
    if decodedLength < 0:
        raise ValueError(f"String length can't be negative : {decodedLength}")
    stringLen = len(string)
    if stringLen < decodedLength:
        raise ValueError(f"String is shorter than expected length ({stringLen} vs {decodedLength})")
    decodedString = string[:decodedLength]
    return decodedString

def encodeStringWithLen(string:bytes,numBytesForLen:int=2,emptyIsLengthNegative1:bool=True) -> bytes:
    stringLen = len(string)
    if emptyIsLengthNegative1 and (stringLen == 0):
        stringLen = -1
    return stringLen.to_bytes(numBytesForLen,"little",signed=True) + string



class OutputString:

    class Number:
        def __init__(self,num:int|float,isIndex:bool=False) -> None:
            self.num = num
            self.isIndex = isIndex

    class UnsafeString:
        def __init__(self,string:str) -> None:
            self.string = string

    class UnsafeNumber:
        def __init__(self,num:int|float,isIndex:bool=False) -> None:
            self.num = num
            self.isIndex = isIndex

    def __init__(self,*elems:str|Number|UnsafeString|UnsafeNumber|typing.Self) -> None:
        self.elems = list(elems)

    def render(self,isShownPublicly:bool) -> str:

        output = ""
        for elem in self.elems:
            elemType = type(elem)

            if elemType == str:
                output += elem

            elif elemType == OutputString.UnsafeString:
                if isShownPublicly:
                    output += f"<{len(elem.string)} character(s) long string not shown because public>"
                else:
                    output += elem.string

            elif elemType == OutputString.Number:
                output += str(elem.num + (1 if elem.isIndex else 0))

            elif elemType == OutputString.UnsafeNumber:
                output += str(elem.num + (1 if elem.isIndex else 0))

            elif elemType == OutputString:
                output += elem.render(isShownPublicly)

            else:
                raise TypeError(f"Unknown elem type in OutputString.elems while executing 'render' function : {elemType.__name__}")

        return output

class Rotation:
    def __init__(self,value:int) -> None:
        self.value = value

    def rotateCW(self,numTimes:int|typing.Self) -> typing.Self:
        if type(numTimes) == Rotation:
            numTimes = numTimes.value
        return Rotation((self.value+numTimes)%4)

class FloatPos:
    def __init__(self,x:float,y:float,z:float=0.0) -> None:
        self.x = x
        self.y = y
        self.z = z

class Pos:
    def __init__(self,x:int,y:int,z:int=0) -> None:
        self.x = x
        self.y = y
        self.z = z

    def __str__(self) -> str:
        return f"Pos({self.x},{self.y},{self.z})"

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return str(self).__hash__()

    def __eq__(self,other:object) -> bool:
        if type(other) != Pos:
            return False
        return (self.x == other.x) and (self.y == other.y) and (self.z == other.z)

    def rotateCW(self,numTimes:int|Rotation,aroundCenter:FloatPos=FloatPos(0,0)) -> typing.Self:
        if type(numTimes) == Rotation:
            numTimes = numTimes.value
        x, y = self.x-aroundCenter.x, self.y-aroundCenter.y
        for _ in range(numTimes):
            x, y = -y, x
        return Pos(round(x+aroundCenter.x),round(y+aroundCenter.y),self.z)

class Size:
    def __init__(self,width:int,height:int,depth:int=0) -> None:
        self.width = width
        self.height = height
        self.depth = depth

    def rotateCW(self,numTimes:int|Rotation) -> typing.Self:
        if type(numTimes) == Rotation:
            numTimes = numTimes.value
        width, height = self.width, self.height
        for _ in range(numTimes):
            width, height = height, width
        return Size(width,height,self.depth)

class Rect:
    def __init__(self,topLeft:Pos,size:Size) -> None:
        self.topLeft = topLeft
        self.size = size

    def rotateCW(self,numTimes:int|Rotation,aroundCenter:FloatPos=FloatPos(0,0)) -> typing.Self:
        if type(numTimes) == Rotation:
            numTimes = numTimes.value
        left, top = self.topLeft.x-aroundCenter.x, self.topLeft.y-aroundCenter.y
        width, height = self.size.width, self.size.height
        for _ in range(numTimes):
            left, top = -top-height+1, left
            width, height = height, width
        return Rect(
            Pos(round(left+aroundCenter.x),round(top+aroundCenter.y)),
            Size(width,height)
        )

    def containsPos(self,pos:Pos) -> bool:
        if pos.x < self.topLeft.x:
            return False
        if pos.y < self.topLeft.y:
            return False
        if pos.x >= self.topLeft.x+self.size.width:
            return False
        if pos.y >= self.topLeft.y+self.size.height:
            return False
        return True