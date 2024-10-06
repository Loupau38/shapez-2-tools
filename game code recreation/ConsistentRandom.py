from fixedint import Int32, UInt32
import typing

T = typing.TypeVar("T")

class ConsistentRandom:

    MBIG = Int32(Int32.maxval)
    MSEED = Int32(161803398)

    def StringToHash(seed:str) -> UInt32:

        hash = UInt32(523423)
        for char in seed:
            hash += UInt32(ord(char))
            hash += hash << 10
            hash ^= hash >> 6
        hash += hash << 3
        hash ^= hash >> 11
        hash += hash << 15
        return hash

    def __init__(self,seed:Int32|str) -> None:

        self.SeedArray = [Int32(0) for _ in range(56)]
        if type(seed) == Int32:
            self.SetSeed(seed)
        else:
            self.SetSeed(Int32(ConsistentRandom.StringToHash(seed))) # Loupau note : uint to int convertion seems to work like in C#

    def SetSeed(self,seed:Int32) -> None:

        subtraction = Int32(Int32.maxval) if seed == Int32(Int32.minval) else abs(seed)
        mj = ConsistentRandom.MSEED - subtraction
        self.SeedArray[55] = mj
        mk = Int32(1)
        for i in range(1,55):
            ii = 21 * i % 55
            self.SeedArray[ii] = mk
            mk = mj - mk
            if mk < 0:
                mk += ConsistentRandom.MBIG
            mj = self.SeedArray[ii]
        for k in range(1,5):
            for i in range(1,56):
                self.SeedArray[i] -= self.SeedArray[1+(i+30)%55]
                if self.SeedArray[i] < 0:
                    self.SeedArray[i] += ConsistentRandom.MBIG
        self.inext = Int32(0)
        self.inextp = Int32(21)

    # [0, int.MaxValue[
    def NextInt(self) -> Int32:

        locINext = self.inext
        locINextp = self.inextp

        locINext += Int32(1)
        if locINext >= 56:
            locINext = Int32(1)
        locINextp += Int32(1)
        if locINextp >= 56:
            locINextp = Int32(1)

        retVal = self.SeedArray[locINext] - self.SeedArray[locINextp]

        if retVal == ConsistentRandom.MBIG:
            retVal -= Int32(1)
        if retVal < 0:
            retVal += ConsistentRandom.MBIG

        self.SeedArray[locINext] = retVal

        self.inext = locINext
        self.inextp = locINextp

        return retVal

    # [min, max[
    def Next(self,minValue:Int32,maxValue:Int32) -> Int32:

        if minValue > maxValue:
            raise ValueError("minValue greater than maxValue")

        range = maxValue - minValue
        return self.NextInt() % range + minValue

    def TestPercentage(self,probability:Int32) -> bool:
        return self.Next(Int32(0),Int32(100)) < probability

    def TestPerMille(self,probabilityPerMille:Int32) -> bool:
        return self.Next(Int32(0),Int32(1000)) < probabilityPerMille

    def Choice(self,array:list[T]) -> T:

        if (array is None) or (len(array) == 0):
            raise NotImplementedError("should return default of T here")

        index = self.Next(Int32(0),Int32(len(array)))
        return array[index]

    def Shuffle(self,list:list[typing.Any]) -> None:

        count = len(list)
        while count > 1:
            count -= 1
            index = self.Next(Int32(0),Int32(count+1))
            (list[index],list[count]) = (list[count],list[index])