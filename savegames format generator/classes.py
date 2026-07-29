#region base types

class byte: ...
bytes
class short: ...
class ushort: ...
int
class uint: ...
class long: ...
class ulong: ...
float
bool
str

class T: ...

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

class GlobalTileCoordinate:
    d="Represents a building level position."
    c=(
        (int,"The X coordinate"),
        (int,"The Y coordinate"),
        (short,"The Z coordinate")
    )

class Rotation:
    c=(
        (byte,[
            ["Byte value","Rotation"],
            ["0","East"],
            ["1","South"],
            ["2","West"],
            ["3","North"]
        ]),
    )

class RailConfig:
    c=(
        (int,"The number of connection color filters encoded"),
        (Array(
            (int,"A bit mask where each color is `1 << colorIndex`, with the `colorIndex` being determined by the `RailColorsConfig` key of the current <a href=\"https://shapez2.wiki.gg/wiki/Custom_Game_Modes#Custom_Scenarios\">scenario</a>")
        ),"The color filters for each connection of the rail (a connection being one of the possible input -> output paths)")
    )

class TrainUnloaderConfig:
    c=(
        (int,"The lanes disabled for unloading, stored as a bit mask, where each lane is `1 << layerIndex`"),
    )

class IIslandConfiguration:
    d=(
        "Represents an island configuration object, the type of which should be deduced from the previously decoded island ID.",
        [
            ["Island types","Configuration"],
            ["All rail types (regular, splitter, merger)",RailConfig],
            ["Shape and fluid train unloaders and transfers",TrainUnloaderConfig]
        ]
    )

class IslandTileCoordinate:
    d="Represents a building level positon relative the island center (see the 'Note' in [this section](https://gist.github.com/Loupau38/77907c80c7be3dd9f00a62d416581bb3#blueprint-center))."
    c=(
        (short,"The X coordinate"),
        (short,"The Y coordinate"),
        (byte,"The Z coordinate")
    )

class LabelConfig:
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

class ShapeId:
    c=(
        (ShapeItem,"Ingame, shapes are represented by integer IDs that are generated at runtime. When serializing, the corresponding ShapeItem is used instead"),
    )

class FluidId:
    c=(
        (IFluid,"Ingame, fluids are represented by integer IDs that are generated at runtime. When serializing, the corresponding IFluid is used instead"),
    )

# ingame there are 3 different methods that can serialize a CargoPackage, but they all do it in the exact same way
class CargoPackage[T_]:
    c=(
        (short,"The amount contained"),
        (T,"The object contained, only there if the amount isn't 0")
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
            ["3",(CargoPackage," of ",FluidId)],
            ["4",(CargoPackage," of ",ShapeId)],
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
    c=(
        (ISignal,"The signal produced"),
    )

class ItemProducerConfig:
    c=(
        (IBeltItem,"The item produced"),
    )

class FluidProducerConfig:
    c=(
        (IFluid,"The fluid produced"),
    )

class ButtonConfig:
    c=(
        (bool,"Whether the button is activated"),
    )

class CompareGateConfig:
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
                ["3","Shape",("The value of the ",ShapeId," corresponding to the shape (i.e. meaningless)")],
                ["4","Fluid",("The fluid's color code, single character converted to a ",byte," then to an ",int)],
                ["5","Positive Integer","The integer itself"],
                ["6","Negative Integer","The integer's opposite value"]
            ]
        ),
    )

class GlobalSignalReceiverConfig:
    c=(
        (SignalChannelId,"For operator signal receivers, this represents the ROS line selected. TODO : is this representative for global signal receivers"),
    )

class IBuildingConfiguration:
    d=(
        "Represents a building configuration object, the type of which should be deduced from the previously decoded building ID.",
        [
            ["Building type","Configuration"],
            ["Label",LabelConfig],
            ["Signal producer",SignalProducerConfig],
            ["Item producer",ItemProducerConfig],
            ["Fluid producer",FluidProducerConfig],
            ["Button",ButtonConfig],
            ["Comparison gate",CompareGateConfig],
            ["Global signal receivers and operator signal receivers",GlobalSignalReceiverConfig]
        ]
    )

