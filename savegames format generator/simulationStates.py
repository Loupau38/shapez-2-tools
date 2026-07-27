from dataclasses import dataclass
from generator import simulationSateIDMarker as _serializationId
from classes import (
    BeltLaneState,
    SignalConductorInputState,
    FastBeltPathLaneState,
    BeltPathLaneState,
    BeltItemSimulationBufferState,
    BeltSlotState,
    FluidContainerState,
    Ticks as SimulationTicks,
    FluidPackageLaunchState,
    ShapeCollapseResult,
    MixerSimulationMixingState,
    BundleState,
    PathMergerSimulationState,
    PathSplitterSimulationState
)
# make sure no name conflicts happen because of this
import classes as gameObjects

# ↓ copy from shapez2/savegameObjects.py ↓

class GenericSimulationState: ...

@_serializationId("BeltFilterState")
@dataclass
class BeltFilterSimulationState(GenericSimulationState):
    inputLaneState:BeltLaneState
    outputLaneStates:list[BeltLaneState]
    inputConductorState:SignalConductorInputState

@_serializationId("BeltPortReceiverDisabledState")
@dataclass
class BeltPortReceiverDisabledState(GenericSimulationState):
    outputLaneState:BeltLaneState

@_serializationId("BeltPortSenderBlockedState")
@dataclass
class BeltPortSenderBlockedState(GenericSimulationState):
    inputLaneState:BeltLaneState

@_serializationId("BeltPortSenderDiscardState")
@dataclass
class BeltPortSenderDiscardState(GenericSimulationState):
    inputLaneState:BeltLaneState

@_serializationId("BeltPortSenderToHubState")
@dataclass
class BeltPortSenderToHubSimulationState(GenericSimulationState):
    inputLaneState:BeltLaneState
    vortexLaneState:FastBeltPathLaneState

@_serializationId("BeltPortSenderToSpacePathState")
@dataclass
class BeltPortSenderToSpacePathSimulationState(GenericSimulationState):
    pathLaneState:BeltPathLaneState
    bufferState:BeltItemSimulationBufferState

@_serializationId("BeltPortSenderTransferState")
class BeltPortSenderTransferSimulationState(GenericSimulationState):

    NUM_JUMP_LANE_ITEMS = 2

    def __init__(self,jumpLaneState:FastBeltPathLaneState):
        self.jumpLaneState = jumpLaneState

@_serializationId("BeltReaderState")
@dataclass
class BeltReaderSimulationState(GenericSimulationState):
    inputLaneState:BeltLaneState
    outputLaneState:BeltLaneState

@_serializationId("ControlledSignalReceiverState")
@dataclass
class ControlledSignalReceiverState(GenericSimulationState):
    inputConductorState:SignalConductorInputState

@_serializationId("ControlledSignalTransmitterState")
@dataclass
class ControlledSignalTransmitterState(GenericSimulationState):
    inputConductorState:SignalConductorInputState

@_serializationId("ConverterHubProducerState")
@dataclass
class ConverterHubProducerSimulationState(GenericSimulationState):
    outputLaneState:BeltLaneState
    numProducedItems:int

@_serializationId("ConverterState")
@dataclass
class ConverterSimulationState(GenericSimulationState):
    inputLaneStates:list[BeltLaneState]
    processingReceiverStates:list[BeltLaneState]
    processingLaneStates:list[BeltLaneState]
    outputLaneStates:list[BeltLaneState]

@_serializationId("ConveyorState")
@dataclass
class ConveyorSimulationState(GenericSimulationState):
    slot0:BeltSlotState
    slot1:BeltSlotState

@_serializationId("CrystalGeneratorState")
@dataclass
class CrystalGeneratorSimulationState(GenericSimulationState):
    inputLaneState:BeltLaneState
    outputLaneState:BeltLaneState
    containerState:FluidContainerState
    currentProcessingPaint:gameObjects.GenericFluid|None
    currentSourceShape:gameObjects.ShapeItem|None
    currentCrystalOnlyShape:gameObjects.ShapeItem|None
    fluidAmountDuringLastUpdate:gameObjects.FluidUnit
    excessTicks:SimulationTicks
    ticksSinceLastCrystallization:SimulationTicks
    ticksSinceItemEntered:SimulationTicks

@_serializationId("DisplayState")
@dataclass
class DisplaySimulationState(GenericSimulationState):
    inputConductorState:SignalConductorInputState

@_serializationId("ExtractorState")
@dataclass
class ExtractorSimulationState(GenericSimulationState):
    processingLaneState:BeltLaneState
    outputLaneState:BeltLaneState

@_serializationId("FluidPortReceiverDisabledState")
@dataclass
class FluidPortReceiverDisabledState(GenericSimulationState):
    outputContainer:FluidContainerState

@_serializationId("FluidPortSenderBlockedState")
@dataclass
class FluidPortSenderBlockedState(GenericSimulationState):
    inputContainer:FluidContainerState

