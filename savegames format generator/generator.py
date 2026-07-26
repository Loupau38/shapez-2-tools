import classes
from classes import (
    byte,
    short,
    ushort,
    uint,
    long,
    ulong,
    Checkpoint,
    Blob,
    Array
)
from dataclasses import dataclass

FORMAT_OBJECTS:dict[str,type] = {
    "BUILDINGS_BIN_FORMAT" : classes.BuildingsBIN,
    "ISLANDS_BIN_FORMAT" : classes.IslandsBIN,
    "STRINGS_BIN_FORMAT" : classes.StringLUT
}
INPUT_FILE = "./base.md"
OUTPUT_FILE = "./output.md"

@dataclass
class Link:
    text:str
    link:str

type RawTextContentInner = str|type|list[list[RawTextContent]]
type RawTextContent = RawTextContentInner|tuple[RawTextContentInner,...]
type TextContent = list[str|Link|Table]

@dataclass
class Cell:
    content:TextContent
    width:int=1
    height:int=1

@dataclass
class Table:
    rows:list[list[Cell]]

@dataclass
class FormatTableRow:
    typeInfo:Link|str
    desc:TextContent
    paddingWidth:int=0
    paddingHeight:int=0

# add new types to list and function at the same time
BASE_TYPES = [
    byte,bytes,
    short,ushort,int,uint,long,ulong,
    bool,str,
    Checkpoint,Blob,Array
]
def typeLink(t:type) -> Link|str:
    if t == byte:
        return Link("byte","byte")
    if t == bytes:
        return "bytes"
    if t in (short,ushort,int,uint,long,ulong):
        return Link(t.__name__,"integers")
    if t == bool:
        return Link("bool","bool")
    if t == str:
        return Link("string","string")
    if t == Checkpoint:
        return Link("Checkpoint","checkpoint")
    if t == Blob:
        return Link("Blob","blob")
    if t == Array:
        return Link("Array","array")
    return Link(t.__name__,t.__name__.lower())

def parseTextContent(raw:RawTextContent) -> TextContent:

    if not isinstance(raw,tuple):
        raw = (raw,)

    parsed:TextContent = []
    for elem in raw:

        if isinstance(elem,str):
            parsed.append(elem)
        elif isinstance(elem,type):
            addContainedObj(elem)
            parsed.append(typeLink(elem))
        else:
            parsed.append(Table([[Cell(parseTextContent(c)) for c in r] for r in elem]))

    return parsed

def genFormatTableRows(contents) -> list[FormatTableRow]:

    generatedRows:list[FormatTableRow] = []

    for line in contents:

        if isinstance(line,Checkpoint):
            generatedRows.append(FormatTableRow(
                typeLink(Checkpoint),
                [f"`{line.id}`"]
            ))
            continue

        typeInfo, *desc = line
        typeInfo:type|Checkpoint|Blob|Array
        desc:RawTextContent = tuple(desc)

        if isinstance(typeInfo,(Blob,Array)):
            innerRows = genFormatTableRows(typeInfo.content)
            innerRows[0].paddingHeight = len(innerRows)
            for r in innerRows:
                r.paddingWidth += 1
            generatedRows.append(FormatTableRow(
                typeLink(Blob if isinstance(typeInfo,Blob) else Array),
                parseTextContent(desc)
            ))
            generatedRows.extend(innerRows)

        else:
            addContainedObj(typeInfo)
            generatedRows.append(FormatTableRow(
                typeLink(typeInfo),
                parseTextContent(desc)
            ))

    return generatedRows

def formatRowsToTable(rows:list[FormatTableRow]) -> Table:
    typeColumnWidth = max(r.paddingWidth for r in rows) + 1
    tableRows = [[
        Cell(["Type"],typeColumnWidth),
        Cell(["Description"])
    ]]
    for r in rows:
        tr = []
        if r.paddingHeight != 0:
            tr.append(Cell(["|"],height=r.paddingHeight))
        tr.append(Cell([r.typeInfo],typeColumnWidth-r.paddingWidth))
        tr.append(Cell(r.desc))
        tableRows.append(tr)
    return Table(tableRows)

def renderTextMarkdown(text:TextContent) -> str:
    out = ""
    for i,elem in enumerate(text):
        if isinstance(elem,str):
            out += elem
        elif isinstance(elem,Link):
            out += f"[{elem.text}](#{elem.link})"
        else:
            if i != 0:
                out += "\n\n"
            out += renderTable(elem)
            if i != len(text)-1:
                out += "\n\n"
    return out

def convertCodeStyleToHTML(raw:str) -> str:
    assert raw.count("`")%2 == 0
    new = ""
    for i,s in enumerate(raw.split("`")):
        if i != 0:
            new += "</code>" if i%2 == 0 else "<code>"
        new += s
    return new

def renderTextHTML(text:TextContent) -> str:
    out = ""
    for elem in text:
        if isinstance(elem,str):
            out += convertCodeStyleToHTML(elem)
        elif isinstance(elem,Link):
            out += f"<a href=\"#{elem.link}\">{elem.text}</a>"
        else:
            out += renderTableHTML(elem)
    return out

def renderTableMarkdown(table:Table) -> str:
    out = "|"
    for c in table.rows[0]:
        out += renderTextMarkdown(c.content)
        out += "|"
    out += "\n|"
    out += "-|" * len(table.rows[0])
    for r in table.rows[1:]:
        out += "\n|"
        for c in r:
            out += renderTextMarkdown(c.content)
            out += "|"
    return out

def renderTableHTML(table:Table) -> str:
    out = "<table>"
    for i,r in enumerate(table.rows):
        out += "<tr>"
        for c in r:
            cellType = "th" if i == 0 else "td"
            out += f"<{cellType}"
            if c.width != 1:
                out += f" colspan=\"{c.width}\""
            elif c.height != 1:
                out += f" rowspan=\"{c.height}\""
            out += ">"
            out += renderTextHTML(c.content)
            out += f"</{cellType}>"
        out += "</tr>"
    out += "</table>"
    return out

def renderTable(table:Table) -> str:
    def needsHTML() -> bool:
        for r in table.rows:
            for c in r:
                if c.width != 1:
                    return True
                if c.height != 1:
                    return True
                for e in c.content:
                    if isinstance(e,Table):
                        return True
        return False
    if needsHTML():
        return renderTableHTML(table)
    return renderTableMarkdown(table)

def processClass(cls:type) -> str:
    out = ""
    if hasattr(cls,"d"):
        out += renderTextMarkdown(parseTextContent(cls.d))
    if hasattr(cls,"c"):
        if len(out) > 0:
            out += "\n\n"
        out += renderTable(formatRowsToTable(genFormatTableRows(cls.c)))
    return out

# can't use a set because it changes size while iterating over it
containedObjects = list[type]()
def addContainedObj(obj:type) -> None:
    if (obj not in BASE_TYPES) and (obj not in containedObjects):
        containedObjects.append(obj)

with open(INPUT_FILE,encoding="utf-8") as f:
    fileContent = f.read()

for replace,cls in FORMAT_OBJECTS.items():
    fileContent = fileContent.replace(replace,processClass(cls))

containedObjectsStr = list[str]()
for cls in containedObjects:
    cur = f"#### {cls.__name__}"
    cur += "\n\n"
    cur += processClass(cls)
    containedObjectsStr.append(cur)
fileContent = fileContent.replace("CONTAINED_OBJECTS_FORMAT","\n\n".join(containedObjectsStr))

with open(OUTPUT_FILE,"w",encoding="utf-8") as f:
    f.write(fileContent)