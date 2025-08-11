# you might want to set this to False if the window is too small or if not on Windows
SET_DPI_AWARE = True

# if the auto detection doesn't work
SAVEGAMES_PATH_OVERRIDE:str|None = None

import zipfile
import os
import typing
import datetime
import sys
import json
import io
import math

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""

def errorExit(msg:str) -> typing.NoReturn:
    print(msg)
    input("Press enter to exit")
    exit()

try:
    import shapez2
    import pygame
except ModuleNotFoundError:
    errorExit("'shapez2' and 'pygame' required if using python file")

import fixedint
import pygame._sdl2

# https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile/13790741#13790741
def resourcePath(relativePath:str) -> str:
    try:
        basePath = sys._MEIPASS
    except AttributeError:
        basePath = os.path.abspath(".")
    return os.path.join(basePath,relativePath)

def orderBackups(folderPath:str) -> list[str]:
    curBackups = []
    for dirEntry in os.scandir(folderPath):
        if dirEntry.is_file() and dirEntry.name.startswith("backup-v"):
            curBackups.append((
                dirEntry.path,
                int(dirEntry.name.removeprefix("backup-v").split("-")[0])
            ))
    curBackups = sorted(curBackups,key=lambda b: b[1],reverse=True)
    return [b[0] for b in curBackups]

def extractFiles(backupPath:str) -> tuple[dict,dict]:
    with zipfile.ZipFile(backupPath,"r") as zipRef:
        zipRef.extractall(workingFolder,["savegame.json","research.json"])
    with open(os.path.join(workingFolder,"savegame.json")) as f:
        savegameInfo = json.load(f)
    with open(os.path.join(workingFolder,"research.json")) as f:
        researchInfo = json.load(f)
    return savegameInfo, researchInfo

def PILToPygame(pil:shapez2.pygamePIL.Surface) -> pygame.Surface:
    with io.BytesIO() as b:
        shapez2.pygamePIL.image.save(pil,b,"png")
        b.seek(0)
        new = pygame.image.load(b)
    return new

def pygameToPIL(py:pygame.Surface) -> shapez2.pygamePIL.Surface:
    with io.BytesIO() as b:
        pygame.image.save(py,b,"png")
        new = shapez2.pygamePIL.image.load(b)
    return new

def goalLineAmount(level:int,start:int,growth:int) -> int:
    return round(min(start*((1+(growth/100))**level),(2**31)-1001)/100)*100

def shapesDiffBetweenLevels(
    levelBefore:int,
    shapesBefore:int,
    levelAfter:int,
    shapesAfter:int,
    start:int,
    growth:int
) -> int:
    if levelBefore == levelAfter:
        return shapesAfter - shapesBefore
    curCount = goalLineAmount(levelBefore,start,growth) - shapesBefore
    for lvl in range(levelBefore+1,levelAfter):
        curCount += goalLineAmount(lvl,start,growth)
    curCount += shapesAfter
    return curCount

class GoalLineStats(typing.TypedDict):
    id:str
    curLevel:int
    curAmount:int
    goalAmount:int
    goalShape:str
    curRawRate:float
    curRawSpaceBeltRate:float
    curMultRate:float
    curMultSpaceBeltRate:float

class SavegameStats(typing.TypedDict):
    ol:int
    shapeMult:int
    beltSpeed:int
    scenario:shapez2.research.Scenario
    researchPoints:int
    goalLines:list[GoalLineStats]