@_serializationId("FluidPortSenderDiscardState")
@dataclass
class FluidPortSenderDiscardState(GenericSimulationState):
    inputContainer:FluidContainerState

@_serializationId("FluidPortSenderToSpacePipeState")
@dataclass
class FluidPortSenderToSpacePipeSimulationState(GenericSimulationState):
    inputContainer:FluidContainerState
    launchState:FluidPackageLaunchState

@_serializationId("FluidPortTransferState")
@dataclass
class FluidPortTransferState(GenericSimulationState):
    inputContainer:FluidContainerState
    launchState:FluidPackageLaunchState
    outputContainer:FluidContainerState

@_serializationId("FluidStorageState")
@dataclass
class FluidStorageSimulationState(GenericSimulationState):
    containerState:FluidContainerState

@_serializationId("FullCutterState")
@dataclass
class FullCutterSimulationState(GenericSimulationState):
    inputLaneState:BeltLaneState
    leftLaneState:BeltLaneState
    rightLaneState:BeltLaneState
    leftOutputLaneState:BeltLaneState
    rightOutputLaneState:BeltLaneState
    leftCollapseResult:ShapeCollapseResult|None
    rightCollapseResult:ShapeCollapseResult|None

@_serializationId("HalfCutterState")
@dataclass
class HalfCutterSimulationState(GenericSimulationState):
    inputLaneState:BeltLaneState
    processingLaneState:BeltLaneState
    outputLaneState:BeltLaneState
    currentWaste:ShapeCollapseResult|None
    currentCollapseResult:ShapeCollapseResult|None
    producingEmptyShape:bool

@_serializationId("HalvesSwapperState")
@dataclass
class HalvesSwapperSimulationState(GenericSimulationState):
    lowerInputLaneState:BeltLaneState
    lowerProcessingLaneState:BeltLaneState
    lowerOutputLaneState:BeltLaneState
    upperInputLaneState:BeltLaneState
    upperProcessingLaneState:BeltLaneState
    upperOutputLaneState:BeltLaneState
    lowerLeftCollapseResult:ShapeCollapseResult|None
    lowerRightCollapseResult:ShapeCollapseResult|None
    upperLeftCollapseResult:ShapeCollapseResult|None
    upperRightCollapseResult:ShapeCollapseResult|None
    lowerFinalResult:gameObjects.ShapeItem|None
    upperFinalResult:gameObjects.ShapeItem|None

@_serializationId("ItemProducerState")
@dataclass
class ItemProducerSimulationState(GenericSimulationState):
    outputLaneState:BeltLaneState

@_serializationId("Lift1LayerState")
@dataclass
class Lift1LayerSimulationState(GenericSimulationState):
    inputLaneState:BeltLaneState
    verticalLaneState:BeltLaneState
    outputLaneState:BeltLaneState

@_serializationId("Lift2LayerState")
@dataclass
class Lift2LayerSimulationState(GenericSimulationState):
    inputLaneState:BeltLaneState
    verticalLane0State:BeltLaneState
    verticalLane1State:BeltLaneState
    outputLaneState:BeltLaneState

@_serializationId("LogicGate2In1OutState")
@dataclass
class LogicGate2In1OutSimulationState(GenericSimulationState):
    input0ConductorState:SignalConductorInputState
    Input1ConductorState:SignalConductorInputState

@_serializationId("LogicGateCompareState")
@dataclass
class LogicGateCompareSimulationState(GenericSimulationState):
    input0ConductorState:SignalConductorInputState
    input1ConductorState:SignalConductorInputState

@_serializationId("LogicGateIfState")
@dataclass
class LogicGateIfSimulationState(GenericSimulationState):
    inputConductorState:SignalConductorInputState
    gateConductorState:SignalConductorInputState

@_serializationId("LogicGateNotState")
@dataclass
class LogicGateNotSimulationState(GenericSimulationState):
    inputConductorState:SignalConductorInputState

@_serializationId("MergerState")
@dataclass
class MergerSimulationState(GenericSimulationState):
    inputLaneStates:list[BeltLaneState]
    outputLaneState:BeltLaneState
    currentInputIndex:int
    preferredInputIndex:int

@_serializationId("MixerState")
@dataclass
class MixerSimulationState(GenericSimulationState):
    input0ContainerState:FluidContainerState
    input1ContainerState:FluidContainerState
    chamber0ContainerState:FluidContainerState
    chamber1ContainerState:FluidContainerState
    outputContainerState:FluidContainerState
    mixingState:MixerSimulationMixingState
    mixingProgress:SimulationTicks
    mixingResult:gameObjects.GenericFluid|None

@_serializationId("PainterState")
@dataclass
class PainterSimulationState(GenericSimulationState):
    inputLaneState:BeltLaneState
    outputLaneState:BeltLaneState
    containerState:FluidContainerState
    currentProcessingPaint:gameObjects.GenericFluid|None
    fluidAmountDuringLastUpdate:gameObjects.FluidUnit
    excessTicks:SimulationTicks
    ticksSinceLastPaint:SimulationTicks
    ticksSinceItemEntered:SimulationTicks