class Steps:
    d="Represents a distance in the world."
    c=(
        (long,"The number of steps, divide this number by 2305195200000 to get the distance in machine level tiles"),
    )

class BeltLaneState:
    c=(
        (bool,"Whether an item is contained"),
        (IBeltItem,"Item, only there if the first value is `true`"),
        (Steps,"Progress, only there if the first value is `true`")
    )

class Ticks:
    d="Represents a duration of time."
    c=(
        (long,"The number of ticks, divide this number by 9604980000 to get the duration in seconds"),
    )

class SignalTicks:
    d="Represents a duration of time for wires."
    c=(
        (long,"The number of ticks, divide this number by 12 to get the duration in seconds"),
    )

class SignalBuffer:
    c=(
        (int,"ValuesArraySize"),
        (Array(
            (ISignal,"")
        ),"Values"),
        (Ticks,"LastStartTicks"),
        (SignalTicks,"LastSignalTick"),
        (bool,"WasPushedThisStartTick")
    )

class SignalConductorInputState:
    c=(
        (SignalBuffer,"InputConductor"),
    )

class FastBeltPathLaneState:
    c=(
        Checkpoint("fast-belt-path:start"),
        (short,"ItemCapacity"),
        (short,"CompressedItemsAfterFirst"),
        (Blob(
            (int,"ItemCount"),
            (Steps,"FirstItemDistance"),
            (Array(
                (IBeltItem,"Item"),
                (Steps,"NextItemDistance")
            ),"Items")
        ),""),
        Checkpoint("fast-belt-path:end")
    )

class BeltSlotState:
    c=(
        (bool,"Whether an item is contained"),
        (IBeltItem,"Item, only there if the first value is `true`"),
        (Steps,"Progress, only there if the first value is `true`")
    )

class BeltPathLaneState:
    c=(
        Checkpoint("belt-path-state:start"),
        (int,"Number of slots"),
        (Array(
            (BeltSlotState,""),
        ),"Slots"),
        Checkpoint("belt-path-state:end")
    )

class SimulationBufferState[T_]:
    c=(
        (int,"Number of items in queue"),
        (Blob(
            (Array(
                (T,"Contained item"),
                (Ticks,"SelfExcess")
            ),"Queue, ingame it is reversed on deserialization, see SPZ2-6575")
        ),"")
    )

class FluidContainerState:
    c=(
        (FluidUnit,"Value"),
        (IFluid,"Fluid")
    )

class FluidPackageLaunchState:
    c=(
        (IFluid,"Fluid"),
        (FluidUnit,"Amount"),
        (Ticks,"RemainingTicks"),
        (Ticks,"TotalTicks")
    )

class ShapeCollapseResult:
    c=(
        (int,"The number of items in the array. If this is `0`, the rest of the format will not be written and the ShapeCollapseResult object is `null`"),
        (bool,"Whether the result shape is valid (i.e. not empty)"),
        (str,"Shape code of the result shape, only there if the previous value is `true`"),
        (Array(
            (str,"Shape code of the group"),
            (byte,"FallDownLayers"),
            (bool,"Vanish")
        ),"Groups making up the result shape")
    )

class BundleState[T_]:
    c=(
        (Array(
            (T,"Contained items")
        ),"An array of 12 elements (the number of lanes on a space belt/pipe)"),
    )

class PathMergerSimulationState:
    c=(
        (byte,"Number of input lanes"),
        (Array(
            (Array(
                (BeltLaneState,"")
            ),"Array of 4 elements")
        ),"InputSegmentSlotStates"),
        (short,"PriorityLaneIndex"),
        (byte,"PreferredInputIndex")
    )

class PathSplitterSimulationState:
    c=(
        (byte,"Number of output lanes"),
        (Array(
            (BeltPathLaneState,"")
        ),"OutputLaneStates"),
        (byte,"NextPreferredIndex")
    )

#region simulation states

# name changes
BeltItemSimulationBufferState = SimulationBufferState[IBeltItem]
GenericFluid = IFluid
MixerSimulationMixingState = type # value shouldn't be used

