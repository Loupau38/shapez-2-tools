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


# generate and print a single level

print(generator.Generate(Int32(1)).ToString())


# generate and print a range of levels

# for i in range(1,11):
#     print(f"{i} : {generator.Generate(Int32(i)).ToString()}")


# generate a range of levels and output it to a file (for statistical sampling for example)

# shapes = [generator.Generate(Int32(i)).ToString() for i in range(51,1051)]
# with open("./output.txt","w",encoding="utf-8") as f:
#     f.write("\n".join(shapes))


# find a savegame's seed by only knowing which shape it has for a specific level
# (will only work if the savegame's seed is between 0 and 99999 which is the range of seeds the game generates by default)

# shape = ""
# level = Int32(0)
# for seed in range(100_000):
#     generator.Mode.Seed = Int32(seed)
#     if generator.Generate(level).ToString() == shape:
#         print()
#         print(seed)
#         break
#     print(f"\r{str(seed).zfill(5)}/99999",end="")