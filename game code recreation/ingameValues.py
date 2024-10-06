import otherClasses
from fixedint import Int32

CIRCLE_SHAPE_PART = otherClasses.IShapeSubPart("C",False,True,True)
SQUARE_SHAPE_PART = otherClasses.IShapeSubPart("R",False,True,True)
STAR_SHAPE_PART = otherClasses.IShapeSubPart("S",False,True,True)
DIAMOND_SHAPE_PART = otherClasses.IShapeSubPart("W",False,True,True)
HEXAGON_SHAPE_PART = otherClasses.IShapeSubPart("H",False,True,True)
FLOWER_SHAPE_PART = otherClasses.IShapeSubPart("F",False,True,True)
GEAR_SHAPE_PART = otherClasses.IShapeSubPart("G",False,True,True)
PIN_SHAPE_PART = otherClasses.IShapeSubPart("P",False,False,False)
CRYSTAL_SHAPE_PART = otherClasses.IShapeSubPart("c",True,True,False)

QUAD_SHAPES_CONFIG = otherClasses.IShapesConfiguration(
    Int32(4),
    CRYSTAL_SHAPE_PART,
    PIN_SHAPE_PART,
    [CIRCLE_SHAPE_PART,SQUARE_SHAPE_PART,STAR_SHAPE_PART,DIAMOND_SHAPE_PART,PIN_SHAPE_PART,CRYSTAL_SHAPE_PART],
    [DIAMOND_SHAPE_PART],
    [STAR_SHAPE_PART],
    [CIRCLE_SHAPE_PART,SQUARE_SHAPE_PART]
)
HEX_SHAPES_CONFIG = otherClasses.IShapesConfiguration(
    Int32(6),
    CRYSTAL_SHAPE_PART,
    PIN_SHAPE_PART,
    [HEXAGON_SHAPE_PART,FLOWER_SHAPE_PART,GEAR_SHAPE_PART,PIN_SHAPE_PART,CRYSTAL_SHAPE_PART],
    [FLOWER_SHAPE_PART],
    [GEAR_SHAPE_PART],
    [HEXAGON_SHAPE_PART]
)

COLOR_SCHEME = otherClasses.IShapeColorScheme(
    [otherClasses.IShapeColor("r"),otherClasses.IShapeColor("g"),otherClasses.IShapeColor("b")],
    [otherClasses.IShapeColor("c"),otherClasses.IShapeColor("m"),otherClasses.IShapeColor("y")],
    [otherClasses.IShapeColor("w")],
    otherClasses.IShapeColor("u")
)