class SplitterSimulationState:
    c=(
        (byte,"Number of output lanes"),
        (BeltLaneState,"InputLaneState"),
        (Array(
            (BeltLaneState,"")
        ),"OutputLaneStates")
    )

class BeltFilterSimulationState:
    c=(
        (SplitterSimulationState,"The BeltFilterSimulationState class inherits from SplitterSimulationState"),
        (SignalConductorInputState,"InputConductorState")
    )

class BeltPortSenderTransferSimulationState:
    c=(
        (byte,"ItemCapacity attribute of JumpLaneState, constant 2 (the written value is ignored on deserialization)"),
        (FastBeltPathLaneState,"JumpLaneState")
    )

class ConverterHubProducerSimulationState:
    c=(
        (BeltLaneState,"OutputLaneState"),
        (int,"NumProducedItems")
    )

class ConverterSimulationState:
    d="TODO : this supposedly throws an exception on deserialization"

class MergerSimulationState:
    c=(
        (byte,"Number of input lanes"),
        (Array(
            (BeltLaneState,"")
        ),"InputLaneStates"),
        (BeltLaneState,"OutputLaneState"),
        (short,"CurrentInputIndex"),
        (byte,"PreferredInputIndex")
    )

class MixerSimulationState:
    c=(
        (FluidContainerState,"Input0ContainerState"),
        (FluidContainerState,"Input1ContainerState"),
        (FluidContainerState,"Chamber0ContainerState"),
        (FluidContainerState,"Chamber1ContainerState"),
        (FluidContainerState,"OutputContainerState"),
        (byte,[
            ["Byte value","Mixing State"],
            ["0","Filling chambers"],
            ["1","Mixing"],
            ["2","Draining"]
        ]),
        (Ticks,"MixingProgress"),
        (IFluid,"MixingResult")
    )

class PrioritySplitterSimulationState:
    c=(
        (SplitterSimulationState,"The PrioritySplitterSimulationState class inherits from SplitterSimulationState"),
        (byte,"PrioritizedIndex")
    )

class SpaceConverterHubSimulationState:
    c=(
        (byte,"Number of output lanes"),
        (Array(
            (BundleState[FastBeltPathLaneState],"")
        ),"OutputLaneBundleStates")
    )

class SpaceConverterSimulationState:
    c=(
        (byte,"Number of input lanes"),
        (byte,"Number of output lanes"),
        (Array(
            (BundleState[FastBeltPathLaneState],"")
        ),"InputLaneBundleStates"),
        (BundleState[ConverterSimulationState],"SimulationBundleState"),
        (Array(
            (BundleState[FastBeltPathLaneState],"")
        ),"OutputLaneBundleStates"),
        (int,"ConversionCount")
    )

class SpaceMergerSimulationState:
    c=(
        (BundleState[PathMergerSimulationState],"MergerSimulationBundleState"),
        (byte,"Number of input lanes"),
        (Array(
            (BundleState[FastBeltPathLaneState],"")
        ),"InputLaneBundleStates")
    )

class SpaceResearchStationSimulationState:
    d="TODO : this supposedly throws an exception on deserialization"

class SpaceTrashSimulationState:
    d="TODO : this supposedly throws an exception on deserialization"

class TrashSimulationState:
    c=(
        (Array(
            (BeltLaneState,"")
        ),"An array of 4 elements"),
    )

SIMULATION_STATE_EXCEPTIONS:list[type] = [
    SplitterSimulationState,
    BeltFilterSimulationState,
    BeltPortSenderTransferSimulationState,
    ConverterHubProducerSimulationState,
    ConverterSimulationState,
    MergerSimulationState,
    MixerSimulationState,
    PrioritySplitterSimulationState,
    SpaceConverterHubSimulationState,
    SpaceConverterSimulationState,
    SpaceMergerSimulationState,
    SpaceResearchStationSimulationState,
    SpaceTrashSimulationState,
    TrashSimulationState
]

class ISimulationState:
    d="A simulation state, the type of which should be deduced from the previously decoded ID, according to the table below. The simulation state classes and the objects contained inside are pretty repetitive and sometimes unclear on their function, so the format descriptions here might be less detailed than in the rest of the documentation, sometimes the description will just be the ingame name of the attribute described.", [["Class ID","Simulation State Class"]]

