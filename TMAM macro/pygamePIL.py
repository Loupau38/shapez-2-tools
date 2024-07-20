# The bot was originally developed with pygame, to convert it to using Pillow,
# I created this interface which copies the pygame functions and classes used in the bot
# to not have to change the code too much, although as a result, some functions might not be
# as efficient as if they were done with Pillow directly

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import typing
import math
import io

SRCALPHA = 65536
color = tuple[int,int,int] | tuple[int,int,int,int]
number = int | float

class error(RuntimeError): ...

class Surface:

    def __init__(self,size:tuple[number,number],flags:int=0,*,_fromImage:PIL.Image.Image|None=None) -> None:
        size = (round(size[0]),round(size[1]))
        if flags == 0:
            defaultColor = (0,0,0,255)
        elif flags == SRCALPHA:
            defaultColor = (0,0,0,0)
        else:
            raise NotImplementedError("Surface creation flags not supported")
        if _fromImage is None:
            self._image = PIL.Image.new("RGBA",size,defaultColor)
        else:
            self._image = _fromImage

    def get_width(self) -> int:
        return self._image.width

    def get_height(self) -> int:
        return self._image.height

    def get_size(self) -> tuple[int,int]:
        return self._image.size

    def get_at(self,x_y:tuple[int,int]) -> tuple[int,int,int,int]:
        return self._image.getpixel(x_y)

    def blit(self,source:typing.Self,dest:tuple[number,number]):
        dest = (round(dest[0]),round(dest[1]))
        self._image.alpha_composite(source._image,dest)

    def fill(self,color:color) -> None:
        self._image.paste(color,(0,0)+self._image.size)

    def copy(self) -> typing.Self:
        return _imgToSurf(self._image.copy())

class Rect:

    def __init__(self,left:number,top:number,width:number,height:number) -> None:
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def _toBBox(self) -> tuple[number,number,number,number]:
        return (self.left,self.top,self.left+self.width-1,self.top+self.height-1)

def _imgToSurf(img:PIL.Image.Image) -> Surface:
    return Surface((0,0),_fromImage=img)

def image_load(filename:str|io.BytesIO) -> Surface:
    try:
        image = PIL.Image.open(filename)
    except PIL.UnidentifiedImageError:
        raise error
    return _imgToSurf(image.convert("RGBA"))

def image_save(surface:Surface,filename:str|io.BytesIO,namehint:str="") -> None:
    surface._image.save(filename,None if namehint == "" else namehint)

def draw_rect(surface:Surface,color:color,rect:Rect,width:int=0,border_radius:int=-1) -> None:
    fillColor = color if width == 0 else None
    outlineColor = None if width == 0 else color
    draw = PIL.ImageDraw.Draw(surface._image)
    if border_radius < 0:
        draw.rectangle(rect._toBBox(),fillColor,outlineColor,width)
    else:
        draw.rounded_rectangle(rect._toBBox(),border_radius,fillColor,outlineColor,width)

def draw_line(surface:Surface,color:color,start_pos:tuple[number,number],end_pos:tuple[number,number],width:int=1) -> None:
    PIL.ImageDraw.Draw(surface._image).line([start_pos,end_pos],color,width)

def draw_circle(
    surface:Surface,color:color,center:tuple[number,number],radius:float,width:int=0,
    draw_top_right:bool=False,draw_top_left:bool=False,draw_bottom_left:bool=False,draw_bottom_right:bool=False
) -> None:

    draw = PIL.ImageDraw.Draw(surface._image)
    bbox = (center[0]-radius,center[1]-radius,center[0]+radius-1,center[1]+radius-1)

    if draw_top_right or draw_top_left or draw_bottom_left or draw_bottom_right:

        for quadrant,startAngle,stopAngle in [
            (draw_bottom_right,0,90),
            (draw_bottom_left,90,180),
            (draw_top_left,180,270),
            (draw_top_right,270,360)
        ]:
            if quadrant:
                draw.arc(bbox,startAngle,stopAngle,color,round(radius) if width == 0 else width)

    else:

        fillColor = color if width == 0 else None
        outlineColor = None if width == 0 else color
        draw.ellipse(bbox,fillColor,outlineColor,width)

def draw_arc(surface:Surface,color:color,rect:Rect,start_angle:float,stop_angle:float,width:int=1) -> None:
    PIL.ImageDraw.Draw(surface._image).arc(
        rect._toBBox(),
        360 - math.degrees(stop_angle),
        360 - math.degrees(start_angle),
        color,
        width
    )

def draw_polygon(surface:Surface,color:color,points:list[tuple[number,number]],width:int=0):
    draw = PIL.ImageDraw.Draw(surface._image)
    if width == 0:
        draw.polygon(points,color)
    else:
        for i,point in enumerate(points):
            draw.line([point,points[(i+1)%len(points)]],color,width)

def font_init() -> None:
    pass

class font_Font:

    def __init__(self,name:str,size:int) -> None:
        self._font = PIL.ImageFont.truetype(name,size)

    def render(self,text:str,antialias:bool|typing.Literal[0,1],color:color,background:color|None=None) -> Surface:

        if not antialias:
            raise NotImplementedError("Text rendering without antialias not supported")

        bbox = self._font.getbbox(text)

        kwargs = {}
        if background is not None:
            kwargs["color"] = color

        image = PIL.Image.new("RGBA",(bbox[2]+1,bbox[3]+1),**kwargs)
        PIL.ImageDraw.Draw(image).text((0,0),text,color,self._font)
        return _imgToSurf(image)

def transform_smoothscale(surface:Surface,size:tuple[int,int]) -> Surface:
    return _imgToSurf(surface._image.resize(size))

def transform_rotate(surface:Surface,angle:float) -> Surface:
    return _imgToSurf(surface._image.rotate(angle,expand=True))

class mask_Mask:

    def __init__(self,_image:PIL.Image.Image) -> None:
        self._image = _image

    def to_surface(self,surface:Surface,setsurface:Surface,unsetcolor:None) -> None:
        surface._image.paste(setsurface._image,(0,0),self._image)

def mask_from_surface(surface:Surface,treshold:int=127) -> mask_Mask:
    return mask_Mask(surface._image.getchannel("A").point(lambda x: 1 if x > treshold else 0,"1"))