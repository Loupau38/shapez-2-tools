import base64
import pygame

SET_DPI_AWARE = True
FPS = 60

pygame.font.init()
BUTTONS_FONT = pygame.font.SysFont("arial",30)
BYTES_FONT = pygame.font.SysFont("arial",25)
REMOVE_BYTE_FONT = pygame.font.SysFont("arial",15)

BUTTONS_PADDING = 5
BUTTONS_MARGIN = 10
BYTES_MARGIN = 5
BYTES_ELEMS_PADDING = 5
BYTES_BIN_PADDING = 2
REMOVE_BYTE_BUTTON_PADDING = 2

BG_COLOR = (50,50,50)
ELEM_COLOR = (75,75,75)
HIGHLIGHTED_COLOR = (127,127,127)
TEXT_COLOR = (255,255,255)
REMOVE_BYTE_BUTTON_COLOR = (255,0,0)

def isAscii(byte:int) -> bool:
    if byte > 127:
        return False
    return chr(byte).isprintable()

def maxSurfSize(surfList:list[pygame.Surface]) -> tuple[int,int]:
    return max(s.get_width() for s in surfList), max(s.get_height() for s in surfList)

def blitCenteredInRect(blitTo:pygame.Surface,blitFrom:pygame.Surface,rect:pygame.Rect) -> None:
    blitTo.blit(blitFrom,(
        rect.left + ((rect.width/2)-(blitFrom.get_width()/2)),
        rect.top + ((rect.height/2)-(blitFrom.get_height()/2))
    ))

