from src.BNXFile.BNXFileReader import BNXFileReader
from src.Exception.EndOfBNXFileException import EndOfBNXFileException
from src.Helpers.LocalMaximaHelper import LocalMaximaHelper
from src.ImageAnalysis.NormalizedImageAnalyzer import NormalizedImageAnalyzer


class NormalizedImageChecker:

    def getCountsOfMarksComparedByMolecules(self, BNXfilename: str, imageFilename: str):
        columnImageAnalyzer = NormalizedImageAnalyzer(imageFilename, 'c')
        rowImageAnalyzer = NormalizedImageAnalyzer(imageFilename, 'r')
        combinedImageAnalyzer = NormalizedImageAnalyzer(imageFilename, 'cr')
        fileReader = BNXFileReader(BNXfilename)
        fileReader.open()
        count = 0
        maxLengthDifference = [0, 0, 0]
        lengthDifferenceSum = [0, 0, 0]
        sameLengthCount = [0, 0, 0]
        while True:
            try:
                molecule = fileReader.getNextMolecule()
            except EndOfBNXFileException:
                break
            count += 1
            columnMaximaCount, columnLengthDifference = self.getCountsForMolecule(columnImageAnalyzer, molecule)
            rowMaximaCount, rowLengthDifference = self.getCountsForMolecule(rowImageAnalyzer, molecule)
            combinedMaximaCount, combinedLengthDifference = self.getCountsForMolecule(combinedImageAnalyzer, molecule)

            maximaMarksCounts = [columnMaximaCount, rowMaximaCount, combinedMaximaCount]
            lengthDifferences = [columnLengthDifference, rowLengthDifference, combinedLengthDifference]

            for i in range(3):
                if lengthDifferences[i] > maxLengthDifference[i]:
                    maxLengthDifference[i] = lengthDifferences[i]
                lengthDifferenceSum[i] += lengthDifferences[i]
                if lengthDifferences[i] == 0:
                    sameLengthCount[i] += 1

            print(maximaMarksCounts)
            print(len(molecule.fluorescentMarks))

        for i in range(3):
            print(sameLengthCount[i])
            print(maxLengthDifference[i])
            print(lengthDifferenceSum[i] / count)
            print('----------')

    def getCountsForMolecule(self, imageAnalyzer: NormalizedImageAnalyzer, molecule):
        maxima = LocalMaximaHelper.getLocalMaximaInList(
            imageAnalyzer.getPixelValuesOnMoleculeLine(molecule), 0)

        maximaMarksCount = len(maxima)
        bnxMarksCount = len(molecule.fluorescentMarks)
        lengthDifference = abs(bnxMarksCount - maximaMarksCount)

        return maximaMarksCount, lengthDifference