class SimulationStateContainer:
    c=(
        (str,"The simulation state class's serialization ID, or `null` if the simulation state itself is `null`"),
        (Blob(
            (ISimulationState,"")
        ),"The simulation state, only there if the previous value wasn't `null`")
    )

#endregion

class ChunkDirection:
    d="Represents a 3D direction."
    c=(
        (byte,[
            ["Byte value","Direction"],
            ["0","East"],
            ["1","South"],
            ["2","West"],
            ["3","North"],
            ["4","Up"],
            ["5","Down"]
        ]),
    )

class LayeredWagonCargo[T_]:
    c=(
        (byte,"The number of containers"),
        (Array(
            # this part is a CargoContainer
            (short,"The number of packages"),
            (short,"The max number of packages"),
            (Array(
                (CargoPackage[T],"")
            ),"The packages")
        ),"The containers")
    )

class TrainCargoExchangerState[T_]:
    c=(
        (byte,"Constant 2, makes the game not load the following Blob if a different value"),
        (Blob(
            (BundleState[BeltPathLaneState],"Loading paths states")
        ),""),
        (Array(
            (CargoPackage[T],"")
        ),"Filling containers states, array of 3 elements (the number of floors)"),
        (Array(
            (BeltPathLaneState,"")
        ),"Cargo on track states, array of 3 elements (the number of floors)"),
        (bool,"Constant `true`, makes the game not load the following array if `false`"),
        (Array(
            (BeltPathLaneState,"")
        ),"Cargo on bridge states, array of 3 elements (the number of floors)"),
    )

class TrainCargoTransferState:
    c=(
        (Array(
            (BeltPathLaneState,"")
        ),"Cargo on track states, array of 3 elements (the number of floors)"),
        (Array(
            (BeltPathLaneState,"")
        ),"Cargo on input bridge states, array of 3 elements (the number of floors)"),
        (Array(
            (BeltPathLaneState,"")
        ),"Cargo on output bridge states, array of 3 elements (the number of floors)")
    )

class SuperChunkCoordinate:
    d="Represents a super chunk position. A super chunk is a square with a side length of 64 chunks (island level tiles)."
    c=(
        (int,"The X coordinate"),
        (int,"The Y coordinate")
    )

# feels appropriate to make it its own class (instead of being integrated in ResourceChunksBIN)
class ShapeDefinition:
    d="Represents the definition of a shape, i.e. a list of parts inside a list of layers."
    c=(
        (str,"The shape code"),
    )

class StatisticsStream[T_]:
    c=(
        (int,"The total number of entries contained, only used to do further processing on the entries after deserialization ingame"),
        (int,"The number of elements in the array below"),
        (Array(
            (T,"They key for which the entries below are"),
            (int,"The number of entries"),
            (Array(
                (Ticks,"The delivery time"),
                (byte,"The amount delivered at that time (if the amount exceeds 255, multiple entries with the same delivery time will be present)")
            ),"The entries")
        ),"The entries grouped by which key they belong to")
    )

class StatisticsBucket[T_]:
    c=(
        (int,"The number of counts"),
        (Array(
            (T,"The key to which the count belongs to"),
            (long,"The count's value")
        ),"The counts")
    )

class IntervalBasedStatisticsTracker[T_]:
    c=(
        (int,"Last bucket index"),
        (int,"Max bucket history, must be 32"),
        (Ticks,"The interval, must the be the value specified in the <a href=\"#statisticsbin\">statistics.bin</a> description"),
        (int,"The number of buckets"),
        (Blob(
            (Array(
                (StatisticsBucket[T],"")
            ),"The buckets")
        ),"")
    )

class AggregatedStatisticsTracker[T_]:
    c=(
        (StatisticsBucket[T],"The bucket contained"),
    )

class SlidingWindowStatisticsStreamView:
    c=(
        (int,"The number of buckets, must be 1"),
        (Array(
            (int,"EntriesStartIndex, relative to an internal list in ",StatisticsStream),
            (int,"EntriesCount, same as above")
        ),"The buckets")
    )

