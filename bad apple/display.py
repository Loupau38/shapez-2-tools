import pygame
import math
FILE_PATH = "./downscaled"
WIDTH, HEIGHT = 64, 48
FRAME_SIZE = WIDTH * HEIGHT
FRAME_SIZE_BYTES = math.ceil(FRAME_SIZE/8)

win = pygame.display.set_mode((WIDTH,HEIGHT),pygame.SCALED,vsync=1)
pygame.mixer.init()
audio = pygame.mixer.Sound("./audio.mp3")
audioChannel = pygame.mixer.Channel(0)
skipFramesCounter = 0

run = True
paused = False
audioChannel.play(audio)
with open(FILE_PATH,"rb") as f:
    while run:
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = not paused
                if paused:
                    audioChannel.pause()
                else:
                    audioChannel.unpause()

        skipFramesCounter += 1
        if skipFramesCounter == 20:
            skipFramesCounter = 0
        if skipFramesCounter != 0:
            continue
        if paused:
            continue


        curFrameRaw = f.read(FRAME_SIZE_BYTES)
        if len(curFrameRaw) != FRAME_SIZE_BYTES:
            break

        curFrameBoolList:list[bool] = []
        for curByte in curFrameRaw:
            curBitValue = 128
            for _ in range(8):
                curFrameBoolList.append((curByte & curBitValue) != 0)
                curBitValue >>= 1 # divide by 2
        curFrameBytes = b"".join(bytes([255,255,255]) if p else bytes([0,0,0]) for p in curFrameBoolList)
        curFrameSurf = pygame.image.frombytes(curFrameBytes,(WIDTH,HEIGHT),"RGB")
        win.blit(curFrameSurf,(0,0))