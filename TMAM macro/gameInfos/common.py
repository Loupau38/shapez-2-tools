import utils

def loadPos(raw:dict[str,int]) -> utils.Pos:
    return utils.Pos(
        raw.get("X",0),
        raw.get("Y",0),
        raw.get("Z",0)
    )

def loadDirection(raw:dict[str,int|dict]) -> dict[str,utils.Pos|utils.Rotation]:
    return {
        "pos" : loadPos(raw.get("Position_L",{})),
        "rot" : utils.Rotation(raw.get("Direction_L",0))
    }