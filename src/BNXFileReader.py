from src.Molecule import Molecule
from src.Exception.EndOfBNXFileException import EndOfBNXFileException

class BNXFileReader:
    SEPARATOR = "\t"

    def __init__(self, filename: str, ignoreDifferentFOV = True):
        self.filename = filename
        #todo
        self.ignoreDifferentFOV = ignoreDifferentFOV

    def open(self) -> None:
        self.filePointer = open(self.filename, "r")
        lineCounter = 0
        lastLine = 0
        while self.filePointer.readline()[0] == "#":
            lineCounter += 1
            lastLine = self.filePointer.tell()
        #print("actual data starting at line: " + str(lineCounter))
        self.filePointer.seek(lastLine)

    def getNextMolecule(self) -> Molecule:
        moleculeLine = self.filePointer.readline()
        if not moleculeLine:
            raise EndOfBNXFileException("nothing more to read")
        molecule = self.getMoleculeFromLine(moleculeLine)
        fluorescentMarksLine = self.filePointer.readline()
        fluorescentMarks = self.getFluorescentMarkDistancesFromLine(fluorescentMarksLine)
        intensitiesLine = self.filePointer.readline()
        intensities = self.getFloatsFromLine(intensitiesLine)
        SNRsLine = self.filePointer.readline()
        SNRs = self.getFloatsFromLine(SNRsLine)
        molecule.createFluorescentMarksFromArray(fluorescentMarks, SNRs, intensities)

        return molecule

    def getMoleculeFromLine(self, line: str) -> Molecule:
        lineAttributes = self.parseLine(line)
        length = int(lineAttributes[2])
        moleculeAttributes = [int(attribute) for attribute in lineAttributes[-6:]]
        # todo hint object
        return Molecule(length, moleculeAttributes[0], moleculeAttributes[1], moleculeAttributes[2],
                        moleculeAttributes[3],
                        moleculeAttributes[4], moleculeAttributes[5])

    def getFluorescentMarkDistancesFromLine(self, line: str):
        lineAttributes = self.parseLine(line)
        # delete 1 from the beginning of line
        lineAttributes.pop(0)
        # delete lastMark
        lineAttributes.pop()
        return [int(value) for value in lineAttributes]

    def getFloatsFromLine(self, line:str):
        lineAttributes = self.parseLine(line)
        # delete Q from the beginning of line
        lineAttributes.pop(0)
        return [float(value) for value in lineAttributes]

    def parseLine(self, line):
        lineAttributes = line.strip().split(self.SEPARATOR)
        return lineAttributes