def loadSave(uuid:str,numBackups:int) -> SavegameStats:

    SPACE_BELT_BASE_SPEED = 120 * 12 * 4

    class BackupStats(typing.TypedDict):
        time:datetime.datetime
        goalLines:dict[str,tuple[int,int,str]]

    def getStatsFromBackup(path:str) -> BackupStats:

        savegameInfo, researchInfo = extractFiles(path)
        savegameScenario = shapez2.research.ingameScenarios[savegameInfo["Parameters"]["ScenarioParameters"]["ScenarioId"]]
        rosGen:list[shapez2.gameCode.RandomResearchShapeGenerator.RandomResearchShapeGenerator] = []
        for crystals in (False,True):
            rosGen.append(shapez2.gameCode.RandomResearchShapeGenerator.RandomResearchShapeGenerator(
                shapez2.gameCode.otherClasses.GameMode(
                    savegameScenario.researchConfig.shapesConfig,
                    savegameScenario.researchConfig.colorScheme,
                    fixedint.Int32(savegameInfo["Parameters"]["Seed"]),
                    fixedint.Int32(savegameScenario.researchConfig.maxShapeLayers)
                ),
                shapez2.gameCode.otherClasses.ShapeRegistry(
                    savegameScenario.researchConfig.shapesConfig,
                    fixedint.Int32(savegameScenario.researchConfig.maxShapeLayers)
                ),
                crystals
            ))

        goalLines = {}
        for id,lvl in researchInfo["PlayerLevelGoals"]["GoalLevels"].items():
            curGoalLine = savegameScenario.operatorLevelConfig.goalLinesById[id]
            if curGoalLine.type == shapez2.research.OperatorLevelGoalLineType.shape:
                curShape = curGoalLine.shape
            elif curGoalLine.type == shapez2.research.OperatorLevelGoalLineType.randomNoCrystals:
                curShape = rosGen[0].Generate(fixedint.Int32(lvl+1))
            else:
                curShape = rosGen[1].Generate(fixedint.Int32(lvl+1))
            curShapeCode = curShape.toShapeCode()
            goalLines[id] = (
                lvl,
                researchInfo["Shapes"]["StoredShapes"].get(curShapeCode,0),
                curShapeCode
            )

        return {
            "time" : datetime.datetime.fromisoformat(savegameInfo["LastSaved"]),
            "goalLines" : goalLines
        }

    backupPaths = orderBackups(os.path.join(savegamesPath,uuid))[:numBackups]
    backups = [getStatsFromBackup(p) for p in backupPaths]

    savegameInfo, researchInfo = extractFiles(backupPaths[0])
    savegameScenario = shapez2.research.ingameScenarios[savegameInfo["Parameters"]["ScenarioParameters"]["ScenarioId"]]
    curGoalLines = savegameScenario.operatorLevelConfig.goalLinesById
    curRates = {id:[] for id in researchInfo["PlayerLevelGoals"]["GoalLevels"].keys()}
    beltSpeedUpgradeId = savegameScenario.linearUpgradesMapping.beltSpeed.id
    shapeMultUpgradeId = savegameScenario.linearUpgradesMapping.shapeQuantity.id

    for i,backupBefore in enumerate(backups[1:]):
        backupAfter = backups[i]
        for id,(lvlBefore,shapesBefore,_) in backupBefore["goalLines"].items():
            lvlAfter, shapesAfter, _ = backupAfter["goalLines"][id]
            shapesDiff = shapesDiffBetweenLevels(
                lvlBefore,
                shapesBefore,
                lvlAfter,
                shapesAfter,
                curGoalLines[id].startingAmount,
                curGoalLines[id].growth
            )
            curRates[id].append(shapesDiff/((backupAfter["time"]-backupBefore["time"])/datetime.timedelta(minutes=1)))

    curAverageRates = {id:sum(r)/len(r) for id,r in curRates.items()}
    curBeltSpeedLevel:int = researchInfo["LinearUpgrades"]["UpgradeLevels"][beltSpeedUpgradeId]
    curShapeMultLevel:int = researchInfo["LinearUpgrades"]["UpgradeLevels"][shapeMultUpgradeId]
    curSpaceBeltSpeed = SPACE_BELT_BASE_SPEED * (
        savegameScenario.linearUpgradesById[beltSpeedUpgradeId].levels[curBeltSpeedLevel].value/100
    )
    curShapeMult = savegameScenario.linearUpgradesById[shapeMultUpgradeId].levels[curShapeMultLevel].value

    goalLineStats:list[GoalLineStats] = []
    for id,rate in curAverageRates.items():
        curLevel = backups[0]["goalLines"][id][0]
        rawRate = rate / curShapeMult
        goalLineStats.append({
            "id" : id,
            "curLevel" : curLevel,
            "curAmount" : backups[0]["goalLines"][id][1],
            "goalAmount" : goalLineAmount(
                curLevel,
                curGoalLines[id].startingAmount,
                curGoalLines[id].growth
            ),
            "goalShape" : backups[0]["goalLines"][id][2],
            "curRawRate" : rawRate,
            "curRawSpaceBeltRate" : rawRate / curSpaceBeltSpeed,
            "curMultRate" : rate,
            "curMultSpaceBeltRate" : rate / curSpaceBeltSpeed
        })

    return {
        "ol" : researchInfo["PlayerLevel"]["Level"],
        "shapeMult" : curShapeMult,
        "beltSpeed" : curBeltSpeedLevel + 1,
        "scenario" : savegameScenario,
        "researchPoints" : researchInfo["PointCurrency"]["Points"],
        "goalLines" : goalLineStats
    }

