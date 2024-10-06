import shapeOperations
from fixedint import Int32
import enum
from dataclasses import dataclass

# Loupau note : Ingame this class is in MapShapeGenerator.cs, moved here because it wouldn't work with python type annotations
class MapShapeGenerationType(enum.Enum):
    UncoloredHalfShape = 0
    UncoloredAlmostFullShape = 1
    UncoloredFullShape = 2
    UncoloredFullShapePure = 3
    PrimaryColorHalfShape = 4
    PrimaryColorAlmostFullShape = 5
    PrimaryColorFullShape = 6
    PrimaryColorFullShapePure = 7
    SecondaryColorHalfShape = 8
    SecondaryColorAlmostFullShape = 9
    SecondaryColorFullShape = 10
    SecondaryColorFullShapePure = 11
    TertiaryColorHalfShape = 12
    TertiaryColorAlmostFullShape = 13
    TertiaryColorFullShape = 14
    TertiaryColorFullShapePure = 15

@dataclass
class MapGenerationShapeLikeliness:
    GenerationType:MapShapeGenerationType
    MinimumDistanceToOrigin:Int32
    LikelinessPerMille:Int32

class MapGenerationParameters:

    @dataclass
    class SerializedData:
        FluidsSpawnPrimaryColors:bool = True
        FluidsSpawnSecondaryColors:bool = False
        FluidsSpawnTertiaryColors:bool = False
        FluidPatchLikelinessPercent:Int32 = Int32(15)
        FluidPatchBaseSize:Int32 = Int32(2)
        FluidPatchSizeGrowPercentPerChunk:Int32 = Int32(70)
        FluidPatchMaxSize:Int32 = Int32(4)
        ShapePatchLikelinessPercent:Int32 = Int32(30)
        ShapePatchBaseSize:Int32 = Int32(2)
        ShapePatchSizeGrowPercentPerChunk:Int32 = Int32(70)
        ShapePatchMaxSize:Int32 = Int32(5)
        ShapePatchShapeColorfulnessPercent:Int32 = Int32(50)
        ShapePatchRareShapeLikelinessPercent:Int32 = Int32(30)
        ShapePatchVeryRareShapeLikelinessPercent:Int32 = Int32(10)
        ShapePatchGenerationLikeliness:list[MapGenerationShapeLikeliness] = None

    def __init__(self,data:SerializedData) -> None:
        self.FluidsSpawnPrimaryColors = data.FluidsSpawnPrimaryColors
        self.FluidsSpawnSecondaryColors = data.FluidsSpawnSecondaryColors
        self.FluidsSpawnTertiaryColors = data.FluidsSpawnTertiaryColors
        self.FluidPatchLikelinessPercent = data.FluidPatchLikelinessPercent
        self.FluidPatchBaseSize = data.FluidPatchBaseSize
        self.FluidPatchSizeGrowPercentPerChunk = data.FluidPatchSizeGrowPercentPerChunk
        self.FluidPatchMaxSize = data.FluidPatchMaxSize
        self.ShapePatchLikelinessPercent = data.ShapePatchLikelinessPercent
        self.ShapePatchBaseSize = data.ShapePatchBaseSize
        self.ShapePatchSizeGrowPercentPerChunk = data.ShapePatchSizeGrowPercentPerChunk
        self.ShapePatchMaxSize = data.ShapePatchMaxSize
        self.ShapePatchRareShapeLikelinessPercent = data.ShapePatchRareShapeLikelinessPercent
        self.ShapePatchVeryRareShapeLikelinessPercent = data.ShapePatchVeryRareShapeLikelinessPercent
        self.ShapePatchShapeColorfulnessPercent = data.ShapePatchShapeColorfulnessPercent
        self.ShapePatchGenerationLikeliness = data.ShapePatchGenerationLikeliness.copy()

@dataclass
class IShapeSubPart:
    Code:str
    DestroyOnFallDown:bool
    AllowColor:bool
    AllowChangingColor:bool

