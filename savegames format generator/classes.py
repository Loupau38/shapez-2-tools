#region base types

class byte: ...
bytes
class short: ...
class ushort: ...
int
class uint: ...
class long: ...
class ulong: ...
bool
str

class Checkpoint:
    def __init__(self,id:str):
        self.id = id

class Blob:
    def __init__(self,*content):
        self.content = content

class Array:
    def __init__(self,*content):
        self.content = content

#endregion
#region contained objects

class GlobalChunkCoordinate:
    d="Represents an island level position."
    c=(
        (int,"The X coordinate"),
        (int,"The Y coordinate"),
        (short,"The Z coordinate")
    )

class ISimulationState:
    d="todo"

class SimulationStateContainer:
    c=(
        (str,"The simulation state class's serialization ID, or `null` if the simulation state itself is `null`"),
        (Blob(
            (ISimulationState,"")
        ),"The simulation state, only there if the previous value wasn't `null`")
    )

class GlobalTileCoordinate:
    d="Represents a building level position."
    c=(
        (int,"The X coordinate"),
        (int,"The Y coordinate"),
        (short,"The Z coordinate")
    )

class Rotation:
    c=(
        (byte,"0 : East, 1 : South, 2 : West, 3 : North"),
    )

class RailConfig:
    d="Applies to all rail types (regular, splitter, merger)."
    c=(
        (int,"The number of connection color filters encoded"),
        (Array(
            (int,"A bit mask where each color is `1 << colorIndex`, with the `colorIndex` being determined by the `RailColorsConfig` key of the current <a href=\"https://shapez2.wiki.gg/wiki/Custom_Game_Modes#Custom_Scenarios\">scenario</a>")
        ),"The color filters for each connection of the rail (a connection being one of the possible input -> output paths)")
    )

class TrainUnloaderConfig:
    d="Applies to shape and fluid train unloaders and transfer stations."
    c=(
        (int,"The lanes disabled for unloading, stored as a bit mask, where each lane is `1 << layerIndex`"),
    )

class IIslandConfiguration:
    d="Represents an island configuration object, the type of which should be deduced from the previously decoded island ID. Can be ", RailConfig, " or ", TrainUnloaderConfig, "."

class IslandTileCoordinate:
    d="Represents a building level positon relative the island center (see the 'Note' in [this section](https://gist.github.com/Loupau38/77907c80c7be3dd9f00a62d416581bb3#blueprint-center))."
    c=(
        (short,"The X coordinate"),
        (short,"The Y coordinate"),
        (byte,"The Z coordinate")
    )

class LabelConfig:
    d="Applies to labels."
    c=(
        (str,"The label's text"),
    )

class ShapeItem:
    c=(
        (bool,"`false` if the object is `null`, `true` otherwise"),
        (str,"The shape code, only there if the previous value was `true`")
    )

class ColorFluid:
    c=(
        (byte,"The color's color code (a single character)"),
    )

class IFluid:
    d=(
        "The encoded data starts with a ",
        byte,
        " representing the type of fluid :",
        [
            ["Byte value","Data encoded after"],
            ["0","`null` (nothing encoded)"],
            ["1",ColorFluid]
        ]
    )

class FluidUnit:
    c=(
        (long,"The amount of fluid, divide this number by 38419920000 to get the amount in liters"),
    )

class FluidPackageItem:
    c=(
        (IFluid,"The type of fluid contained"),
        (FluidUnit,"The amount of fluid contained")
    )

class FluidPackageOnTrack:
    c=(
        (short,"The amount contained"),
        (IFluid,"The fluid contained, only present if the amount isn't 0")
    )

class ShapePackageOnTrack:
    c=(
        (short,"The amount contained"),
        (ShapeItem,"The shape contained, only present if the amount isn't 0")
    )

class IBeltItem:
    d=(
        "The encoded data starts with a ",
        byte,
        " representing the type of belt item :",
        [
            ["Byte value","Data encoded after"],
            ["0","`null` (nothing encoded)"],
            ["1",ShapeItem],
            ["2",FluidPackageItem],
            ["3",FluidPackageOnTrack],
            ["4",ShapePackageOnTrack],
        ]
    )

class ISignal:
    d=(
        "The encoded data starts with a ",
        byte,
        " representing the type of signal :",
        [
            ["Byte value","Type of signal","Data encoded after","Notes"],
            ["0","`null`","none","This means a `null` object, which produces errors if actually loaded ingame"],
            ["1","Null","none","This means a Null Signal, supported by the game"],
            ["2","Conflict","none",""],
            ["3","Integer",int,""],
            ["4","Integer 0","none","This produces the same type of Integer Signal as with a `3` byte"],
            ["5","Integer 1","none","This produces the same type of Integer Signal as with a `3` byte"],
            ["6","Belt Item",IBeltItem,"Ingame, this returns a Null Signal if the `IBeltItem` object is `null`"],
            ["7","Fluid",IFluid,"Ingame, this returns a Null Signal if the `IFluid` object is `null`"]
        ]
    )

class SignalProducerConfig:
    d="Applies to signal producers."
    c=(
        (ISignal,"The signal produced"),
    )

