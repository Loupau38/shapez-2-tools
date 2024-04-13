import sys
import os
import pathlib
import base64
import gzip
import json

CHANGED_ISLAND_IDS = {
    "Layout_1" : "Layout_Normal_1",
    "LayoutTunnelEntrance" : "Layout_SpaceBeltTunnel_Entrance",
    "LayoutTunnelExit" : "Layout_SpaceBeltTunnel_Exit",
    "ShapeMinerLayout" : "Layout_ShapeMiner",
    "ChainMiner" : "Layout_ShapeMinerExtension",
    "TrainProducer" : "Layout_TrainProducer_Blue",
    "Layout_2" : "Layout_Normal_2",
    "LayoutFluidExtractor" : "Layout_FluidMiner",
    "Layout_3_L" : "Layout_Normal_3_L",
    "Layout_4_Quad_TwoNotches" : "Layout_Normal_4_2x2",
    "Layout_4_T" : "Layout_Normal_4_T",
    "Layout_5_Cross" : "Layout_Normal_5_Cross",
    "Layout_9_Quad_TopAllNotches" : "Layout_Normal_9_3x3"
}

def fixBp(bp:str) -> str:

    def fixBuildingBp(bp:dict) -> None:

        def encodeLen(string:bytes) -> bytes:
            stringLen = len(string)
            if stringLen == 0:
                stringLen = -1
            return stringLen.to_bytes(2,"little",signed=True)

        def fixShapeGen(shapeGen:bytes) -> bytes:
            shapeGen = shapeGen[2:]
            if shapeGen.startswith((b"shapecrate:",b"fluidcrate:")):
                newShapeGen = b"shape:CuCuCuCu"
            else:
                newShapeGen = b"shape:" + shapeGen.removeprefix(b"shape:").replace(b"p",b"m")
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

    decodedBP = json.loads(gzip.decompress(base64.b64decode(bp.removeprefix("SHAPEZ2-1-").removesuffix("$"))))

    if decodedBP["BP"]["$type"] == "Building":
        fixBuildingBp(decodedBP["BP"])
    else:
        for island in decodedBP["BP"]["Entries"]:
            island["T"] = CHANGED_ISLAND_IDS.get(island["T"],island["T"])
            if island.get("B") is not None:
                fixBuildingBp(island["B"])

    return "SHAPEZ2-1-" + base64.b64encode(gzip.compress(json.dumps(decodedBP,separators=(",",":")).encode())).decode() + "$"

def main() -> None:

    if len(sys.argv) > 1:
        inputtedBP = sys.argv[1]
    else:
        print("Input either :")
        print("- A blueprint code directly")
        print("- A path to a blueprint file (will create a copy for the fixed version)")
        print("- A path to a folder containing blueprint files (will recursively also take files inside sub-folders) (will create a copy of the base folder for the fixed version)")
        inputtedBP = input(">")

    if inputtedBP.startswith("SHAPEZ2-1-"):

        print()
        print("Fixed blueprint :")
        print()
        print(fixBp(inputtedBP))
        print()
        input("Press enter to exit")

    elif pathlib.Path(inputtedBP).is_file():

        with open(inputtedBP,encoding="utf-8") as f:
            rawBP = f.read()
        fixedBP = fixBp(rawBP)
        *pathStart, extension = inputtedBP.split(".")
        newPath = ".".join(pathStart) + ".fixed." + extension
        with open(newPath,"w",encoding="utf-8") as f:
            f.write(fixedBP)

    else:

        def fixDir(dirPath:pathlib.Path,fixedDirPath:pathlib.Path) -> None:
            os.makedirs(fixedDirPath,exist_ok=True)
            for dirEntry in os.scandir(dirPath):
                if dirEntry.is_dir():
                    fixDir(pathlib.Path(dirEntry.path),pathlib.Path(fixedDirPath,dirEntry.name))
                elif dirEntry.name.endswith(".spz2bp"):
                    with open(dirEntry.path,encoding="utf-8") as f:
                        rawBP = f.read()
                    fixedBP = fixBp(rawBP)
                    with open(pathlib.Path(fixedDirPath,dirEntry.name),"w",encoding="utf-8") as f:
                        f.write(fixedBP)
        inputtedDir = pathlib.Path(inputtedBP)
        fixDir(inputtedDir,pathlib.Path(inputtedDir.parent,inputtedDir.name+".fixed"))

if __name__ == "__main__":
    main()