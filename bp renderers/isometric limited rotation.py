import pygame
CONTROLS = {
    "forward" : pygame.K_z,
    "left" : pygame.K_q,
    "backward" : pygame.K_s,
    "right" : pygame.K_d,
    "up" : pygame.K_e,
    "down" : pygame.K_a,
    "camAngle" : 0 # mouse button : 0 : left, 1 : middle, 2 : right
} # additionally : scroll wheel : zoom
import ctypes
ctypes.windll.user32.SetProcessDPIAware()
import math
class Pos:
    def __init__(self,x:int|float,y:int|float,z:int|float) -> None:
        self.x = x
        self.y = y
        self.z = z
BG_COLOR = (147,134,141)
FPS = 60
textures = []
temp = pygame.Surface((10,10))
temp.fill((255,0,0))
textures.append({"x":-1,"y":0,"z":1,"w":1,"h":1,"f":"u","surf":temp})
temp = pygame.Surface((10,10))
temp.fill((200,0,0))
textures.append({"x":-1,"y":1,"z":1,"w":1,"h":1,"f":"s","surf":temp})
temp = pygame.Surface((10,10))
temp.fill((0,255,0))
textures.append({"x":0,"y":-1,"z":1,"w":1,"h":1,"f":"u","surf":temp})
temp = pygame.Surface((10,10))
temp.fill((0,200,0))
textures.append({"x":0,"y":0,"z":1,"w":1,"h":1,"f":"s","surf":temp})
temp = pygame.Surface((10,10))
temp.fill((0,0,255))
textures.append({"x":-1,"y":-1,"z":2,"w":1,"h":1,"f":"u","surf":temp})
temp = pygame.Surface((10,10))
temp.fill((0,0,200))
textures.append({"x":-1,"y":0,"z":2,"w":1,"h":1,"f":"s","surf":temp})
camPos = Pos(0,0,0)
camAngle = 45
zoom = 1
pygame.font.init()
textFont = pygame.font.SysFont("arial",25)
clock = pygame.time.Clock()
win = pygame.display.set_mode((700,700),pygame.RESIZABLE)
run = True
while run:
    clock.tick(FPS)
    pygame.display.set_caption(f"S2 BP renderer - {clock.get_fps():.0f} FPS")
    timeDelta = clock.get_time()/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
        elif event.type == pygame.MOUSEWHEEL:
            zoom = max(zoom+((zoom/10)*-event.y),1)
        elif event.type == pygame.KEYDOWN:
            if event.key == CONTROLS["up"]:
                camPos.z += 1
            elif event.key == CONTROLS["down"]:
                camPos.z = max(camPos.z-1,0)
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[CONTROLS["camAngle"]]:
                camSpeed = event.rel[1] / 2
                camAngle = max(min(camAngle+(camSpeed),90),0)
    if not run:
        break
    pressedKeys = pygame.key.get_pressed()
    camSpeed = 2 * timeDelta * zoom
    if pressedKeys[CONTROLS["forward"]]:
        camPos.y -= camSpeed
    if pressedKeys[CONTROLS["left"]]:
        camPos.x -= camSpeed
    if pressedKeys[CONTROLS["backward"]]:
        camPos.y += camSpeed
    if pressedKeys[CONTROLS["right"]]:
        camPos.x += camSpeed
    winWidth, winHeight = win.get_size()
    win.fill(BG_COLOR)
    for texture in textures:
        x = texture["x"] - camPos.x
        y = texture["y"] - camPos.y
        z = texture["z"] - camPos.z
        px = x
        py = (y*math.sin(math.radians(camAngle))) - (z*math.cos(math.radians(camAngle)))
        px = (px*(1/zoom)*(winHeight/2)) + (winWidth/2)
        py = (py*(1/zoom)*(winHeight/2)) + (winHeight/2)
        newTexture = pygame.transform.smoothscale_by(texture["surf"],(
            (1/texture["surf"].get_width()) * texture["w"] * (1/zoom) * (winHeight/2),
            (1/texture["surf"].get_height()) * texture["h"] * (1/zoom) * (winHeight/2) * ((math.sin if texture["f"] == "u" else math.cos)(math.radians(camAngle)))
        ))
        win.blit(newTexture,(px,py))
    win.blit(textFont.render(f"{camPos.x:.3f},{camPos.y:.3f},{camPos.z:.3f}",1,(255,255,255)),(0,0))
    pygame.display.update()