# rotate a point around the origin ccw :
# x = x*cos(a) - y*sin(a)
# y = y*cos(a) + x*sin(a)

#      N
#      |
#      |  X
# W----+---->E
#      |
#      | Y
#      v
#      S

# cam rotation :
# north : 0
# east : 90
# west : -90

import pygame
import math

number = int|float

class Pos:
    def __init__(self,x:number,y:number,z:number) -> None:
        self.x = x
        self.y = y
        self.z = z

class Point:
    def __init__(self,pos:Pos,color:tuple[int,int,int]=(255,255,255)) -> None:
        self.pos = pos
        self.color = color

def rotatePos(x:number,y:number,angle:number) -> tuple[number,number]:
    angle = math.radians(angle)
    newX = (x*math.cos(angle)) - (y*math.sin(angle))
    newY = (y*math.cos(angle)) + (x*math.sin(angle))
    return newX, newY

def rotatePoint(point:Point) -> Point:
    x, y, z = point.pos.x, point.pos.y, point.pos.z
    x, y = rotatePos(x,y,-camRotation)
    y, z = rotatePos(y,z,-camAngle)
    return Point(Pos(x,y,z),point.color)

def getPXPY(point:Point) -> tuple[number,number]:
    px, py = point.pos.x, -point.pos.z
    tempScaleFactor = 50
    px, py = px*tempScaleFactor, py*tempScaleFactor
    px, py = px+(winWidth/2), py+(winHeight/2)
    return px, py

points:list[Point] = [
    Point(Pos(1,1,1),(255,0,0)),
    Point(Pos(1,1,-1)),
    Point(Pos(1,-1,1)),
    Point(Pos(1,-1,-1)),
    Point(Pos(-1,1,1)),
    Point(Pos(-1,1,-1)),
    Point(Pos(-1,-1,1)),
    Point(Pos(-1,-1,-1))
]
lines = [
    (0,1),
    (0,2),
    (0,4),
    (1,3),
    (1,5),
    (2,3),
    (2,6),
    (3,7),
    (4,5),
    (4,6),
    (5,7),
    (6,7)
]

camRotation = 0
camAngle = 0

win = pygame.display.set_mode((700,700))
clock = pygame.time.Clock()
pygame.font.init()
textFont = pygame.font.SysFont("arial",30)

run = True
while run:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
        if event.type == pygame.MOUSEMOTION and event.buttons[0]:
            camRotation = (camRotation+(event.rel[0]/2)) % 360
            camAngle = max(min(camAngle+(event.rel[1]/2),90),0)

    rotatedPoints:list[Point] = [rotatePoint(p) for p in points]

    winWidth, winHeight = win.get_size()

    win.fill((0,0,0))

    projectedPoints:list[tuple[number,number,tuple[int,int,int]]] = [tuple([*getPXPY(p),p.color]) for p in rotatedPoints]

    for point in projectedPoints:
        pygame.draw.circle(win,point[2],(point[0],point[1]),5)

    for line in lines:
        point1 = projectedPoints[line[0]]
        point2 = projectedPoints[line[1]]
        pygame.draw.line(win,(255,255,255),point1[:2],point2[:2])

    origin = getPXPY(rotatePoint(Point(Pos(0,0,0))))
    xAxis = getPXPY(rotatePoint(Point(Pos(1,0,0))))
    yAxis = getPXPY(rotatePoint(Point(Pos(0,1,0))))
    zAxis = getPXPY(rotatePoint(Point(Pos(0,0,1))))

    pygame.draw.line(win,(255,0,0),origin,xAxis)
    pygame.draw.line(win,(0,255,0),origin,yAxis)
    pygame.draw.line(win,(0,0,255),origin,zAxis)

    win.blit(textFont.render("X",1,(255,0,0)),xAxis)
    win.blit(textFont.render("Y",1,(0,255,0)),yAxis)
    win.blit(textFont.render("Z",1,(0,0,255)),zAxis)

    pygame.display.update()