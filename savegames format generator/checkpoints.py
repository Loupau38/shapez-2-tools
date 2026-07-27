import fixedint

checkpoints = sorted([
    "blob:start",
    "blob:end",
    "island",
    "buildings",
    "building",
    "fast-belt-path:start",
    "fast-belt-path:end",
    "belt-path-state:start",
    "belt-path-state:end",
    "TrainData",
    "super-chunk",
    "super-chunk:shape-resources",
    "super-chunk:fluid-resources"
],key=lambda s: s.lower())

def checkpointHash(checkpointId:str) -> int:
    h = fixedint.UInt32(523423)
    for c in checkpointId:
        char = fixedint.UInt32(ord(c))
        h += char
        h += h << fixedint.Int32(10)
        h ^= h >> fixedint.Int32(6)
    h += h << fixedint.Int32(3)
    h ^= h >> fixedint.Int32(11)
    h += h << fixedint.Int32(15)
    return int(h)

for c in checkpoints:
    r = checkpointHash(c)
    print("| ",end="")
    print(c,end="")
    print(" | ",end="")
    print(r,end="")
    print(" | `",end="")
    print(" ".join(hex(b)[2:].upper().zfill(2) for b in r.to_bytes(4,"little",signed=False)),end="")
    print("` |",end="")
    print()