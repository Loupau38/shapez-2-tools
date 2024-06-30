import sys
import os
import pathlib
import base64
import gzip
import json

BUILDING_BP_TYPE = "Building"
ISLAND_BP_TYPE = "Island"

def alpha8Fix(bp:dict):

    if bp["BP"].get("$type",BUILDING_BP_TYPE) == BUILDING_BP_TYPE:
        for building in bp["BP"]["Entries"]:
            if building["T"] == "MergerTShapeInternalVariant":
                building["R"] = (building.get("R",0)-1) % 4

def alpha17Fix(bp:dict) -> None:

    CHANGED_ISLAND_IDS = {
        "LayoutMinerCompact" : "ShapeMinerLayout"
    }

    if bp["BP"].get("$type",BUILDING_BP_TYPE) == ISLAND_BP_TYPE:
        for island in bp["BP"]["Entries"]:
            island["T"] = CHANGED_ISLAND_IDS.get(island["T"],island["T"])

def alpha19Fix(bp:dict) -> None:

    CHANGED_ISLAND_IDS = {
        "Layout_1"                    : "Layout_Normal_1",
        "LayoutTunnelEntrance"        : "Layout_SpaceBeltTunnel_Entrance",
        "LayoutTunnelExit"            : "Layout_SpaceBeltTunnel_Exit",
        "ShapeMinerLayout"            : "Layout_ShapeMiner",
        "ChainMiner"                  : "Layout_ShapeMinerExtension",
        "TrainProducer"               : "Layout_TrainProducer_Blue",
        "Layout_2"                    : "Layout_Normal_2",
        "LayoutFluidExtractor"        : "Layout_FluidMiner",
        "Layout_3_L"                  : "Layout_Normal_3_L",
        "Layout_4_Quad_TwoNotches"    : "Layout_Normal_4_2x2",
        "Layout_4_T"                  : "Layout_Normal_4_T",
        "Layout_5_Cross"              : "Layout_Normal_5_Cross",
        "Layout_9_Quad_TopAllNotches" : "Layout_Normal_9_3x3"
    }

    def fixBuildingBp(bp:dict) -> None:

        def encodeLen(string:bytes) -> bytes:
            stringLen = len(string)
            if stringLen == 0:
                stringLen = -1
            return stringLen.to_bytes(2,"little",signed=True)

        def fixShapeGen(shapeGen:bytes) -> bytes:
            shapeGenWithoutLen = shapeGen[2:]
            if shapeGenWithoutLen == b"":
                return shapeGen
            if shapeGenWithoutLen.startswith((b"shapecrate:",b"fluidcrate:")):
                newShapeGen = b"shape:CuCuCuCu"
            else:
                newShapeGen = b"shape:" + shapeGenWithoutLen.removeprefix(b"shape:").replace(b"p",b"m")
            return encodeLen(newShapeGen) + newShapeGen

        def fixFluidGen(fluidGen:bytes) -> bytes:
            fluidGen = fluidGen[2:]
            newFluidGen = fluidGen.replace(b"p",b"m")
            return encodeLen(newFluidGen) + newFluidGen

        itemProducer = "SandboxItemProducerDefaultInternalVariant"
        fluidProducer = "SandboxFluidProducerDefaultInternalVariant"
        constantGen = "ConstantSignalDefaultInternalVariant"

        for entry in bp["Entries"]:

            entryType = entry["T"]
            if entryType not in (itemProducer,fluidProducer,constantGen):
                continue

            extraData = base64.b64decode(entry["C"])

            if entryType == itemProducer:
                newExtraData = fixShapeGen(extraData)
            elif entryType == fluidProducer:
                newExtraData = fixFluidGen(extraData)
            else:
                genType = extraData[0]
                genValue = extraData[1:]
                if genType == 6:
                    newExtraData = bytes([6]) + fixShapeGen(genValue)
                elif genType == 7:
                    newExtraData = bytes([7]) + fixFluidGen(genValue)
                else:
                    continue

            entry["C"] = base64.b64encode(newExtraData).decode()

    if bp["BP"].get("$type",BUILDING_BP_TYPE) == BUILDING_BP_TYPE:
        fixBuildingBp(bp["BP"])
    else:
        for island in bp["BP"]["Entries"]:
            island["T"] = CHANGED_ISLAND_IDS.get(island["T"],island["T"])
            if island.get("B") is not None:
                fixBuildingBp(island["B"])

