import math

from src.BNXFile.BNXFileReader import BNXFileReader
from src.Exception.EndOfBNXFileException import EndOfBNXFileException
from src.FileToImageResult import FileToImageResultWithBounds, FileToImageResultWithRanges
from src.ImageAnalysis.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
from src.Helpers.Graph.GraphVisualizer import GraphVisualizer
from src.Helpers.LocalMaximaHelper import LocalMaximaHelper


class ValidityChecker:

    def checkMaximumInCenter(self, surroundingPixelValues):
        centerIndex = int(len(surroundingPixelValues) / 2)
        centerRadius = 1
        maxValue = (max(map(max, surroundingPixelValues)))
        for i in range(centerIndex - centerRadius, centerIndex + centerRadius + 1):
            for j in range(centerIndex - centerRadius, centerIndex + centerRadius + 1):
                if surroundingPixelValues[i][j] == maxValue:
                    return True
        return False

    def getDistanceBetweenCenterAndMaximum(self, surroundingPixelValues):
        centerIndex = int(len(surroundingPixelValues) / 2)
        maxValue = 0
        maxIndices = (0, 0)
        for i in range(len(surroundingPixelValues)):
            for j in range(len(surroundingPixelValues)):
                if surroundingPixelValues[i][j] > maxValue:
                    maxValue = surroundingPixelValues[i][j]
                    maxIndices = (i, j)
        return math.sqrt((maxIndices[0] - centerIndex) ** 2 + (maxIndices[1] - centerIndex) ** 2)

    def getFileToImageStatistics(self, BNXFilename: str, imageFilename: str, closeSurroundings=3, minValue=0):
        fileReader = BNXFileReader(BNXFilename)
        fileReader.open()

        imageAnalyzer = FluorescentMarkImageAnalyzer(imageFilename)
        # imageAnalyzer.open()

        correctCount = 0
        incorrectCount = 0
        distanceSum = 0
        maxDistance = 0

        while True:
            try:
                molecule = fileReader.getNextMolecule()
            except EndOfBNXFileException:
                break

            if not (molecule.startFOV == molecule.endFOV):
                # todo move to bnx reader
                continue

            for fluorescentMark in molecule.fluorescentMarks:
                # todo check molecules interfering
                values = imageAnalyzer.getFluorescentMarkSurroundingValues(fluorescentMark, closeSurroundings)

                if imageAnalyzer.getPixelValue(fluorescentMark.posX, fluorescentMark.posY) < minValue:
                    continue

                if self.checkMaximumInCenter(values):
                    correctCount += 1

                else:
                    incorrectCount += 1
                    distance = self.getDistanceBetweenCenterAndMaximum(values)
                    distanceSum += distance
                    if distance > maxDistance:
                        maxDistance = distance

        print("correct: " + str(correctCount) + " incorrect: " + str(incorrectCount))
        print("ratio:" + str(correctCount / (correctCount + incorrectCount)))
        print("average distance from center when not correct: " + str(distanceSum / incorrectCount))
        print("max distance " + str(maxDistance))
        return correctCount / (correctCount + incorrectCount)

    def getFileToImageStatisticsValidityComparedByRanges(self, BNXFilename: str, imageFilename: str,
                                                         countOfCloseSurroundingRanges, maxLowerBound,
                                                         lowerBoundStep=100):
        graphDataIndexedBySurroundingRanges = {}
        for closeSurrounding in range(3, countOfCloseSurroundingRanges + 1):
            resultForIndex = FileToImageResultWithBounds()

            for lowerBound in range(0, maxLowerBound + lowerBoundStep, lowerBoundStep):
                result = self.getFileToImageStatistics(BNXFilename, imageFilename, closeSurrounding, lowerBound)
                print(result)
                resultForIndex.addResult(result, lowerBound)

            graphDataIndexedBySurroundingRanges[closeSurrounding] = resultForIndex

        gv = GraphVisualizer()
        gv.showFileToImageStatisticsComparedByRanges(graphDataIndexedBySurroundingRanges)

    def getFileToImageStatisticsValidityComparedByLowerBounds(self, BNXFilename: str, imageFilename: str,
                                                              countOfCloseSurroundingRanges, maxLowerBound,
                                                              lowerBoundStep=100):
        graphDataIndexedByUpperBounds = {}
        for lowerBound in range(250, maxLowerBound + lowerBoundStep, lowerBoundStep):
            resultForIndex = FileToImageResultWithRanges()
            for closeSurrounding in range(3, countOfCloseSurroundingRanges + 1):
                result = self.getFileToImageStatistics(BNXFilename, imageFilename, closeSurrounding, lowerBound)
                print(result)
                resultForIndex.addResult(result, closeSurrounding)

            graphDataIndexedByUpperBounds[lowerBound] = resultForIndex

        gv = GraphVisualizer()
        gv.showFileToImageStatisticsComparedByLowerBounds(graphDataIndexedByUpperBounds)

    def getImageToFileGraphs(self, BNXFilename: str, imageFilename: str):
        fileReader = BNXFileReader(BNXFilename)
        fileReader.open()

        imageAnalyzer = FluorescentMarkImageAnalyzer(imageFilename)
        # imageAnalyzer.open()

        for i in range(5):
            try:
                molecule = fileReader.getNextMolecule()
            except EndOfBNXFileException:
                break

            pixelValuesOnLine = imageAnalyzer.getPixelValuesOnMoleculeLine(molecule)
            interpolatedPixelValuesOnLine = imageAnalyzer.getInterpolatedPixelValuesOnMoleculeLine(molecule)

            gv = GraphVisualizer()
            gv.showComparedImageAndBnxValues(pixelValuesOnLine,
                                             imageAnalyzer.getPositionedFluorescentMarkValues(molecule),
                                             LocalMaximaHelper.getPositionedLocalMaximaInList(pixelValuesOnLine))

            gv.showComparedInterpolatedValues(pixelValuesOnLine,
                                              interpolatedPixelValuesOnLine)

            gv.showComparedImageAndBnxValues(interpolatedPixelValuesOnLine,
                                             imageAnalyzer.getPositionedInterpolatedFluorescentMarkValues(molecule),
                                             LocalMaximaHelper.getPositionedLocalMaximaInList(
                                                 interpolatedPixelValuesOnLine))

    def getImageToFileStatistics(self, BNXFilename: str, imageFilename: str):
        fileReader = BNXFileReader(BNXFilename)
        fileReader.open()

        imageAnalyzer = FluorescentMarkImageAnalyzer(imageFilename)
        # imageAnalyzer.open()

        for lowerBound in range(0, 600, 50):
            maxLengthDifference = 0
            lengthDifferenceSum = 0
            sameLengthCount = 0
            count = 0
            fileReader = BNXFileReader(BNXFilename)
            fileReader.open()
            while True:
                try:
                    molecule = fileReader.getNextMolecule()
                except EndOfBNXFileException:
                    break
                count += 1

                #pixelValuesOnLine, pixelPositions = imageAnalyzer.getPotentialMarksOnMolecule(molecule, lowerBound)
                pixelValuesOnLine, pixelPositions = imageAnalyzer.getPixelValuesOnMoleculeLine(molecule)

                maximaMarksCount = len(LocalMaximaHelper.getLocalMaximaInList(pixelValuesOnLine, lowerBound))
                #maximaMarksCount=len(pixelPositions)
                bnxMarksCount = len(imageAnalyzer.getFluorescentMarkValuesBiggerThan(molecule, lowerBound))
                lengthDifference = abs(bnxMarksCount - maximaMarksCount)
                lengthDifferenceSum += lengthDifference

                if lengthDifference > maxLengthDifference:
                    maxLengthDifference = lengthDifference
                if lengthDifference == 0:
                    sameLengthCount += 1

                '''print("-                                            -")
                print(maximaMarksCount)
                print((self.getLocalMaximaInList(pixelValuesOnLine, lowerBound)))
                print(bnxMarksCount)
                print(imageAnalyzer.getFluorescentMarkValuesBiggerThan(molecule, lowerBound))'''

            print('bound: ' + str(lowerBound))
            print("max difference: " + str(maxLengthDifference))
            print("average difference: " + str(lengthDifferenceSum / count))
            print("same length count: " + str(sameLengthCount) + " of total: " + str(count))
