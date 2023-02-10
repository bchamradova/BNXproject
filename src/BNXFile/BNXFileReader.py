from src import constants
from src.Model.Molecule import Molecule
from src.Exception.EndOfBNXFileException import EndOfBNXFileException
import pandas as pd


class BNXFileReader:
    SEPARATOR = "\t"

    def __init__(self, filename: str, ignoreDifferentFOV=True):
        self.filename = filename
        # todo
        self.ignoreDifferentFOV = ignoreDifferentFOV

    def open(self) -> None:
        self.filePointer = open(self.filename, "r")
        lineCounter = 0
        lastLine = 0
        while self.filePointer.readline()[0] == "#":
            lineCounter += 1
            lastLine = self.filePointer.tell()
        # print("actual data starting at line: " + str(lineCounter))
        self.filePointer.seek(lastLine)

    def getNextMolecule(self, useLine = True) -> Molecule:
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
        molecule.createFluorescentMarksFromArray(fluorescentMarks, SNRs, intensities, useLine)

        return molecule

    def getMoleculeFromLine(self, line: str) -> Molecule:
        moleculeAttributes = self.parseLine(line)
        length = int(moleculeAttributes[2])
        return Molecule(int(length), int(moleculeAttributes[13]), int(moleculeAttributes[14]),
                        int(moleculeAttributes[15]), int(moleculeAttributes[16]), int(moleculeAttributes[17]),
                        int(moleculeAttributes[18]), int(moleculeAttributes[11]), int(moleculeAttributes[12]))

    def getFluorescentMarkDistancesFromLine(self, line: str):
        lineAttributes = self.parseLine(line)
        # delete 1 from the beginning of line
        lineAttributes.pop(0)
        # delete lastMark
        lineAttributes.pop()
        return [int(value) for value in lineAttributes]

    def getFloatsFromLine(self, line: str):
        lineAttributes = self.parseLine(line)
        # delete Q from the beginning of line
        lineAttributes.pop(0)
        return [float(value) for value in lineAttributes]

    def parseLine(self, line):
        lineAttributes = line.strip().split(self.SEPARATOR)
        return lineAttributes

    def prepareDatasetEA(self, scan: int):
        #x,y,fov - start
        cols = [
            'intensity',
            'snr',
            'x',
            'y',
            'fov',
            'avg_intensity',
            'avg_snr',
            'length',
            'marks_count',
            'scan',
            'run',
            'column',
            'x_diff'
        ]
        res=[]
        c=0
        while(True):
            moleculeLine = self.filePointer.readline()

            if not moleculeLine:
                df = pd.DataFrame(res, columns=cols)
                df.to_csv('bnxMarksEA_scan' + str(scan) + '.csv')
                print(df)
                return df
            moleculeLine = self.parseLine(moleculeLine)
            print(c)
            c += 1
            marksLine = self.filePointer.readline()
            snrLine = self.filePointer.readline()
            snrLine = self.parseLine(snrLine)
            intensitiesLine = self.filePointer.readline()
            intensitiesLine = self.parseLine(intensitiesLine)
            for i,snr in enumerate(snrLine[1:]):
                res.append( [
                float(intensitiesLine[i+1]),
                float(snr),
                int(moleculeLine[14]),
                int(moleculeLine[15]) * (int(moleculeLine[13])-1) * constants.FOV_SIZE,
                int(moleculeLine[13]),
                float(moleculeLine[3]),
                float(moleculeLine[4]),
                int(moleculeLine[2]),
                int(moleculeLine[5]),
                scan,
                int(moleculeLine[11]),
                int(moleculeLine[12]),
                abs(int(moleculeLine[14]) - int(moleculeLine[17]))
            ])