def alpha20Fix(bp:dict) -> None:

    def fixBuildingBp(bp:dict) -> None:

        def encodeLen(string:bytes) -> bytes:
            stringLen = len(string)
            if stringLen == 0:
                stringLen = -1
            return stringLen.to_bytes(2,"little",signed=True)

        def fixShapeGen(shapeGen:bytes) -> bytes:
            shapeGen = shapeGen[2:]
            if shapeGen == b"":
                return bytes([0])
            return bytes([1,1]) + encodeLen(shapeGen) + shapeGen.removeprefix(b"shape:").replace(b"k",b"u")

        def fixFluidGen(fluidGen:bytes) -> bytes:
            if fluidGen == bytes([255,255]):
                return bytes([0])
            return b"\x01" + fluidGen.removeprefix(b"\x07\x00color-").replace(b"k",b"u")

        itemProducer = "SandboxItemProducerDefaultInternalVariant"
        fluidProducer = "SandboxFluidProducerDefaultInternalVariant"
        constantGen = "ConstantSignalDefaultInternalVariant"

        for entry in bp["Entries"]:

            entryType = entry["T"]
            if entryType not in (itemProducer,fluidProducer,constantGen):
                continue

            extraData = base64.b64decode(entry["C"])

            if entryType == itemProducer:
                newExtraData = fixShapeGen(extraData)
            elif entryType == fluidProducer:
                newExtraData = fixFluidGen(extraData)
            else:
                genType = extraData[0]
                genValue = extraData[1:]
                if genType == 6:
                    newExtraData = bytes([6]) + fixShapeGen(genValue)
                elif genType == 7:
                    newExtraData = bytes([7]) + fixFluidGen(genValue)
                else:
                    continue

            entry["C"] = base64.b64encode(newExtraData).decode()

    if bp["BP"].get("$type",BUILDING_BP_TYPE) == BUILDING_BP_TYPE:
        fixBuildingBp(bp["BP"])
    else:
        for island in bp["BP"]["Entries"]:
            if island.get("B") is not None:
                fixBuildingBp(island["B"])

def alpha21Fix(bp:dict) -> None:

    CHANGED_BUILDING_IDS = {
        "BeltDefaultRightInternalVariant"    : "BeltDefaultLeftInternalVariantMirrored",
        "Splitter1To2RInternalVariant"       : "Splitter1To2LInternalVariantMirrored",
        "Merger2To1RInternalVariant"         : "Merger2To1LInternalVariantMirrored",
        "Lift1DownRightInternalVariant"      : "Lift1DownLeftInternalVariantMirrored",
        "Lift1UpRightInternalVariant"        : "Lift1UpLeftInternalVariantMirrored",
        "Lift2DownRightInternalVariant"      : "Lift2DownLeftInternalVariantMirrored",
        "Lift2UpRightInternalVariant"        : "Lift2UpLeftInternalVariantMirrored",
        "CutterMirroredInternalVariant"      : "CutterDefaultInternalVariantMirrored",
        "StackerMirroredInternalVariant"     : "StackerDefaultInternalVariantMirrored",
        "PipeRightInternalVariant"           : "PipeLeftInternalVariantMirrored",
        "PipeUpRightInternalVariant"         : "PipeUpLeftInternalVariantMirrored",
        "Pipe2UpRightInternalVariant"        : "Pipe2UpLeftInternalVariantMirrored",
        "WireDefaultRightInternalVariant"    : "WireDefaultLeftInternalVariantMirrored",
        "WireDefault1UpRightInternalVariant" : "WireDefault1UpLeftInternalVariantMirrored",
        "WireDefault2UpRightInternalVariant" : "WireDefault2UpLeftInternalVariantMirrored"
    }

    def fixBuildingBp(bp:dict) -> None:
        for entry in bp["Entries"]:
            entry["T"] = CHANGED_BUILDING_IDS.get(entry["T"],entry["T"])

    if bp["BP"].get("$type",BUILDING_BP_TYPE) == BUILDING_BP_TYPE:
        fixBuildingBp(bp["BP"])
    else:
        for island in bp["BP"]["Entries"]:
            if island.get("B") is not None:
                fixBuildingBp(island["B"])