@_serializationId("PinPusherState")
@dataclass
class PinPusherSimulationState(GenericSimulationState):
    inputLaneState:BeltLaneState
    processingLaneState:BeltLaneState
    outputLaneState:BeltLaneState
    currentWaste:gameObjects.ShapeItem|None
    currentResult:ShapeCollapseResult|None

@_serializationId("PipeGateState")
@dataclass
class PipeGateSimulationState(GenericSimulationState):
    containerState:FluidContainerState
    inputConductorState:SignalConductorInputState

@_serializationId("RotatorState")
@dataclass
class RotatorSimulationState(GenericSimulationState):
    inputLaneState:BeltLaneState
    processingLaneState:BeltLaneState
    outputLaneState:BeltLaneState

@_serializationId("PrioritySplitterState")
@dataclass
class PrioritySplitterSimulationState(GenericSimulationState):
    inputLaneState:BeltLaneState
    outputLaneStates:list[BeltLaneState]
    prioritizedIndex:int

@_serializationId("SignalPortSenderBlockedState")
@dataclass
class SignalPortSenderBlockedState(GenericSimulationState):
    inputConductorState:SignalConductorInputState

@_serializationId("SignalPortTransferState")
@dataclass
class SignalPortTransferState(GenericSimulationState):
    inputConductorState:SignalConductorInputState

@_serializationId("ConverterHubState")
@dataclass
class SpaceConverterHubSimulationState(GenericSimulationState):
    outputLaneBundleStates:list[BundleState[FastBeltPathLaneState]]

@_serializationId("SpaceConverterState")
@dataclass
class SpaceConverterSimulationState(GenericSimulationState):
    inputLaneBundleStates:list[BundleState[FastBeltPathLaneState]]
    simulationBundleState:BundleState[ConverterSimulationState]
    outputLaneBundleStates:list[BundleState[FastBeltPathLaneState]]
    conversionCount:int

@_serializationId("SpaceConveyorState")
@dataclass
class SpaceConveyorSimulationState(GenericSimulationState):
    pathBundleState:BundleState[FastBeltPathLaneState]

@_serializationId("SpaceMergerState")
@dataclass
class SpaceMergerSimulationState(GenericSimulationState):
    mergerSimulationBundleState:BundleState[PathMergerSimulationState]
    inputLaneBundleStates:list[BundleState[FastBeltPathLaneState]]

@_serializationId("SpacePathToBeltPortReceiverState")
@dataclass
class SpacePathToBeltPortReceiverSimulationState(GenericSimulationState):
    inputLaneState:BeltLaneState
    pathLaneState:FastBeltPathLaneState
    bufferState:BeltItemSimulationBufferState

@_serializationId("SpacePipeToFluidPortReceiverState")
@dataclass
class SpacePipeToFluidPortReceiverSimulationState(GenericSimulationState):
    outputContainer:FluidContainerState
    launchState:FluidPackageLaunchState
    bufferState:BeltItemSimulationBufferState
    inputLaneState:BeltLaneState

@_serializationId("ResearchStationState")
@dataclass
class SpaceResearchStationSimulationState(GenericSimulationState):
    inputBundleState:BundleState[FastBeltPathLaneState]
    processingBundleState:BundleState[FastBeltPathLaneState]
    outputBundleState:BundleState[FastBeltPathLaneState]

@_serializationId("SpaceSplitterState")
@dataclass
class SpaceSplitterSimulationState(GenericSimulationState):
    splitterSimulationBundleState:BundleState[PathSplitterSimulationState]

@_serializationId("SpaceTrashState")
@dataclass
class SpaceTrashSimulationState(GenericSimulationState):
    inputBundleState:BundleState[FastBeltPathLaneState]

@_serializationId("SplitterState")
@dataclass
class SplitterSimulationState(GenericSimulationState):
    inputLaneState:BeltLaneState
    outputLaneStates:list[BeltLaneState]

@_serializationId("StackerState")
@dataclass
class StackerSimulationState(GenericSimulationState):
    lowerInputLaneState:BeltLaneState
    upperInputLaneState:BeltLaneState
    processingLaneState:BeltLaneState
    outputLaneState:BeltLaneState
    currentCollapseResult:ShapeCollapseResult|None

@_serializationId("TrashState")
class TrashSimulationState(GenericSimulationState):

    NUM_LANES = 4

    def __init__(self,laneStates:list[BeltLaneState]):
        self.laneStates = laneStates

@_serializationId("Virtual1InSimulationState")
@dataclass
class Virtual1InSimulationState(GenericSimulationState):
    inputConductorState:SignalConductorInputState

@_serializationId("Virtual2InSimulationState")
@dataclass
class Virtual2InSimulationState(GenericSimulationState):
    input0ConductorState:SignalConductorInputState
    input1ConductorState:SignalConductorInputState