def displayTimedelta(delta:datetime.timedelta) -> str:
    hours, minutes = divmod(delta.seconds//60,60)
    return f"{delta.days}d {hours}h {minutes}min"

def displayDatetime(time:datetime.datetime) -> str:
    return time.strftime("%a %d %b %Y, %H:%M")

def main() -> None:
    global workingFolder, savegamesPath

    if SET_DPI_AWARE:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()

    os.path.expandvars("%LOCALAPPDATA%low/tobspr Games/shapez 2/savegames/")
    if SAVEGAMES_PATH_OVERRIDE is not None:
        savegamesPath = SAVEGAMES_PATH_OVERRIDE
    else:
        basePath = os.path.expanduser("~")
        windowsPath = os.path.join(basePath,"AppData","LocalLow","tobspr Games","shapez 2","savegames")
        macPath = os.path.join(basePath,"Library","Application Support","tobspr Games","shapez 2","savegames")
        linuxPath = os.path.join(basePath,".config","unity3d","tobspr Games","shapez 2","savegames")
        if os.path.exists(windowsPath):
            savegamesPath = windowsPath
        elif os.path.exists(macPath):
            savegamesPath = macPath
        elif os.path.exists(linuxPath):
            savegamesPath = linuxPath
        else:
            errorExit("Savegames folder not found, set a manual override in the python file")

    workingFolder = os.path.join(".","temp")

    win = pygame.display.set_mode((700,700),pygame.RESIZABLE)
    pygame.font.init()
    clock = pygame.time.Clock()

    pygame._sdl2.Window.from_display_module().maximize()

    FONT = pygame.font.Font(resourcePath("Barlow-Regular.ttf"),25)
    FONT_SMALL = pygame.font.Font(resourcePath("Barlow-Regular.ttf"),20)
    FONT_PIL = shapez2.pygamePIL.font.Font(resourcePath("Barlow-Regular.ttf"),25)
    FONT_PIL_BOLD = shapez2.pygamePIL.font.Font(resourcePath("Barlow-Bold.ttf"),25)

    TEXT_COLOR = (255,255,255)
    TOOLTIP_BG_COLOR = (40,40,40)
    BG_COLOR = (36,54,91)
    TOP_BAR_BG_COLOR = (55,48,81)
    BUTTON_COLOR = (29,43,73)
    BUTTON_HOVERED_COLOR = (43,65,109)
    GOAL_LINE_BG_COLOR = (147,84,46)
    GOAL_LINE_BUTTON_COLOR = (118,67,39)
    GOAL_LINE_BUTTON_HOVERED_COLOR = (176,101,55)
    FPS = 60
    SMALL_MARGIN = 5
    BIG_MARGIN = 10
    SCROLL_SPEED = 30
    SHAPE_SIZE = 100
    ICON_SIZE = 30
    NUM_GOAL_LINES_PER_ROW = 4

    SCROLL_TO_MODIFY = "Scroll to modify"

    def createInfoLine(*elems:pygame.Surface) -> tuple[pygame.Surface,list[tuple[int,float]]]:
        newSurf = pygame.Surface((
            sum(e.get_width() for e in elems) + (SMALL_MARGIN*(len(elems)-1)),
            max(e.get_height() for e in elems)
        ),pygame.SRCALPHA)
        curX = 0
        elemsPos = []
        for elem in elems:
            pos = (curX,(newSurf.get_height()/2)-(elem.get_height()/2))
            elemsPos.append(pos)
            newSurf.blit(elem,pos)
            curX += elem.get_width() + SMALL_MARGIN
        return (newSurf,elemsPos)

    curTime = datetime.datetime.now()

    def goalLineLevelCompleteTime(goalLine:int,level:int) -> datetime.timedelta:
        if goalLineLevelCompleteTimeCache[goalLine].get(level) is None:
            curGoalLineInfo = curSaveInfo["goalLines"][goalLine]
            if level == curGoalLineInfo["curLevel"]:
                shapesBefore = curGoalLineInfo["curAmount"]
            else:
                shapesBefore = 0
            curGoalLine = curSaveInfo["scenario"].operatorLevelConfig.goalLinesById[curGoalLineInfo["id"]]
            shapesDiff = shapesDiffBetweenLevels(
                level,
                shapesBefore,
                level + 1,
                0,
                curGoalLine.startingAmount,
                curGoalLine.growth
            )
            goalLineLevelCompleteTimeCache[goalLine][level] = datetime.timedelta(
                minutes=shapesDiff / curGoalLineInfo["curMultRate"]
            )
        return goalLineLevelCompleteTimeCache[goalLine][level]

    def goalLineUntilLevelCompleteTime(goalLine:int,level:int) -> datetime.timedelta:
        return sum(
            (
                goalLineLevelCompleteTime(goalLine,lvl)
                for lvl in range(curSaveInfo["goalLines"][goalLine]["curLevel"],level)
            ),
            start=datetime.timedelta(0)
        )

    def olUntilLevelCompleteTime(level:int) -> datetime.timedelta:

        def inner(level:int) -> tuple[datetime.timedelta,dict[int,tuple[int,datetime.timedelta]]]:

            if olCompleteTimeCache.get(level) is not None:
                return olCompleteTimeCache[level]

            if level == curSaveInfo["ol"]:
                olCompleteTimeCache[level] = (
                    datetime.timedelta(0),
                    {
                        i : (gl["curLevel"],goalLineLevelCompleteTime(i,gl["curLevel"]))
                        for i,gl in enumerate(curSaveInfo["goalLines"])
                        if gl["curMultRate"] != 0
                    }
                )
                return olCompleteTimeCache[level]

            timeSoFar, curGLs = inner(level-1)
            firstGL = min(((i,gl) for i,gl in curGLs.items()),key=lambda v: v[1][1])[0]
            newTime = curGLs[firstGL][1]
            newGLs = {}
            for i,gl in curGLs.items():
                if i == firstGL:
                    newGLs[i] = (gl[0]+1,goalLineLevelCompleteTime(i,gl[0]+1))
                else:
                    newGLs[i] = (gl[0],gl[1]-newTime)
            olCompleteTimeCache[level] = (timeSoFar+newTime,newGLs)
            return olCompleteTimeCache[level]

        return inner(level)[0]

    icons:dict[typing.Literal["spaceBelt","beltLauncher","shape"],pygame.Surface] = {}
    for id,file in [
        ("spaceBelt","SpaceBeltIcon.png"),
        ("beltLauncher","BeltLauncherIcon.png"),
        ("shape","ShapeIcon.png")
    ]:
        icons[id] = pygame.transform.smoothscale(pygame.image.load(resourcePath(file)),(ICON_SIZE,ICON_SIZE))

    win.blit(FONT.render("Loading...",1,TEXT_COLOR),(0,0))
    pygame.display.update()

    class SavegameInfo(typing.TypedDict):
        uuid:str
        name:str
        scenario:shapez2.research.Scenario
        ol:int
        lastSaved:datetime.datetime

    curSavegames:list[SavegameInfo] = []

    for dirEntry in os.scandir(savegamesPath):
        if dirEntry.is_dir():
            curBackups = orderBackups(dirEntry.path)
            if len(curBackups) == 0:
                continue
            savegameInfo, researchInfo = extractFiles(curBackups[0])
            savegameScenario = shapez2.research.ingameScenarios.get(
                savegameInfo["Parameters"]["ScenarioParameters"]["ScenarioId"]
            )
            if savegameScenario is None:
                continue
            curSavegames.append({
                "uuid" : dirEntry.name,
                "name" : savegameInfo["Parameters"]["SavegameName"],
                "scenario" : savegameScenario,
                "ol" : researchInfo["PlayerLevel"]["Level"],
                "lastSaved" : datetime.datetime.fromisoformat(savegameInfo["LastSaved"])
            })
    
    curSavegames = sorted(curSavegames,key=lambda s: s["lastSaved"],reverse=True)

    saveNameHeader = FONT.render("Name",1,TEXT_COLOR)
    saveScenarioHeader = FONT.render("Scenario",1,TEXT_COLOR)
    saveOLHeader = FONT.render("Operator Level",1,TEXT_COLOR)

    saveNames:list[pygame.Surface] = []
    saveScenarios:list[pygame.Surface] = []
    saveOLs:list[pygame.Surface] = []
    saveUUIDs:list[pygame.Surface] = []

    for sg in curSavegames:
        saveNames.append(PILToPygame(
            shapez2.translations.featureStringFromRaw(sg["name"])
            .renderToSurface(FONT_PIL,FONT_PIL_BOLD)
        ))
        saveScenarios.append(FONT.render(sg["scenario"].title.translate().renderToStringNoFeatures(),1,TEXT_COLOR))
        saveOLs.append(FONT.render(str(sg["ol"]),1,TEXT_COLOR))
        saveUUIDs.append(FONT_SMALL.render(sg["uuid"],1,TEXT_COLOR))

    maxNameWidth = max(max(s.get_width() for s in saveNames),saveNameHeader.get_width())
    maxScenarioWidth = max(max(s.get_width() for s in saveScenarios),saveScenarioHeader.get_width())
    maxOLWidth = max(max(s.get_width() for s in saveOLs),saveOLHeader.get_width())
    saveWidth = maxNameWidth + maxScenarioWidth + maxOLWidth + (4*BIG_MARGIN)

    curScreen = "saves"
    curNumBackupsUsed = 2
    scrollOffset = 0
    run = True
    while run:

        clock.tick(FPS)
        pygame.display.set_caption(f"Operator Level Tracker | {clock.get_fps():.0f}fps")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1):

                if curScreen == "saves":
                    if not isOverTopBar:
                        for i,r in enumerate(savegameRects):
                            if r.collidepoint(event.pos):
                                curSaveInfo = loadSave(curSavegames[i]["uuid"],curNumBackupsUsed)
                                curScreen = "OL"
                                curShapes:list[pygame.Surface] = []
                                for gl in curSaveInfo["goalLines"]:
                                    s = shapez2.pygamePIL.Surface(
                                        (SHAPE_SIZE,SHAPE_SIZE),
                                        shapez2.pygamePIL.SRCALPHA
                                    )
                                    shapez2.pygamePIL.draw.arc(
                                        s,
                                        TEXT_COLOR,
                                        shapez2.pygamePIL.Rect(0,0,SHAPE_SIZE,SHAPE_SIZE),
                                        (math.pi/2)-((gl["curAmount"]/gl["goalAmount"])*2*math.pi),
                                        math.pi / 2,
                                        3
                                    )
                                    s.blit(shapez2.shapeViewer.renderShape(
                                        shapez2.gameObjects.Shape.fromShapeCode(
                                            gl["goalShape"],
                                            curSaveInfo["scenario"].researchConfig.shapesConfig
                                        ),
                                        SHAPE_SIZE,
                                        shapesConfig=curSaveInfo["scenario"].researchConfig.shapesConfig
                                    ),(0,0))
                                    curShapes.append(PILToPygame(s))
                                goalLineLevelCompleteTimeCache:list[dict[int,datetime.timedelta]] = [{} for _ in curSaveInfo["goalLines"]]
                                goalLinesUntilLevel = [g["curLevel"]+1 for g in curSaveInfo["goalLines"]]
                                olCompleteTimeCache:dict[int,tuple[datetime.timedelta,dict[int,tuple[int,datetime.timedelta]]]] = {}
                                olUntilLevel = curSaveInfo["ol"] + 1
                                canIncreaseOL = any(gl["curMultRate"] != 0 for gl in curSaveInfo["goalLines"])
                                if canIncreaseOL:
                                    curShapeMultLevels = curSaveInfo["scenario"].linearUpgradesMapping.shapeQuantity.levels
                                    shapeMultMaxLevel = curShapeMultLevels[-1].value
                                    shapeMultMaxed = curSaveInfo["shapeMult"] == shapeMultMaxLevel
                                    if not shapeMultMaxed:
                                        shapeMultUntilLevel = curSaveInfo["shapeMult"] + 1
                                        olForShapeMult:dict[int,int] = {}
                                        curResearchPoints = curSaveInfo["researchPoints"]
                                        curOperatorLevel = curSaveInfo["ol"]
                                        curMultLevel = curSaveInfo["shapeMult"]
                                        while curMultLevel < shapeMultMaxLevel:
                                            while True:
                                                curCost = curShapeMultLevels[curMultLevel].cost.amount
                                                if curCost > curResearchPoints:
                                                    break
                                                curMultLevel += 1
                                                curResearchPoints -= curCost
                                                olForShapeMult[curMultLevel] = curOperatorLevel
                                                if curMultLevel == shapeMultMaxLevel:
                                                    break
                                            curOperatorLevel += 1
                                            for r in curSaveInfo["scenario"].operatorLevelConfig.rewards:
                                                if r.minLevel <= curOperatorLevel:
                                                    curResearchPoints += r.rewards.researchPoints
                                                    break
                                break

            elif event.type == pygame.MOUSEWHEEL:

                if curScreen == "saves":
                    if isOverTopBar:
                        if numBackupsRect.collidepoint(mousePosX,mousePosY):
                            curNumBackupsUsed = max(2,curNumBackupsUsed+event.y)
                    else:
                        scrollChange = min((-event.y)*SCROLL_SPEED,curSavegamesBottom-winHeight)
                        scrollOffset = max(scrollOffset+scrollChange,0)

                else:
                    if canIncreaseOL and olUntilLevelRect.collidepoint(mousePosX,mousePosY):
                        olUntilLevel = max(
                            olUntilLevel + event.y,
                            curSaveInfo["ol"] + 1
                        )
                    elif (
                        canIncreaseOL
                        and (not shapeMultMaxed)
                        and shapeMultUntilLevelRect.collidepoint(mousePosX,mousePosY)
                    ):
                        shapeMultUntilLevel = max(
                            min(shapeMultUntilLevel+event.y,shapeMultMaxLevel),
                            curSaveInfo["shapeMult"] + 1
                        )
                        olUntilLevel = olForShapeMult[shapeMultUntilLevel]
                    else:
                        for i,rect in enumerate(curGoalLineUntiLevelRects):
                            if (rect is not None) and (rect.collidepoint(mousePosX,mousePosY)):
                                goalLinesUntilLevel[i] = max(
                                    goalLinesUntilLevel[i] + event.y,
                                    curSaveInfo["goalLines"][i]["curLevel"] + 1
                                )

            elif event.type == pygame.KEYDOWN:
                if (curScreen == "OL") and (event.key == pygame.K_ESCAPE):
                    curScreen = "saves"

        winWidth, winHeight = win.get_size()
        mousePosX, mousePosY = pygame.mouse.get_pos()

        win.fill(BG_COLOR)
        curTooltip = None

        if curScreen == "saves":

            saveRectsLeft = (winWidth/2) - (saveWidth/2)

            numBackupsHeader = FONT.render("Number of backups to use :",1,TEXT_COLOR)
            numBackupsText = FONT.render(str(curNumBackupsUsed),1,TEXT_COLOR)
            numBackupsRect = pygame.Rect(
                saveRectsLeft + numBackupsHeader.get_width() + SMALL_MARGIN,
                BIG_MARGIN,
                numBackupsText.get_width() + (2*SMALL_MARGIN),
                numBackupsText.get_height()
            )
            topBarHeight = (
                numBackupsRect.bottom
                + max(saveNameHeader.get_height(),saveScenarioHeader.get_height(),saveOLHeader.get_height())
                + (2*BIG_MARGIN)
            )
            topBarRect = pygame.Rect(0,0,winWidth,topBarHeight)
            isOverTopBar = topBarRect.collidepoint(mousePosX,mousePosY)

            curY = topBarHeight - scrollOffset + BIG_MARGIN
            savegameRects:list[pygame.Rect] = []
            for name,scenario,ol,uuid in zip(saveNames,saveScenarios,saveOLs,saveUUIDs):
                curRect = pygame.Rect(
                    saveRectsLeft,
                    curY,
                    saveWidth,
                    name.get_height() + uuid.get_height() + (3*BIG_MARGIN)
                )
                pygame.draw.rect(
                    win,
                    BUTTON_HOVERED_COLOR if (not isOverTopBar) and curRect.collidepoint(mousePosX,mousePosY) else BUTTON_COLOR,
                    curRect,
                    border_radius=10
                )
                win.blit(name,(curRect.x+BIG_MARGIN,curRect.y+BIG_MARGIN))
                win.blit(scenario,(curRect.x+maxNameWidth+(2*BIG_MARGIN),curRect.y+BIG_MARGIN))
                win.blit(ol,(curRect.x+maxNameWidth+maxScenarioWidth+(3*BIG_MARGIN),curRect.y+BIG_MARGIN))
                win.blit(uuid,(curRect.x+BIG_MARGIN,curRect.y+name.get_height()+(2*BIG_MARGIN)))
                savegameRects.append(curRect)
                curY += curRect.height + BIG_MARGIN

            curSavegamesBottom = curY

            pygame.draw.rect(win,TOP_BAR_BG_COLOR,topBarRect)
            win.blit(numBackupsHeader,(
                saveRectsLeft,
                BIG_MARGIN
            ))
            pygame.draw.rect(
                win,
                BUTTON_HOVERED_COLOR if numBackupsRect.collidepoint(mousePosX,mousePosY) else BUTTON_COLOR,
                numBackupsRect
            )
            win.blit(numBackupsText,(numBackupsRect.x+SMALL_MARGIN,numBackupsRect.y))
            if numBackupsRect.collidepoint(mousePosX,mousePosY):
                curTooltip = SCROLL_TO_MODIFY
            win.blit(saveNameHeader,(saveRectsLeft+BIG_MARGIN,numBackupsRect.bottom+BIG_MARGIN))
            win.blit(saveScenarioHeader,(saveRectsLeft+maxNameWidth+(2*BIG_MARGIN),numBackupsRect.bottom+BIG_MARGIN))
            win.blit(saveOLHeader,(saveRectsLeft+maxNameWidth+maxScenarioWidth+(3*BIG_MARGIN),numBackupsRect.bottom+BIG_MARGIN))

        else:

            curY = BIG_MARGIN

            curX = BIG_MARGIN
            olInfoStr = f"Operator Level : {curSaveInfo["ol"]}"
            if canIncreaseOL:
                olInfoStr += "    \u2022    Until Level"
            olInfo = FONT.render(olInfoStr,1,TEXT_COLOR)
            win.blit(olInfo,(curX,curY))
            if canIncreaseOL:
                curX += olInfo.get_width() + SMALL_MARGIN
                olUntilLevelText = FONT.render(str(olUntilLevel),1,TEXT_COLOR)
                olUntilLevelRect = pygame.Rect(
                    curX,
                    curY,
                    olUntilLevelText.get_width() + (2*SMALL_MARGIN),
                    olUntilLevelText.get_height()
                )
                pygame.draw.rect(
                    win,
                    BUTTON_HOVERED_COLOR if olUntilLevelRect.collidepoint(mousePosX,mousePosY) else BUTTON_COLOR,
                    olUntilLevelRect
                )
                win.blit(olUntilLevelText,(olUntilLevelRect.x+SMALL_MARGIN,olUntilLevelRect.y))
                if olUntilLevelRect.collidepoint(mousePosX,mousePosY):
                    curTooltip = SCROLL_TO_MODIFY
                curX += olUntilLevelRect.width + SMALL_MARGIN
                olUntilLevelResult = olUntilLevelCompleteTime(olUntilLevel)
                olUntilLevelResultText = FONT.render(
                    f": {displayTimedelta(olUntilLevelResult)} -> {displayDatetime(curTime+olUntilLevelResult)}",
                    1,
                    TEXT_COLOR
                )
                win.blit(olUntilLevelResultText,(curX,curY))
            curY += olInfo.get_height() + BIG_MARGIN

            curX = BIG_MARGIN
            shapeMultInfoStr = f"Shape Multiplier : {curSaveInfo["shapeMult"]}"
            if canIncreaseOL and (not shapeMultMaxed):
                shapeMultInfoStr += "    \u2022    Until Level"
            shapeMultInfo = FONT.render(shapeMultInfoStr,1,TEXT_COLOR)
            win.blit(shapeMultInfo,(curX,curY))
            if canIncreaseOL and (not shapeMultMaxed):
                curX += shapeMultInfo.get_width() + SMALL_MARGIN
                shapeMultUntilLevelText = FONT.render(str(shapeMultUntilLevel),1,TEXT_COLOR)
                shapeMultUntilLevelRect = pygame.Rect(
                    curX,
                    curY,
                    shapeMultUntilLevelText.get_width() + (2*SMALL_MARGIN),
                    shapeMultUntilLevelText.get_height()
                )
                pygame.draw.rect(
                    win,
                    BUTTON_HOVERED_COLOR if shapeMultUntilLevelRect.collidepoint(mousePosX,mousePosY) else BUTTON_COLOR,
                    shapeMultUntilLevelRect
                )
                win.blit(shapeMultUntilLevelText,(
                    shapeMultUntilLevelRect.x + SMALL_MARGIN,
                    shapeMultUntilLevelRect.y
                ))
                if shapeMultUntilLevelRect.collidepoint(mousePosX,mousePosY):
                    curTooltip = SCROLL_TO_MODIFY
            curY += shapeMultInfo.get_height() + BIG_MARGIN

            topPartBottom = curY

            shapeMultIcon = FONT.render(f"x{curSaveInfo["shapeMult"]}",1,TEXT_COLOR)

            goalLinesSurf:list[tuple[pygame.Surface,bool,list[tuple[int,float]]]] = []
            for goalLineIndex,goalLine in enumerate(curSaveInfo["goalLines"]):

                curShape = curShapes[goalLineIndex]

                curLines:list[pygame.Surface] = []
                curTooltipsPos = []
                activeGoalLine = goalLine["curRawRate"] != 0

                shapeAmountSurf, elemsPos = createInfoLine(
                    icons["shape"],
                    FONT.render(f"{goalLine["curAmount"]:,.0f} / {goalLine["goalAmount"]:,}",1,TEXT_COLOR)
                )
                curLines.append(shapeAmountSurf)
                curTooltipsPos.append([elemsPos[0]])

                if activeGoalLine:

                    shapeRateRawSurf, elemsPos = createInfoLine(
                        icons["beltLauncher"],
                        FONT.render(":",1,TEXT_COLOR),
                        icons["shape"],
                        FONT.render(f"{goalLine["curRawRate"]:,.0f}/min",1,TEXT_COLOR),
                        icons["spaceBelt"],
                        FONT.render(f"{goalLine["curRawSpaceBeltRate"]:.3f}",1,TEXT_COLOR)
                    )
                    curLines.append(shapeRateRawSurf)
                    curTooltipsPos.append([elemsPos[0],elemsPos[2],elemsPos[4]])

                    shapeRateMultSurf, elemsPos = createInfoLine(
                        shapeMultIcon,
                        FONT.render(":",1,TEXT_COLOR),
                        icons["shape"],
                        FONT.render(f"{goalLine["curMultRate"]:,.0f}/min",1,TEXT_COLOR),
                        icons["spaceBelt"],
                        FONT.render(f"{goalLine["curMultSpaceBeltRate"]:.3f}",1,TEXT_COLOR)
                    )
                    curLines.append(shapeRateMultSurf)
                    curTooltipsPos.append([elemsPos[0],elemsPos[2],elemsPos[4]])

                else:
                    curLines.append(FONT.render("0/min",1,TEXT_COLOR))
                    curTooltipsPos.append([])

                curLines.append(FONT.render(f"Level : {goalLine["curLevel"]}",1,TEXT_COLOR))
                curTooltipsPos.append([])

                if activeGoalLine:
                    curUntilLevel = goalLinesUntilLevel[goalLineIndex]
                    curCompleteTime = goalLineUntilLevelCompleteTime(
                        goalLineIndex,
                        curUntilLevel
                    )
                    curUntilLevelText = FONT.render(str(curUntilLevel),1,TEXT_COLOR)
                    completeTimeSurf, elemsPos = createInfoLine(
                        FONT.render("Until Level",1,TEXT_COLOR),
                        pygame.Surface((
                            curUntilLevelText.get_width() + SMALL_MARGIN,
                            curUntilLevelText.get_height() + SMALL_MARGIN
                        ),pygame.SRCALPHA),
                        FONT.render(f": {displayTimedelta(curCompleteTime)}",1,TEXT_COLOR)
                    )
                    curLines.append(completeTimeSurf)
                    curTooltipsPos.append([elemsPos[1]])

                    curLines.append(FONT.render(
                        f"-> {displayDatetime(curTime+curCompleteTime)}",
                        1,
                        TEXT_COLOR
                    ))
                    curTooltipsPos.append([])

                curGoalLineSurf = pygame.Surface((
                    curShape.get_width() + BIG_MARGIN + max(l.get_width() for l in curLines),
                    max(curShape.get_height(),sum(l.get_height() for l in curLines))
                ),pygame.SRCALPHA)

                curGoalLineSurf.blit(curShape,(0,(curGoalLineSurf.get_height()/2)-(curShape.get_height()/2)))

                curX = curShape.get_width() + BIG_MARGIN
                curY = 0
                rectifiedTooltipsPos = []
                for i,l in enumerate(curLines):
                    curGoalLineSurf.blit(l,(curX,curY))
                    rectifiedTooltipsPos.extend([(curX+p[0],curY+p[1]) for p in curTooltipsPos[i]])
                    curY += l.get_height()

                goalLinesSurf.append((curGoalLineSurf,activeGoalLine,rectifiedTooltipsPos))

            curGoalLineWidth = max(s[0].get_width() for s in goalLinesSurf) + (2*BIG_MARGIN)
            curGoalLineHeight = max(s[0].get_height() for s in goalLinesSurf) + (2*BIG_MARGIN)
            curGoalLineUntiLevelRects:list[pygame.Rect|None] = []

            for goalLineIndex,(goalLineSurf,activeGoalLine,tooltipsPos) in enumerate(goalLinesSurf):

                curX = BIG_MARGIN + ((BIG_MARGIN+curGoalLineWidth)*(goalLineIndex%NUM_GOAL_LINES_PER_ROW))
                curY = topPartBottom + ((BIG_MARGIN+curGoalLineHeight)*(goalLineIndex//NUM_GOAL_LINES_PER_ROW))

                pygame.draw.rect(win,GOAL_LINE_BG_COLOR,pygame.Rect(
                    curX,
                    curY,
                    curGoalLineWidth,
                    curGoalLineHeight,
                ),border_radius=10)

                win.blit(goalLineSurf,(curX+BIG_MARGIN,curY+BIG_MARGIN))

                tooltipRects = [pygame.Rect(
                    curX + BIG_MARGIN + p[0],
                    curY + BIG_MARGIN + p[1],
                    ICON_SIZE,
                    ICON_SIZE
                ) for p in tooltipsPos]

                if activeGoalLine:

                    tooltipRects[4].width = shapeMultIcon.get_width()
                    tooltipRects[4].height = shapeMultIcon.get_height()

                    curUntilLevelText = FONT.render(str(goalLinesUntilLevel[goalLineIndex]),1,TEXT_COLOR)
                    tooltipRects[-1].width = curUntilLevelText.get_width() + (2*SMALL_MARGIN)
                    tooltipRects[-1].height = curUntilLevelText.get_height()
                    curUntilLevelRect = tooltipRects[-1]
                    pygame.draw.rect(win,(
                        GOAL_LINE_BUTTON_HOVERED_COLOR
                        if curUntilLevelRect.collidepoint(mousePosX,mousePosY) else
                        GOAL_LINE_BUTTON_COLOR
                    ),curUntilLevelRect)
                    win.blit(curUntilLevelText,(
                        curUntilLevelRect.x + SMALL_MARGIN,
                        curUntilLevelRect.y
                    ))
                    curGoalLineUntiLevelRects.append(curUntilLevelRect)

                else:
                    curGoalLineUntiLevelRects.append(None)

                for rect,msg in zip(tooltipRects,[
                    "Shapes Delivered / Shapes Required",
                    "The raw rate of shapes delivered to the vortex",
                    "As a shapes/min throughput",
                    "As the equivalent number of full space belts",
                    "The rate of shapes actually counted, i.e. multiplied by the shape multiplier",
                    "As a shapes/min throughput",
                    "As the equivalent number of full space belts",
                    SCROLL_TO_MODIFY
                ]):
                    if rect.collidepoint(mousePosX,mousePosY):
                        curTooltip = msg

            footerText = FONT_SMALL.render(
                "Press ESC to go back; "
                f"Belt Speed Upgrade Level : {curSaveInfo["beltSpeed"]}; "
                f"Current Time : {displayDatetime(curTime)}",
                1,
                TEXT_COLOR
            )
            footerRect = pygame.Rect(
                0,
                winHeight - footerText.get_height() - (2*SMALL_MARGIN),
                winWidth,
                footerText.get_height() + (2*SMALL_MARGIN)
            )
            pygame.draw.rect(win,TOP_BAR_BG_COLOR,footerRect)
            win.blit(footerText,(SMALL_MARGIN,footerRect.y+SMALL_MARGIN))

        if curTooltip is not None:
            curTooltipText = FONT_SMALL.render(curTooltip,1,TEXT_COLOR)
            curTooltipRect = pygame.Rect(
                mousePosX,
                mousePosY + 25,
                curTooltipText.get_width() + (2*SMALL_MARGIN),
                curTooltipText.get_height() + (2*SMALL_MARGIN)
            )
            pygame.draw.rect(win,TOOLTIP_BG_COLOR,curTooltipRect)
            pygame.draw.rect(win,TEXT_COLOR,curTooltipRect,1)
            win.blit(curTooltipText,(curTooltipRect.x+SMALL_MARGIN,curTooltipRect.y+SMALL_MARGIN))

        pygame.display.update()

if __name__ == "__main__":
    main()