def alpha22_2Fix(bp:dict) -> None:

    CHANGED_BUILDING_IDS = {
        "FluidBridgeSenderInternalVariant"   : "FluidPortSenderInternalVariant",
        "FluidBridgeReceiverInternalVariant" : "FluidPortReceiverInternalVariant"
    }
    REMOVED_BUILDING_IDS = [
        "BlobLauncherInternalVariant",
        "BlobCatcherInternalVariant"
    ]

    def fixBuildingBp(bp:dict) -> None:
        newEntries = []
        for entry in bp["Entries"]:
            if entry["T"] not in REMOVED_BUILDING_IDS:
                entry["T"] = CHANGED_BUILDING_IDS.get(entry["T"],entry["T"])
                newEntries.append(entry)
        bp["Entries"] = newEntries

    if bp["BP"].get("$type",BUILDING_BP_TYPE) == BUILDING_BP_TYPE:
        fixBuildingBp(bp["BP"])
    else:
        for island in bp["BP"]["Entries"]:

            if island.get("B") is not None:
                fixBuildingBp(island["B"])
                if len(island["B"]["Entries"]) == 0:
                    island.pop("B")

            spaceBelt = "Layout_SpaceBeltNode"
            spacePipe = "Layout_SpacePipeNode"
            rail = "Layout_RailNode"

            islandType = island["T"]
            if islandType in (spaceBelt,spacePipe,rail):
                extra = base64.b64decode(island["C"])

                if islandType in (spaceBelt,spacePipe):
                    extra = b"\x14" + extra
                elif islandType == rail:
                    extra = b"\x0a" + extra

                island["C"] = base64.b64encode(extra).decode()

def alpha22_3Fix(bp:dict) -> None:

    bp["BP"]["$type"] = bp["BP"].get("$type",BUILDING_BP_TYPE)

    if bp["BP"]["$type"] == ISLAND_BP_TYPE:
        for entry in bp["BP"]["Entries"]:
            if entry.get("C") in (None,""):
                entry["C"] = base64.b64encode(bytes([0])).decode()

def allVersionFix(bp:str) -> str:

    decodedBP = json.loads(gzip.decompress(base64.b64decode(bp.removeprefix("SHAPEZ2-1-").removesuffix("$"))))
    bpVersion = decodedBP["V"]

    for version,func in [
        (1024,alpha8Fix),
        (1040,alpha17Fix),
        (1045,alpha19Fix),
        (1057,alpha20Fix),
        (1064,alpha21Fix),
        (1067,alpha22_2Fix),
        (1071,alpha22_3Fix)
    ]:
        if bpVersion < version:
            func(decodedBP)

    encodedBP = "SHAPEZ2-1-" + base64.b64encode(gzip.compress(json.dumps(decodedBP,separators=(",",":")).encode())).decode() + "$"

    return encodedBP

def main() -> None:

    outputToStdOut = False

    if not os.isatty(0):
        inputtedBP = sys.stdin.read().strip()
        outputToStdOut = True

    elif len(sys.argv) > 1:
        inputtedBP = sys.argv[1].strip()

    else:
        print("Input either :")
        print("- A blueprint code directly")
        print("- A path to a blueprint file (will create a copy for the fixed version)")
        print("- A path to a folder containing blueprint files (will recursively also take files inside sub-folders) (will create a copy of the base folder for the fixed version)")
        inputtedBP = input(">").strip()

    if inputtedBP.startswith("SHAPEZ2-1-"):

        fixedBP = allVersionFix(inputtedBP)
        if outputToStdOut:
            sys.stdout.write(fixedBP)
        else:
            print()
            print("Fixed blueprint :")
            print()
            print(fixedBP)
            print()
            input("Press enter to exit")

    elif pathlib.Path(inputtedBP).is_file():

        with open(inputtedBP,encoding="utf-8") as f:
            rawBP = f.read()
        fixedBP = allVersionFix(rawBP)
        *pathStart, extension = inputtedBP.split(".")
        newPath = ".".join(pathStart) + ".fixed." + extension
        with open(newPath,"w",encoding="utf-8") as f:
            f.write(fixedBP)
        if outputToStdOut:
            sys.stdout.write(newPath)
        else:
            print(f"Wrote fixed blueprint to {newPath}")
            input("Press enter to exit")

    else:

        def fixDir(dirPath:pathlib.Path,fixedDirPath:pathlib.Path) -> None:
            os.makedirs(fixedDirPath,exist_ok=True)
            for dirEntry in os.scandir(dirPath):
                if dirEntry.is_dir():
                    fixDir(pathlib.Path(dirEntry.path),pathlib.Path(fixedDirPath,dirEntry.name))
                elif dirEntry.name.endswith(".spz2bp"):
                    with open(dirEntry.path,encoding="utf-8") as f:
                        rawBP = f.read()
                    fixedBP = allVersionFix(rawBP)
                    with open(pathlib.Path(fixedDirPath,dirEntry.name),"w",encoding="utf-8") as f:
                        f.write(fixedBP)
        inputtedDir = pathlib.Path(inputtedBP)
        fixedDirPath = pathlib.Path(inputtedDir.parent,inputtedDir.name+".fixed")
        fixDir(inputtedDir,fixedDirPath)
        if outputToStdOut:
            sys.stdout.write(str(fixedDirPath))
        else:
            print(f"Wrote fixed blueprints to {fixedDirPath}")
            input("Press enter to exit")

if __name__ == "__main__":
    main()