def main() -> None:

    if SET_DPI_AWARE:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()

    win = pygame.display.set_mode((700,700),pygame.RESIZABLE)

    pygame.scrap.init()
    clock = pygame.time.Clock()

    getFromClipBoardText = BUTTONS_FONT.render("Get from clipboard",1,TEXT_COLOR)
    copyToClipBoardText = BUTTONS_FONT.render("Copy to clipboard",1,TEXT_COLOR)
    addByteText = BYTES_FONT.render("+",1,TEXT_COLOR)
    removeByteText = REMOVE_BYTE_FONT.render("X",1,TEXT_COLOR)

    run = True
    curBytes:list[int] = []

    while run:

        clock.tick(FPS)
        pygame.display.set_caption(f"Base64 encoded bytes editor | {clock.get_fps():.0f} fps")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if getFromClipBoardButton.collidepoint(*event.pos):
                    try:
                        curBytes = [b for b in base64.b64decode(pygame.scrap.get(pygame.SCRAP_TEXT))]
                    except Exception:
                        print("Couldn't get from clipboard")
                elif copyToClipBoardButton.collidepoint(*event.pos):
                    try:
                        pygame.scrap.put(pygame.SCRAP_TEXT,base64.b64encode(bytes(curBytes)))
                    except Exception:
                        print("Couldn't copy to clipboard")
                elif curAddByteBox.collidepoint(*event.pos):
                    curBytes.append(0)
                elif (curRemoveByteButton is not None) and (curRemoveByteButton.collidepoint(*event.pos)):
                    curBytes.pop(curRemoveByteIndex)
                else:
                    for i,curBinRow in enumerate(renderedBinsBox):
                        for i2,curBinBox in enumerate(curBinRow):
                            if curBinBox.collidepoint(*event.pos):
                                bitValue = 2 ** (7-i2)
                                bitState = (curBytes[i] & bitValue) != 0
                                if bitState:
                                    curBytes[i] -= bitValue
                                else:
                                    curBytes[i] += bitValue
            elif event.type == pygame.MOUSEWHEEL:
                for i,curIntBox in enumerate(renderedIntsBox):
                    if curIntBox.collidepoint(*mousePos):
                        curBytes[i] = max(0,min(255,(curBytes[i]+event.y)))
            elif event.type == pygame.KEYDOWN:
                for i,curCharBox in enumerate(renderedCharsBox):
                    if curCharBox.collidepoint(*mousePos) and (event.unicode != "") and isAscii(keyOrd:=ord(event.unicode)):
                        curBytes[i] = keyOrd

        winWidth, winHeight = win.get_size()
        mousePos = pygame.mouse.get_pos()

        getFromClipBoardButtonWidth = getFromClipBoardText.get_width() + (2*BUTTONS_PADDING)
        getFromClipBoardButtonHeight = getFromClipBoardText.get_height() + (2*BUTTONS_PADDING)
        getFromClipBoardButton = pygame.Rect(
            (winWidth/2) - (getFromClipBoardButtonWidth/2),
            BUTTONS_MARGIN,
            getFromClipBoardButtonWidth,
            getFromClipBoardButtonHeight
        )

        copyToClipBoardButtonWidth = copyToClipBoardText.get_width() + (2*BUTTONS_PADDING)
        copyToClipBoardButtonHeight = copyToClipBoardText.get_height() + (2*BUTTONS_PADDING)
        copyToClipBoardButton = pygame.Rect(
            (winWidth/2) - (copyToClipBoardButtonWidth/2),
            winHeight - BUTTONS_MARGIN - copyToClipBoardButtonHeight,
            copyToClipBoardButtonWidth,
            copyToClipBoardButtonHeight
        )

        curRemoveByteButton = None
        curRemoveByteIndex = None

        bytesAreaTop = getFromClipBoardButton.bottom + BUTTONS_MARGIN
        bytesAreaBottom = copyToClipBoardButton.top - BUTTONS_MARGIN

        renderedCharsSurf:list[pygame.Surface] = []
        renderedHexsSurf:list[pygame.Surface] = []
        renderedIntsSurf:list[pygame.Surface] = []
        renderedBinsSurf:list[list[pygame.Surface]] = []

        for byte in curBytes:

            curByteChar = BYTES_FONT.render(chr(byte) if isAscii(byte) else " ",1,TEXT_COLOR)
            renderedCharsSurf.append(curByteChar)

            curByteHex = BYTES_FONT.render(hex(byte)[2:].zfill(2),1,TEXT_COLOR)
            curByteInt = BYTES_FONT.render(str(byte).zfill(3),1,TEXT_COLOR)
            renderedHexsSurf.append(curByteHex)
            renderedIntsSurf.append(curByteInt)

            renderedBinsSurf.append([])
            for char in bin(byte)[2:].zfill(8):
                charText = BYTES_FONT.render(char,1,TEXT_COLOR)
                renderedBinsSurf[-1].append(charText)

        if len(curBytes) == 0:
            byteBoxMaxWidth = addByteText.get_width() + (2*BYTES_ELEMS_PADDING)
            byteBoxMaxHeight = addByteText.get_height() + (2*BYTES_ELEMS_PADDING)
        else:
            byteCharSurfMaxWidth, byteCharSurfMaxHeight = maxSurfSize(renderedCharsSurf)
            byteHexSurfMaxWidth, byteHexSurfMaxHeight = maxSurfSize(renderedHexsSurf)
            byteIntSurfMaxWidth, byteIntSurfMaxHeight = maxSurfSize(renderedIntsSurf)
            allRenderedBinsSurf:list[pygame.Surface] = []
            for list_ in renderedBinsSurf:
                allRenderedBinsSurf.extend(list_)
            byteBinSurfMaxWidth, byteBinSurfMaxHeight = maxSurfSize(allRenderedBinsSurf)
            byteBoxMaxWidth = (
                BYTES_ELEMS_PADDING
                + byteCharSurfMaxWidth
                + (2*BYTES_ELEMS_PADDING)
                + byteHexSurfMaxWidth
                + (2*BYTES_ELEMS_PADDING)
                + byteIntSurfMaxWidth
                + (2*BYTES_ELEMS_PADDING)
                + (8*byteBinSurfMaxWidth) + (16*BYTES_BIN_PADDING)
                + BYTES_ELEMS_PADDING
            )
            byteBoxMaxHeight = max(
                byteCharSurfMaxHeight,
                byteHexSurfMaxHeight,
                byteIntSurfMaxHeight,
                byteBinSurfMaxHeight
            ) + (2*BYTES_ELEMS_PADDING)

        renderedBytesBox:list[pygame.Rect] = []
        renderedCharsBox:list[pygame.Rect] = []
        renderedIntsBox:list[pygame.Rect] = []
        renderedBinsBox:list[list[pygame.Rect]] = []

        curX = BYTES_MARGIN
        curY = bytesAreaTop
        for i,byte in enumerate(curBytes+[None]):

            if curY+BYTES_MARGIN+byteBoxMaxHeight > bytesAreaBottom:
                curX += byteBoxMaxWidth + BYTES_MARGIN
                curY = bytesAreaTop

            if byte is None:
                curAddByteBox = pygame.Rect(curX,curY,byteBoxMaxWidth,byteBoxMaxHeight)
            else:

                curByteBox = pygame.Rect(curX,curY,byteBoxMaxWidth,byteBoxMaxHeight)
                renderedBytesBox.append(curByteBox)
                if curByteBox.collidepoint(*mousePos):
                    curRemoveByteButton = pygame.Rect(
                        curByteBox.right - removeByteText.get_width() - (2*REMOVE_BYTE_BUTTON_PADDING),
                        curByteBox.top,
                        removeByteText.get_width() + (2*REMOVE_BYTE_BUTTON_PADDING),
                        removeByteText.get_height()
                    )
                    curRemoveByteIndex = i

                curCurX = curX

                curByteCharBox = pygame.Rect(curCurX,curY,
                    byteCharSurfMaxWidth + (2*BYTES_ELEMS_PADDING),
                    byteCharSurfMaxHeight + (2*BYTES_ELEMS_PADDING)
                )
                renderedCharsBox.append(curByteCharBox)
                curCurX += curByteCharBox.width

                curByteIntBox = pygame.Rect(curCurX,curY,
                    byteHexSurfMaxWidth + byteIntSurfMaxWidth + (4*BYTES_ELEMS_PADDING),
                    max(byteHexSurfMaxHeight,byteIntSurfMaxHeight) + (2*BYTES_ELEMS_PADDING)
                )
                renderedIntsBox.append(curByteIntBox)
                curCurX += curByteIntBox.width

                curCurX += BYTES_ELEMS_PADDING
                renderedBinsBox.append([])
                for _ in range(8):
                    curByteBinBox = pygame.Rect(curCurX,curY,
                        byteBinSurfMaxWidth + (2*BYTES_BIN_PADDING),
                        byteBinSurfMaxHeight + (2*BYTES_ELEMS_PADDING)
                    )
                    renderedBinsBox[-1].append(curByteBinBox)
                    curCurX += curByteBinBox.width

                curY += byteBoxMaxHeight + BYTES_MARGIN

        getFromClipBoardButtonHighLighted = getFromClipBoardButton.collidepoint(*mousePos)
        copyToClipBoardButtonHighLighted = copyToClipBoardButton.collidepoint(*mousePos)
        curAddByteBoxHighlighted = curAddByteBox.collidepoint(*mousePos)

        curCharBoxHighlighted:list[bool] = []
        curIntBoxHighlighted:list[bool] = []
        curBinBoxHighlighted:list[list[bool]] = []
        for i,_ in enumerate(renderedBytesBox):
            if curRemoveByteButton is None:
                curRemoveByteButtonHighlighted = False
            else:
                curRemoveByteButtonHighlighted = curRemoveByteButton.collidepoint(*mousePos)
            curCharBoxHighlighted.append(renderedCharsBox[i].collidepoint(*mousePos))
            curIntBoxHighlighted.append(renderedIntsBox[i].collidepoint(*mousePos))
            curBinBoxHighlighted.append([])
            for curBinBox in renderedBinsBox[i]:
                if curRemoveByteButtonHighlighted:
                    curBinBoxHighlighted[-1].append(False)
                else:
                    curBinBoxHighlighted[-1].append(curBinBox.collidepoint(*mousePos))

        win.fill(BG_COLOR)

        win.blit(BYTES_FONT.render(f"{len(curBytes)} bytes",1,TEXT_COLOR),(0,0))

        pygame.draw.rect(
            win,
            HIGHLIGHTED_COLOR if getFromClipBoardButtonHighLighted else ELEM_COLOR,
            getFromClipBoardButton
        )
        win.blit(getFromClipBoardText,(
            getFromClipBoardButton.left+BUTTONS_PADDING,
            getFromClipBoardButton.top+BUTTONS_PADDING
        ))
        pygame.draw.rect(
            win,
            HIGHLIGHTED_COLOR if copyToClipBoardButtonHighLighted else ELEM_COLOR,
            copyToClipBoardButton
        )
        win.blit(copyToClipBoardText,(
            copyToClipBoardButton.left+BUTTONS_PADDING,
            copyToClipBoardButton.top+BUTTONS_PADDING
        ))

        for i,byteBox in enumerate(renderedBytesBox+[None]):

            if byteBox is None:
                pygame.draw.rect(
                    win,
                    HIGHLIGHTED_COLOR if curAddByteBoxHighlighted else ELEM_COLOR,
                    curAddByteBox
                )
                win.blit(addByteText,(
                    curAddByteBox.left + ((curAddByteBox.width/2)-(addByteText.get_width()/2)),
                    curAddByteBox.top + ((curAddByteBox.height/2)-(addByteText.get_height()/2))
                ))

            else:

                pygame.draw.rect(win,ELEM_COLOR,byteBox)
                curCharBox = renderedCharsBox[i]
                if curCharBoxHighlighted[i]:
                    pygame.draw.rect(win,HIGHLIGHTED_COLOR,curCharBox)
                blitCenteredInRect(win,renderedCharsSurf[i],curCharBox)
                curIntBox = renderedIntsBox[i]
                curHexSurf = renderedHexsSurf[i]
                if curIntBoxHighlighted[i]:
                    pygame.draw.rect(win,HIGHLIGHTED_COLOR,curIntBox)
                blitCenteredInRect(win,curHexSurf,pygame.Rect(
                    curIntBox.left,
                    curIntBox.top,
                    byteHexSurfMaxWidth + (2*BYTES_ELEMS_PADDING),
                    curIntBox.height
                ))
                blitCenteredInRect(win,renderedIntsSurf[i],pygame.Rect(
                    curIntBox.left + byteHexSurfMaxWidth + (2*BYTES_ELEMS_PADDING),
                    curIntBox.top,
                    byteIntSurfMaxWidth + (2*BYTES_ELEMS_PADDING),
                    curIntBox.height
                ))
                for i2,curBinBox in enumerate(renderedBinsBox[i]):
                    if curBinBoxHighlighted[i][i2]:
                        pygame.draw.rect(win,HIGHLIGHTED_COLOR,curBinBox)
                    blitCenteredInRect(win,renderedBinsSurf[i][i2],curBinBox)

        if curRemoveByteButton is not None:
            pygame.draw.rect(
                win,
                REMOVE_BYTE_BUTTON_COLOR if curRemoveByteButtonHighlighted else ELEM_COLOR,
                curRemoveByteButton
            )
            blitCenteredInRect(win,removeByteText,curRemoveByteButton)

        pygame.display.update()

if __name__ == "__main__":
    main()