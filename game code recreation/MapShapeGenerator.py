import ConsistentRandom
import otherClasses
from otherClasses import MapShapeGenerationType
from fixedint import Int32

class MapShapeGenerator:

    def __init__(
        self,
        mapGenerationParameters:otherClasses.MapGenerationParameters,
        shapesConfiguration:otherClasses.IShapesConfiguration,
        colorScheme:otherClasses.IShapeColorScheme
    ) -> None:
        self.MapGenerationParameters = mapGenerationParameters
        self.ShapesConfiguration = shapesConfiguration
        self.ColorScheme = colorScheme

    def GenerateClusterShape_withType(
        self,
        rng:ConsistentRandom.ConsistentRandom,
        type:MapShapeGenerationType
    ) -> otherClasses.ShapeDefinition:

        match type:
            case MapShapeGenerationType.UncoloredHalfShape:
                accentColor = self.ColorScheme.DefaultShapeColor
            case MapShapeGenerationType.UncoloredAlmostFullShape:
                accentColor = self.ColorScheme.DefaultShapeColor
            case MapShapeGenerationType.UncoloredFullShape:
                accentColor = self.ColorScheme.DefaultShapeColor
            case MapShapeGenerationType.UncoloredFullShapePure:
                accentColor = self.ColorScheme.DefaultShapeColor
            case MapShapeGenerationType.PrimaryColorHalfShape:
                accentColor = rng.Choice(self.ColorScheme.PrimaryColors)
            case MapShapeGenerationType.PrimaryColorAlmostFullShape:
                accentColor = rng.Choice(self.ColorScheme.PrimaryColors)
            case MapShapeGenerationType.PrimaryColorFullShape:
                accentColor = rng.Choice(self.ColorScheme.PrimaryColors)
            case MapShapeGenerationType.PrimaryColorFullShapePure:
                accentColor = rng.Choice(self.ColorScheme.PrimaryColors)
            case MapShapeGenerationType.SecondaryColorHalfShape:
                accentColor = rng.Choice(self.ColorScheme.SecondaryColors)
            case MapShapeGenerationType.SecondaryColorAlmostFullShape:
                accentColor = rng.Choice(self.ColorScheme.SecondaryColors)
            case MapShapeGenerationType.SecondaryColorFullShape:
                accentColor = rng.Choice(self.ColorScheme.SecondaryColors)
            case MapShapeGenerationType.SecondaryColorFullShapePure:
                accentColor = rng.Choice(self.ColorScheme.SecondaryColors)
            case MapShapeGenerationType.TertiaryColorHalfShape:
                accentColor = rng.Choice(self.ColorScheme.TertiaryColors)
            case MapShapeGenerationType.TertiaryColorAlmostFullShape:
                accentColor = rng.Choice(self.ColorScheme.TertiaryColors)
            case MapShapeGenerationType.TertiaryColorFullShape:
                accentColor = rng.Choice(self.ColorScheme.TertiaryColors)
            case MapShapeGenerationType.TertiaryColorFullShapePure:
                accentColor = rng.Choice(self.ColorScheme.TertiaryColors)
            case _:
                raise ValueError

        partCount = self.ShapesConfiguration.PartCount

        oneQuad = Int32(1)
        halfShapeQuadCount = partCount // Int32(2)
        pureShapePartCount = partCount

        match type:
            case MapShapeGenerationType.UncoloredHalfShape:
                type1ShapeCount = oneQuad
            case MapShapeGenerationType.UncoloredAlmostFullShape:
                type1ShapeCount = oneQuad
            case MapShapeGenerationType.UncoloredFullShape:
                type1ShapeCount = halfShapeQuadCount
            case MapShapeGenerationType.UncoloredFullShapePure:
                type1ShapeCount = pureShapePartCount
            case MapShapeGenerationType.PrimaryColorHalfShape:
                type1ShapeCount = oneQuad
            case MapShapeGenerationType.PrimaryColorAlmostFullShape:
                type1ShapeCount = oneQuad
            case MapShapeGenerationType.PrimaryColorFullShape:
                type1ShapeCount = halfShapeQuadCount
            case MapShapeGenerationType.PrimaryColorFullShapePure:
                type1ShapeCount = pureShapePartCount
            case MapShapeGenerationType.SecondaryColorHalfShape:
                type1ShapeCount = oneQuad
            case MapShapeGenerationType.SecondaryColorAlmostFullShape:
                type1ShapeCount = oneQuad
            case MapShapeGenerationType.SecondaryColorFullShape:
                type1ShapeCount = halfShapeQuadCount
            case MapShapeGenerationType.SecondaryColorFullShapePure:
                type1ShapeCount = pureShapePartCount
            case MapShapeGenerationType.TertiaryColorHalfShape:
                type1ShapeCount = oneQuad
            case MapShapeGenerationType.TertiaryColorAlmostFullShape:
                type1ShapeCount = oneQuad
            case MapShapeGenerationType.TertiaryColorFullShape:
                type1ShapeCount = halfShapeQuadCount
            case MapShapeGenerationType.TertiaryColorFullShapePure:
                type1ShapeCount = pureShapePartCount
            case _:
                raise ValueError

        match type:
            case MapShapeGenerationType.UncoloredHalfShape:
                type2ShapeCount = oneQuad
            case MapShapeGenerationType.UncoloredAlmostFullShape:
                type2ShapeCount = halfShapeQuadCount
            case MapShapeGenerationType.UncoloredFullShape:
                type2ShapeCount = halfShapeQuadCount
            case MapShapeGenerationType.UncoloredFullShapePure:
                type2ShapeCount = Int32(0)
            case MapShapeGenerationType.PrimaryColorHalfShape:
                type2ShapeCount = oneQuad
            case MapShapeGenerationType.PrimaryColorAlmostFullShape:
                type2ShapeCount = halfShapeQuadCount
            case MapShapeGenerationType.PrimaryColorFullShape:
                type2ShapeCount = halfShapeQuadCount
            case MapShapeGenerationType.PrimaryColorFullShapePure:
                type2ShapeCount = Int32(0)
            case MapShapeGenerationType.SecondaryColorHalfShape:
                type2ShapeCount = oneQuad
            case MapShapeGenerationType.SecondaryColorAlmostFullShape:
                type2ShapeCount = halfShapeQuadCount
            case MapShapeGenerationType.SecondaryColorFullShape:
                type2ShapeCount = halfShapeQuadCount
            case MapShapeGenerationType.SecondaryColorFullShapePure:
                type2ShapeCount = Int32(0)
            case MapShapeGenerationType.TertiaryColorHalfShape:
                type2ShapeCount = oneQuad
            case MapShapeGenerationType.TertiaryColorAlmostFullShape:
                type2ShapeCount = halfShapeQuadCount
            case MapShapeGenerationType.TertiaryColorFullShape:
                type2ShapeCount = halfShapeQuadCount
            case MapShapeGenerationType.TertiaryColorFullShapePure:
                type2ShapeCount = Int32(0)
            case _:
                raise ValueError

        shapeParts:list[otherClasses.ShapePart] = []

        # Part 1 is shared, part 2 not
        part1 = self.PickRandomShape(rng)
        for i in range(type1ShapeCount):
            color = (
                accentColor
                if rng.TestPercentage(self.MapGenerationParameters.ShapePatchShapeColorfulnessPercent) else
                self.ColorScheme.DefaultShapeColor
            )
            shapeParts.append(otherClasses.ShapePart(part1,color))

        for i in range(type2ShapeCount):
            part2 = self.PickRandomShape(rng)
            color = (
                accentColor
                if rng.TestPercentage(self.MapGenerationParameters.ShapePatchShapeColorfulnessPercent) else
                self.ColorScheme.DefaultShapeColor
            )
            shapeParts.append(otherClasses.ShapePart(part2,color))

        assert len(shapeParts) > 0
        assert len(shapeParts) <= partCount

        for i in range(len(shapeParts),partCount):
            shapeParts.append(otherClasses.ShapePart(None,None))

        rng.Shuffle(shapeParts)

        layer = otherClasses.ShapeLayer(shapeParts)
        return otherClasses.ShapeDefinition([layer])

    def GenerateClusterShape_withDistance(
        self,
        rng:ConsistentRandom.ConsistentRandom,
        distanceToOrigin:Int32
    ) -> otherClasses.ShapeDefinition:

        type = MapShapeGenerationType.UncoloredHalfShape

        for shape in self.MapGenerationParameters.ShapePatchGenerationLikeliness:

            if (distanceToOrigin < shape.MinimumDistanceToOrigin) or (not rng.TestPerMille(shape.LikelinessPerMille)):
                continue

            # Found it!
            type = shape.GenerationType
            break

        return self.GenerateClusterShape_withType(rng,type)

    def PickRandomShape(self,rng:ConsistentRandom.ConsistentRandom) -> otherClasses.IShapeSubPart:

        if (
            (len(self.ShapesConfiguration.MapGenerationVeryRareParts) > 0)
            and (rng.TestPercentage(self.MapGenerationParameters.ShapePatchVeryRareShapeLikelinessPercent))
        ):
            return rng.Choice(self.ShapesConfiguration.MapGenerationVeryRareParts)

        if (
            (len(self.ShapesConfiguration.MapGenerationRareParts) > 0)
            and (rng.TestPercentage(self.MapGenerationParameters.ShapePatchRareShapeLikelinessPercent))
        ):
            return rng.Choice(self.ShapesConfiguration.MapGenerationRareParts)

        return rng.Choice(self.ShapesConfiguration.MapGenerationCommonParts)