class IStatisticsTracker[T_]:
    d="A statistics tracker, can be ", IntervalBasedStatisticsTracker, " of ", T, ", ", AggregatedStatisticsTracker, " of ", T, ", or ", SlidingWindowStatisticsStreamView, ". See the description in [statistics.bin](#statisticsbin) to know which."

class RocketGroupId:
    c=(
        (str,"The ID of the rocket group"),
    )

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
#region simulation state

class SimulationStateBIN:
    d="Holds data about the current simulation time and the signals inside the currently active global signal transmitter channels."
    c=(
        (Ticks,"The current simulation time, i.e. how long the simulation has been running for since the save was created"),
        (int,"The number of active channels"),
        (Array(
            (SignalChannelId,"The channel ID"),
            (Blob(
                (int,"The number of signals in the array"),
                (Array(
                    (ISignal,"The signal value"),
                    (SignalTicks,"The time associated to that signal")
                ),"The signals for the channel")
            ),"The channel's state")
        ),"The active channels")
    )

#endregion
#region cargo

class CargoBIN:
    d="The data about packages in train loaders, unloaders, and transfers."
    c=(
        (Blob(
            (int,"The number of shape loaders"),
            (Array(
                (GlobalChunkCoordinate,"The loader's position"),
                (Blob(
                    (TrainCargoExchangerState[ShapeId],"")
                ),"The loader's state")
            ),"The shape loaders"),
            (int,"The number of fluid loaders"),
            (Array(
                (GlobalChunkCoordinate,"The loader's position"),
                (Blob(
                    (TrainCargoExchangerState[FluidId],"")
                ),"The loader's state")
            ),"The fluid loaders"),
            (int,"The number of shape unloaders"),
            (Array(
                (GlobalChunkCoordinate,"The unloader's position"),
                (Blob(
                    (TrainCargoExchangerState[ShapeId],"")
                ),"The unloader's state")
            ),"The shape unloaders"),
            (int,"The number of fluid unloaders"),
            (Array(
                (GlobalChunkCoordinate,"The unloader's position"),
                (Blob(
                    (TrainCargoExchangerState[FluidId],"")
                ),"The unloader's state")
            ),"The fluid unloaders"),
            (int,"The number of shape transfers"),
            (Array(
                (GlobalChunkCoordinate,"The transfer platform's position"),
                (Blob(
                    (TrainCargoTransferState,"")
                ),"The transfer platform's state")
            ),"The shape tranfers"),
            (int,"The number of fluid transfers"),
            (Array(
                (GlobalChunkCoordinate,"The transfer platform's position"),
                (Blob(
                    (TrainCargoTransferState,"")
                ),"The transfer platform's state")
            ),"The fluid transfers")
        ),""),
    )

#endregion
#region resource chunks

class ResourceChunksBIN:
    d="The data about asteroids on the map."
    c=(
        (int,"The number of super chunks serialized, those being the ones that contain islands"),
        (Array(
            Checkpoint("super-chunk"),
            (SuperChunkCoordinate,"The super chunk's position"),
            (Blob(
                Checkpoint("super-chunk:shape-resources"),
                (int,"The number of shape asteroids"),
                (Array(
                    (int,"Resource type, only valid value is `1`"),
                    (GlobalChunkCoordinate,"The asteroid origin postion"),
                    (int,"The number of tiles in the asteroid"),
                    (Array(
                        (ShapeDefinition,"")
                    ),"The shapes in the asteroid. Same number of elements as the number of tiles, with each shape being in the tile with the same index in the next array"),
                    (Array(
                        (int,"The X coordinate"),
                        (int,"The Y coordinate")
                    ),"The tiles in the asteroid, each element is a position relative to the asteroid's origin")
                ),"The shape asteroids"),
                Checkpoint("super-chunk:fluid-resources"),
                (int,"The number of fluid asteroids"),
                (Array(
                    (int,"Resource type, only valid value is `1`"),
                    (GlobalChunkCoordinate,"The asteroid origin position"),
                    (IFluid,"The fluid in the asteroid"),
                    (int,"The number of tiles in the asteroid"),
                    (Array(
                        (int,"The X coordinate"),
                        (int,"The Y coordinate")
                    ),"The tiles in the asteroid, each element is a position relative to the asteroid's origin")
                ),"The fluid asteroids")
            ),"The asteroids contained in the super chunk")
        ),"The super chunks serialized")
    )

