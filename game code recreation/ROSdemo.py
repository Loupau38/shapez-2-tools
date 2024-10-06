import RandomResearchShapeGenerator
import ingameValues
import otherClasses
from fixedint import Int32

SHAPES_CONFIG = ingameValues.QUAD_SHAPES_CONFIG
MAX_SHAPE_LAYERS = 4
SEED = 0 # the savegame's seed
CRYSTALS = False

generator = RandomResearchShapeGenerator.RandomResearchShapeGenerator(
    otherClasses.GameMode(
        SHAPES_CONFIG,
        ingameValues.COLOR_SCHEME,
        Int32(SEED),
        Int32(MAX_SHAPE_LAYERS)
    ),
    otherClasses.ShapeRegistry(Int32(MAX_SHAPE_LAYERS)),
    CRYSTALS
)

# Note : the level to provide is for which level the shape will unlock, so +1 from the level displayed under it ingame (which is the current level)

print(generator.Generate(Int32(1)).ToString())

# for i in range(1,11):
#     print(f"{i} : {generator.Generate(Int32(i)).ToString()}")

# shapes = [generator.Generate(Int32(i)).ToString() for i in range(51,1051)]
# with open("./output.txt","w",encoding="utf-8") as f:
#     f.write(",".join(shapes))