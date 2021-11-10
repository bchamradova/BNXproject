import numpy as np

from src.Molecule import Molecule
from src.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
from src.BNXFileReader import BNXFileReader
from src.Exception.EndOfBNXFileException import EndOfBNXFileException


class ValidityChecker:

    def checkMaximumInCenter(self, surroundingPixelValues):
        centerIndex = int(len(surroundingPixelValues)/2)
        if(surroundingPixelValues[centerIndex][centerIndex] == (max(map(max, surroundingPixelValues)))):
            return True
        return False

    def getFileToImageStatistics(self, BNXFilename: str, imageFilename):
        fileReader = BNXFileReader(BNXFilename)
        fileReader.open()

        imageAnalyzer = FluorescentMarkImageAnalyzer(imageFilename)
        imageAnalyzer.open()

        correctCount = 0
        incorrectCount = 0
        while True:
            try:
                molecule = fileReader.getNextMolecule()
            except EndOfBNXFileException:
                break

            if not (molecule.startFOV == molecule.endFOV):
                #todo move to bnx reader
                continue

            for fluorescentMark in molecule.fluorescentMarks:

                values = imageAnalyzer.getFluorescentMarkSurroundingValues(fluorescentMark, 2)
                #print(fluorescentMark)
                #print(np.matrix(values))

                if self.checkMaximumInCenter(values):
                    correctCount += 1
                else:
                    incorrectCount += 1

        print("correct: " + str(correctCount) + " incorrect: " + str(incorrectCount))