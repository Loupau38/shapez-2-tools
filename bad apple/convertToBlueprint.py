import math
import blueprints
from gameInfos import buildings, versions
import utils
import typing

INPUT_PATH = "./downscaled"
OUTPUT_PATH = "./bad apple.spz2bp"
WIDTH, HEIGHT = 64, 48
FRAME_SIZE = WIDTH * HEIGHT
FRAME_SIZE_BYTES = math.ceil(FRAME_SIZE/8)
ON_QUAD = "Rw"
OFF_QUAD = "Rk"

def arrayToShapeArray(array:list[list[typing.Any]],conversionTable:dict[typing.Any,str]) -> list[list[str]]:
    shapeArray:list[list[str]] = []
    for y in range(int(len(array)/2)):
        shapeArray.append([])
        for x in range(int(len(array[0])/2)):
            shapeArray[-1].append("".join(conversionTable[array[(y*2)+y2][(x*2)+x2]] for y2,x2 in ((0,1),(1,1),(1,0),(0,0))))
    return shapeArray

blueprint:list[blueprints.BuildingEntry] = []
frameIndex = 0

with open(INPUT_PATH,"rb") as f:
    while True:
        curFrame = f.read(FRAME_SIZE_BYTES)
        if len(curFrame) != FRAME_SIZE_BYTES:
            break

        curFrameBoolList = []
        for curByte in curFrame:
            curBitValue = 128
            for _ in range(8):
                curFrameBoolList.append((curByte & curBitValue) != 0)
                curBitValue >>= 1 # divide by 2
        curFrameBoolList:list[list[bool]] = [curFrameBoolList[y*WIDTH:(y+1)*WIDTH] for y in range(HEIGHT)]

        curShapeArray = arrayToShapeArray(curFrameBoolList,{False:OFF_QUAD,True:ON_QUAD})

        for i in range(int(len(curShapeArray)/3)):
            for i2 in range(3):

                xPos = frameIndex // 2
                xPos += (xPos//46) * 14
                yPos = i * 5
                if frameIndex%2 == 1:
                    yPos += 4
                if i > 3:
                    yPos += 14
                zPos = 2 - i2
                rot = 3 if frameIndex%2 == 1 else 1
                shape = ":".join(curShapeArray[(i*3)+i2])
                blueprint.append(blueprints.BuildingEntry(
                    utils.Pos(
                        xPos,
                        yPos,
                        zPos
                    ),
                    utils.Rotation(rot),
                    buildings.allBuildings["SandboxItemProducerDefaultInternalVariant"],
                    {"type":"shape","value":shape}
                ))

        frameIndex += 1

encodedBP = blueprints.encodeBlueprint(blueprints.Blueprint(
    versions.LATEST_MAJOR_VERSION,versions.LATEST_GAME_VERSION,blueprints.BUILDING_BP_TYPE,
    blueprints.BuildingBlueprint(blueprint)
))
with open(OUTPUT_PATH,"w") as f:
    f.write(encodedBP)