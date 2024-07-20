import ctypes
ctypes.windll.user32.SetProcessDPIAware()
from PIL import ImageGrab
import time
import pynput
import pygame
import blueprints
import gameInfos
import utils

# positions on the screen
READ_COMPLETED = (680,900)
CLICK_COMPLETED = (750,990)
CLICK_SHAPE = (570,920)
CLICK_COPY_SHAPE_CODE = (680,230)
CLICK_PLACE_BP = (975,555)

DELAY_BETWEEN_INPUTS = 0.2
CHECK_DELAY = 0.1
COMPLETED_COLOR = (41,192,100)
COMPLETED_COLOR_DIFF = 20
OL_KEY = "t"
CLOSE_KEY = pynput.keyboard.Key.esc
PASTE_BP_KEY = "v"
PASTE_BP_KEY_MOD = pynput.keyboard.Key.ctrl

pygame.display.set_mode((100,100))
pygame.scrap.init()

mouse = pynput.mouse.Controller()
keyboard = pynput.keyboard.Controller()

def on_press(key):
    global stop
    if key == pynput.keyboard.Key.alt_l:
        stop = True
stop = False
listener = pynput.keyboard.Listener(
    on_press=on_press)
listener.start()

def clickAt(pos:tuple[int,int]) -> None:
    mouse.position = pos
    time.sleep(0.1)
    mouse.click(pynput.mouse.Button.left)

itemProducerPos = []
for z in range(3):
    for n in range(-6,6):
        itemProducerPos.append((n,-11,z,1))
        itemProducerPos.append((n,10,z,3))
        itemProducerPos.append((-11,n,z,0))
        itemProducerPos.append((10,n,z,2))

def genBP() -> None:

    shapeCode = pygame.scrap.get(pygame.SCRAP_TEXT).strip(b"\x00").decode()

    bp = blueprints.Blueprint(
        gameInfos.versions.LATEST_MAJOR_VERSION,
        gameInfos.versions.LATEST_GAME_VERSION,
        blueprints.BUILDING_BP_TYPE,
        blueprints.BuildingBlueprint(
            [
                blueprints.BuildingEntry(
                    utils.Pos(*pos[0:3]),
                    utils.Rotation(pos[3]),
                    gameInfos.buildings.allBuildings["SandboxItemProducerDefaultInternalVariant"],
                    {"type":"shape","value":shapeCode}
                ) for pos in itemProducerPos
            ],
            blueprints.getDefaultBlueprintIcons(blueprints.BUILDING_BP_TYPE),
            gameInfos.versions.LATEST_GAME_VERSION
        )
    )

    encoded = blueprints.encodeBlueprint(bp)
    pygame.scrap.put(pygame.SCRAP_TEXT,encoded.encode())

time.sleep(3)

while not stop:

    time.sleep(CHECK_DELAY)

    screen = ImageGrab.grab().load()
    color = screen[*READ_COMPLETED]

    diffs = []
    for i in range(3):
        diffs.append(abs(color[i]-COMPLETED_COLOR[i]))
    diff = sum(diffs) / 3
    if diff > COMPLETED_COLOR_DIFF:
        continue

    # complete the current goal and get the next one
    clickAt(CLICK_COMPLETED)
    time.sleep(DELAY_BETWEEN_INPUTS)
    clickAt(CLICK_SHAPE)
    time.sleep(DELAY_BETWEEN_INPUTS)
    clickAt(CLICK_COPY_SHAPE_CODE)
    time.sleep(DELAY_BETWEEN_INPUTS)

    # exit menus to main game
    keyboard.tap(CLOSE_KEY)
    time.sleep(DELAY_BETWEEN_INPUTS)
    keyboard.tap(CLOSE_KEY)
    time.sleep(DELAY_BETWEEN_INPUTS)

    genBP()

    # paste bp
    keyboard.press(PASTE_BP_KEY_MOD)
    keyboard.tap(PASTE_BP_KEY)
    keyboard.release(PASTE_BP_KEY_MOD)
    time.sleep(DELAY_BETWEEN_INPUTS)
    time.sleep(5) # the game freezes after the bp is pasted, if that doesn't happen then that line can be removed
    clickAt(CLICK_PLACE_BP)
    time.sleep(DELAY_BETWEEN_INPUTS)

    # deselect bp
    mouse.click(pynput.mouse.Button.right)
    time.sleep(DELAY_BETWEEN_INPUTS)

    # go back in operator level screen
    keyboard.tap(OL_KEY)
    time.sleep(DELAY_BETWEEN_INPUTS)