#endregion
#region trains

class TrainsBIN:
    d="The data about all trains in the save."
    c=(
        (int,"The number of trains"),
        (Array(
            Checkpoint("TrainData"),
            (Blob(
                (Blob(
                    (str,"The train color's ID"),
                    (float,"Chunk progress"),
                    (byte,[
                        ["Byte value","Train state"],
                        ["0","Idle"],
                        ["1","Moving"]
                    ]),
                    (bool,"Is upside down"),
                    (int,"The number of wagons"),
                    (Array(
                        (GlobalChunkCoordinate,"Incoming position"),
                        (GlobalChunkCoordinate,"Outgoing position"),
                        (ChunkDirection,"Incoming direction"),
                        (ChunkDirection,"Outgoing direction"),
                        (bool,"Is upside down"),
                        (byte,[
                            ["Byte value","Wagon state"],
                            ["0","Moving"],
                            ["1","Airborne"],
                            ["2","Twisting"],
                            ["3","Flipping"],
                            ["4","In queue for production"],
                            ["5","Producing"],
                            ["6","Looping"],
                            ["7","Launching into HUB"],
                            ["8","Looping flipped"]
                        ]),
                        (float,"Travelled chunks inside jump"),
                        (float,"Jump length")
                    ),"Wagons"),
                    (float,"Velocity"),
                    (float,"Max speed ahead"),
                    (float,"Acceleration"),
                    (float,"Chunks until max speed should be respected"),
                    (bool,"Is stopped"),
                    (bool,"Was stopped in current chunk"),
                    (Ticks,"Stop time"),
                    (int,"The number of occupied rails"),
                    (Array(
                        (GlobalChunkCoordinate,"The rail's position"),
                        (bool,"Whether the occupied position is under the rail")
                    ),"Occupied rails")
                ),"The navigation state"),
                (GlobalChunkCoordinate,"Parent producer position"),
                (Blob(
                    (int,"The number of fluid wagons"),
                    (Array(
                        (int,"The wagon's index in the train"),
                        (LayeredWagonCargo[FluidId],"The wagon's cargo")
                    ),"Fluid wagons")
                ),"The fluid cargo data"),
                (Blob(
                    (int,"The number of shape wagons"),
                    (Array(
                        (int,"The wagon's index in the train"),
                        (LayeredWagonCargo[ShapeId],"The wagon's cargo")
                    ),"Shape wagons")
                ),"The shape cargo data")
            ),"")
        ),"Each element is a train")
    )

#endregion
#region statistics

# ShapeId here -> UnifiedShapeId ingame
class StatisticsBIN:
    d="The data for everything showed in the statistics screen."
    c=(
        (Blob(
            (Blob(
                (StatisticsStream[ShapeId],"The shape statistics stream")
            ),""),
            (int,"The number of shape delivery trackers, must be 9"),
            (Array(
                (Blob(
                    (IStatisticsTracker[ShapeId],"The first 5 elements are ",IntervalBasedStatisticsTracker, "s of ", ShapeId, " with intervals of 1, 5, 60, 300, and 3600 seconds, the next element is an ",AggregatedStatisticsTracker, " of ", ShapeId, ", and the last 3 elements are ",SlidingWindowStatisticsStreamView, "s")
                ),"")
            ),"The shape delivery trackers")
        ),"The shape statistics"),
        (Blob(
            (Blob(
                (StatisticsStream[RocketGroupId],"The rocket statistics stream")
            ),""),
            (int,"The number of rocket delivery trackers, must be 9"),
            (Array(
                (Blob(
                    (IStatisticsTracker[RocketGroupId],"Same as above (but with ",ShapeId," replaced by ",RocketGroupId,")")
                ),"")
            ),"The rocket delivery trackers")
        ),"The rocket statistics")
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