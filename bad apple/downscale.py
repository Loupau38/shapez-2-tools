import math
import time
OG_PATH = "./original"
DS_PATH = "./downscaled"
OG_WIDTH, OG_HEIGHT = 480, 360
DS_WIDTH, DS_HEIGHT = 64, 48
DS_RATIO = 7.5
OG_FPS = 30
DS_FPS = 3
DS_FPS_RATIO = 10
NUM_FRAMES = 6572
OG_FRAME_SIZE = math.ceil((OG_WIDTH*OG_HEIGHT)/8)

pixelSizeIsIntEvery = round(1/(DS_RATIO-math.floor(DS_RATIO)))

open(DS_PATH,"wb").close()
with open(OG_PATH,"rb") as f:
    for frameIndex in range(NUM_FRAMES):

        curOGFrame = f.read(OG_FRAME_SIZE)
        if frameIndex % DS_FPS_RATIO != 0:
            continue

        timeStart = time.perf_counter()

        curOGFrameBoolList:list[bool] = []
        for curByte in curOGFrame:
            curBitValue = 128
            for _ in range(8):
                curOGFrameBoolList.append((curByte & curBitValue) != 0)
                curBitValue >>= 1 # divide by 2

        curDSFrameBoolList:list[bool] = []
        curOGPixelY = 0
        for y in range(DS_HEIGHT):
            curOGPixelX = 0
            curDSPixelHeight = (math.ceil if y%pixelSizeIsIntEvery == 0 else math.floor)(DS_RATIO)
            for x in range(DS_WIDTH):
                curDSPixelWidth = (math.ceil if x%pixelSizeIsIntEvery == 0 else math.floor)(DS_RATIO)
                curPixels = []
                for yOffset in range(curDSPixelHeight):
                    for xOffset in range(curDSPixelWidth):
                        curPixels.append(curOGFrameBoolList[((curOGPixelY+yOffset)*OG_WIDTH)+(curOGPixelX+xOffset)])
                curColor = (sum(curPixels)/len(curPixels)) >= 0.5
                curDSFrameBoolList.append(curColor)
                curOGPixelX += curDSPixelWidth
            curOGPixelY += curDSPixelHeight

        curDSFrameByteList:list[bytes] = []
        for i in range(math.ceil(len(curDSFrameBoolList)/8)):
            curChunk = curDSFrameBoolList[i*8:(i+1)*8]
            curBitValue = 128
            curByte = 0
            for curBit in curChunk:
                if curBit:
                    curByte += curBitValue
                curBitValue >>= 1 # divide by 2
            curDSFrameByteList.append(bytes([curByte]))
        with open(DS_PATH,"ab") as f2:
            f2.write(b"".join(curDSFrameByteList))

        timeEnd = time.perf_counter()
        frameTime = timeEnd - timeStart
        numFramesLeft = (NUM_FRAMES/DS_FPS_RATIO) - ((frameIndex)/DS_FPS_RATIO)
        print(f"ETA : {(numFramesLeft*frameTime)/60:.3f}min | frame {((frameIndex)/DS_FPS_RATIO)-1}/{(NUM_FRAMES/DS_FPS_RATIO)-1}")