@dataclass
class IShapesConfiguration:
    PartCount:Int32
    CrystalShapePart:IShapeSubPart
    PinShapePart:IShapeSubPart
    Parts:list[IShapeSubPart]
    MapGenerationVeryRareParts:list[IShapeSubPart]
    MapGenerationRareParts:list[IShapeSubPart]
    MapGenerationCommonParts:list[IShapeSubPart]

@dataclass
class IShapeColor:
    Code:str

class IShapeColorScheme:
    def __init__(
        self,
        PrimaryColors:list[IShapeColor],
        SecondaryColors:list[IShapeColor],
        TertiaryColors:list[IShapeColor],
        DefaultShapeColor:IShapeColor
    ) -> None:
        self.PrimaryColors = PrimaryColors
        self.SecondaryColors = SecondaryColors
        self.TertiaryColors = TertiaryColors
        self.DefaultShapeColor = DefaultShapeColor
        self.Colors = PrimaryColors + SecondaryColors + TertiaryColors + [DefaultShapeColor]

@dataclass
class ShapePart:
    Shape:IShapeSubPart|None
    Color:IShapeColor|None

    def ToString(self) -> str:
        return f"{'-' if self.Shape is None else self.Shape.Code}{'-' if self.Color is None else self.Color.Code}"

@dataclass
class ShapeLayer:
    Parts:list[ShapePart]

    def ToString(self) -> str:
        return "".join(p.ToString() for p in self.Parts)

@dataclass
class ShapeDefinition:
    Layers:list[ShapeLayer]

    def ToString(self) -> str:
        result = ""
        for i,layer in enumerate(self.Layers):
            if i != 0:
                result += ":"
            result += layer.ToString()
        return result

    def IsEmpty(self) -> bool:
        return _gameShapeToPyShape(self).isEmpty()

def _gameShapeToPyShape(shape:ShapeDefinition) -> shapeOperations.Shape:
    return shapeOperations.Shape.fromShapeCode(shape.ToString())

def _pyShapePartToGameShapePart(shapePart:shapeOperations.ShapePart) -> ShapePart:
    if shapePart.shape == shapeOperations.NOTHING_CHAR:
        shape = None
    else:
        shape = IShapeSubPart(
            shapePart.shape,
            shapePart.shape == shapeOperations.CRYSTAL_CHAR,
            shapePart.shape != shapeOperations.PIN_CHAR,
            shapePart.shape not in shapeOperations.UNPAINTABLE_SHAPES
        )
    color = None if shapePart.color == shapeOperations.NOTHING_CHAR else IShapeColor(shapePart.color)
    return ShapePart(shape,color)

def _pyShapeToGameShape(shape:shapeOperations.Shape) -> ShapeDefinition:
    return ShapeDefinition([
        ShapeLayer([
            _pyShapePartToGameShapePart(p) for p in l
        ]) for l in shape.layers
    ])

@dataclass
class GameMode:
    ShapesConfiguration:IShapesConfiguration
    ShapeColorScheme:IShapeColorScheme
    Seed:Int32
    MaxShapeLayers:Int32

class ShapeRegistry:

    def __init__(self,maxShapeLayers:Int32) -> None:
        self.maxShapeLayers = maxShapeLayers
        self._pyOperationsConfig = shapeOperations.ShapeOperationConfig(int(maxShapeLayers))

    def Op_Stack(self,bottomShape:ShapeDefinition,topShape:ShapeDefinition) -> ShapeDefinition:
        return _pyShapeToGameShape(shapeOperations.stack(
            _gameShapeToPyShape(bottomShape),
            _gameShapeToPyShape(topShape),
            config=self._pyOperationsConfig
        )[0])

    def Op_PushPin(self,shape:ShapeDefinition) -> ShapeDefinition:
        return _pyShapeToGameShape(shapeOperations.pushPin(_gameShapeToPyShape(shape),config=self._pyOperationsConfig)[0])

    def Op_Crystallize(self,shape:ShapeDefinition,color:IShapeColor) -> ShapeDefinition:
        return _pyShapeToGameShape(shapeOperations.genCrystal(_gameShapeToPyShape(shape),color.Code,config=self._pyOperationsConfig)[0])