class ItemProducerConfig:
    d="Applies to item producers."
    c=(
        (IBeltItem,"The item produced"),
    )

class FluidProducerConfig:
    d="Applies to fluid producers."
    c=(
        (IFluid,"The fluid produced"),
    )

class ButtonConfig:
    d="Applies to buttons."
    c=(
        (bool,"Whether the button is activated"),
    )

class CompareGateConfig:
    d="Applies to comparison gates."
    c=(
        (
            byte,
            [
                ["Byte Value","Compare mode"],
                ["1","Equal"],
                ["2","GreaterEqual"],
                ["3","Greater"],
                ["4","Less"],
                ["5","LessEqual"],
                ["6","NotEqual"],
            ]
        ),
    )

class SignalChannelId:
    c=(
        (
            int,
            "The channel ID. The upper ",
            byte,
            " represents the type of channel and the channel value is an ",
            int,
            " bitwise-OR'ed with the channel type (unexpected behavior can happen if the channel value needs more than 3 bytes to be encoded) :",
            [
                ["Channel Type Byte","Channel Type Name","Channel Value"],
                ["2","ROS","The goal line index"],
                ["3","Shape","The shape's UID, internal to the game and generated at runtime"],
                ["4","Fluid",("The fluid's color code, single character converted to a ",byte," then to an ",int)],
                ["5","Positive Integer","The integer itself"],
                ["6","Negative Integer","The integer's opposite value"]
            ]
        ),
    )

class GlobalSignalReceiverConfig:
    d="Applies to global signal receivers and operator signal receivers."
    c=(
        (SignalChannelId,"For operator signal receivers, this represents the ROS line selected. TODO : is this representative for global signal receivers"),
    )

class IBuildingConfiguration:
    d="Represents a building configuration object, the type of which should be deduced from the previously decoded building ID. Can be ", LabelConfig, ", ", SignalProducerConfig, ", ", ItemProducerConfig, ", ", FluidProducerConfig, ", ", ButtonConfig, ", ", CompareGateConfig, " or ", GlobalSignalReceiverConfig, "."

#endregion
#region buildings.bin

class BuildingsBIN:
    d="The files in this folder encode the simulation state of buildings and islands, with each file being an island bundle. When the save is generated by the game, each bundle contains the same islands as the corresponding bundle in [maps/main/islands/[#].bin](#mapsmainislandsbin) (the same notes on bundle contents apply here), but this is not a requirement when loading a save.\n\nEach file has the following format :"
    c=(
        (int,"The number of islands in the bundle"),
        (Array(
            (GlobalChunkCoordinate,"The island's position, used to indentify which island this simulation state belongs to"),
            (str,"The island's ID, used as a safety check by comparing it with the ID of the island at that postition"),
            (Blob(
                (SimulationStateContainer,"The island's simulation state")
            ),"")
        ),"The islands inside the bundle"),
        (int,"The number of buildings in the bundle"),
        (Array(
            (GlobalTileCoordinate,"The building's position, used to indentify which building this simulation state belongs to"),
            (str,"The building's ID, used as a safety check by comparing it with the ID of the building at that postition"),
            (Blob(
                (SimulationStateContainer,"The building's simulation state")
            ),"")
        ),"The buildings inside the bundle. When generated by the game, those are the buildings placed on the islands inside the bundle, but they can be any building in the save")
    )

#endregion
#region islands.bin

class IslandsBIN:
    d="The files in this folder encode the type, position and configuration of buildings and islands. Each file is an 'island bundle', i.e. a group of islands, with the maximum number of islands per bundle when generated by the game being determined by the formula `ceil(4^log10(island_count))`. When the game loads a save however, there is no restrictions to how many islands can be in each bundle nor in which order the islands are inside a bundle nor the order of bundles themselves.\n\nEach file has the following format :"
    c=(
        (int,"The number of islands in the bundle"),
        (Array(
            Checkpoint("island"),
            (GlobalChunkCoordinate,"The island's position"),
            (str,"The island's ID"),
            (Rotation,"The island's rotation"),
            (Blob(
                (bool,"Whether the island has configuration data"),
                (Blob(
                    (IIslandConfiguration,"")
                ),"The island's configuration data, only there if the previous value was `true`"),
                (Blob(
                    Checkpoint("buildings"),
                    (int,"The number of buildings placed on the island"),
                    (Array(
                        Checkpoint("building"),
                        (IslandTileCoordinate,"The building's position"),
                        (Rotation,"The building's rotation"),
                        (str,"The building's ID"),
                        (bool,"Whether the building has configuration data"),
                        (Blob(
                            (IBuildingConfiguration,"")
                        ),"The building's configuration data, only there if the previous value was `true`")
                    ),"The buildings placed on the island")
                ),"The buildings placed on the island")
            ),"")
        ),"The islands inside the bundle")
    )

#endregion
#region strings.bin

class StringLUT:
    d="The string lookup table for the savegame."
    c=(
        (int,"The number of entries in the table"),
        (Array(
            (int,"The length of the string in bytes"),
            (bytes,"The string encoded in UTF-8")
        ),"The strings in the table")
    )