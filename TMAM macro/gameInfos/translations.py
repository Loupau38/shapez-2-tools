import globalInfos
import json
import typing

class StringComponent:
    def __init__(self,value:str) -> None:
        self.value = value

class TagComponent:
    def __init__(self,type:typing.Literal["single","start","end"],value:str) -> None:
        self.type = type
        self.value = value

    def asString(self) -> str:
        returnString = "<"
        if self.type == "end":
            returnString += "/"
        returnString += self.value
        if self.type == "single":
            returnString += "/"
        returnString += ">"
        return returnString

class TranslationString:
    def __init__(self,rawString:str,parsedString:str,components:list[StringComponent|TagComponent]) -> None:
        self.rawString = rawString
        self.parsedString = parsedString
        self.components = components

def _loadTranslations() -> dict[str,TranslationString]:

    with open(globalInfos.GI_TRANSLATIONS_PATH,encoding="utf-8") as f:
        raw:dict[str,str] = json.load(f)
    parsedTranslations:dict[str,TranslationString] = {}

    def decodeString(key:str) -> TranslationString:

        if parsedTranslations.get(key) is not None:
            return parsedTranslations[key]

        rawString = raw[key]
        components:list[StringComponent|TagComponent] = []
        openingSplits = rawString.split("<")
        components.append(StringComponent(openingSplits[0]))

        for split in openingSplits[1:]:
            tag,text = split.split(">")
            if tag.startswith("/"):
                tagType = "end"
            elif tag.endswith("/"):
                tagType = "single"
            else:
                tagType = "start"
            components.append(TagComponent(tagType,tag.removeprefix("/").removesuffix("/")))
            components.append(StringComponent(text))

        newComponents:list[StringComponent|TagComponent] = []
        for component in components:
            if (type(component) == TagComponent) and (component.type == "single") and (component.value.startswith("copy-from:")):
                newComponents.extend(decodeString(component.value.removeprefix("copy-from:")).components)
            else:
                newComponents.append(component)

        parsedString = ""
        for component in newComponents:
            if type(component) == StringComponent:
                parsedString += component.value
            else:
                parsedString += component.asString()

        parsedTranslations[key] = TranslationString(rawString,parsedString,newComponents)
        return parsedTranslations[key]

    for key in raw.keys():
        decodeString(key)
    return parsedTranslations

_translations = _loadTranslations()

def getTranslation(key:str) -> str:
    if _translations.get(key) is None:
        return key
    return _translations[key].parsedString