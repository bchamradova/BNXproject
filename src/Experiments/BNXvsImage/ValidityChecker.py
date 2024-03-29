import csv
import math
import pandas as pd
import numpy as np
import progressbar

from src.BNXFile.BNXFileReader import BNXFileReader
from src.Exception.EndOfBNXFileException import EndOfBNXFileException
from src.Exception.ImageDoesNotExist import ImageDoesNotExist
from src.Exception.UndefinedFilterException import UndefinedFilterException
from src.FileToImageResult import FileToImageResultWithBounds, FileToImageResultWithRanges
from src.Filesystem.BNXFilesystem import BNXFilesystem
from src.Filesystem.ImageFilesystem import ImageFilesystem
from src.ImageAnalysis.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
from src.Helpers.Graph.GraphVisualizer import GraphVisualizer
from src.Helpers.LocalMaximaHelper import LocalMaximaHelper
from src.ImageAnalysis.MoleculeDetector import MoleculeDetector
import argparse

from src.ImageAnalysis.GaussianFilteredImageAnalyzer import GaussianFilteredImageAnalyzer
from src.ImageAnalysis.MeanFilteredImageAnalyzer import MeanFilteredImageAnalyzer
from src.ImageAnalysis.MedianFilteredImageAnalyzer import MedianFilteredImageAnalyzer

# definition of image filter used
# FluorescentMarkImageAnalyzer = FluorescentMarkImageAnalyzer
# FluorescentMarkImageAnalyzer = MeanFilteredImageAnalyzer
# FluorescentMarkImageAnalyzer = MedianFilteredImageAnalyzer
# FluorescentMarkImageAnalyzer = GaussianFilteredImageAnalyzer

class ValidityChecker:

    def checkMaximumInCenter(self, surroundingPixelValues, centerRadius=0):
        centerIndex = int(len(surroundingPixelValues) / 2)
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

    def getFileToImageStatistics(self, BNXFilename: str, imageFilename: str, closeSurroundings=3, minValue=0,
                                 useLine=False):
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
                molecule = fileReader.getNextMolecule(useLine)
            except EndOfBNXFileException:
                break

            if not (molecule.startFOV == molecule.endFOV):
                continue

            for fluorescentMark in molecule.fluorescentMarks:
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

        for i in range(10):
            try:
                molecule = fileReader.getNextMolecule()
            except EndOfBNXFileException:
                break

            pixelValuesOnLine, coordsOnLine = imageAnalyzer.getPixelValuesOnMoleculeLine(molecule)
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

                # pixelValuesOnLine, pixelPositions = imageAnalyzer.getPotentialMarksOnMolecule(molecule, lowerBound)
                pixelValuesOnLine, pixelPositions = imageAnalyzer.getPixelValuesOnMoleculeLine(molecule)

                maximaMarksCount = len(LocalMaximaHelper.getLocalMaximaInList(pixelValuesOnLine, lowerBound))
                # maximaMarksCount=len(pixelPositions)
                bnxMarksCount = len(imageAnalyzer.getFluorescentMarkValuesBiggerThan(molecule, lowerBound))
                lengthDifference = abs(bnxMarksCount - maximaMarksCount)
                lengthDifferenceSum += lengthDifference

                if lengthDifference > maxLengthDifference:
                    maxLengthDifference = lengthDifference
                if lengthDifference == 0:
                    sameLengthCount += 1

            print('bound: ' + str(lowerBound))
            print("max difference: " + str(maxLengthDifference))
            print("average difference: " + str(lengthDifferenceSum / count))
            print("same length count: " + str(sameLengthCount) + " of total: " + str(count))

    def getFileToImageStatisticsByScan(self, scan, filterValue=0, surroundingsSize=3, useLineForMolecule=True):
        fileReader = BNXFileReader(BNXFilesystem.getBNXByScan(scan))
        fileReader.open()
        filename = ''
        missingImages = set()
        c = correctCount = incorrectCount = 0
        bar = progressbar.ProgressBar(maxval=fileReader.moleculeCount,
                                      widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        while True:
            c += 1
            if c % 100 != 0:
                fileReader.skipMolecule()
                continue
            try:
                molecule = fileReader.getNextMolecule(useLineForMolecule)
            except EndOfBNXFileException:
                break
            bar.update(c)

            try:
                currentFilename = ImageFilesystem.getImageByScanAndRunAndColumn(scan, molecule.runId, molecule.column)
            except ImageDoesNotExist:
                missingImages.add((molecule.runId, molecule.column))
                continue

            if currentFilename != filename:
                filename = currentFilename
                imageAnalyzer = FluorescentMarkImageAnalyzer(filename)

            if not (molecule.startFOV == molecule.endFOV):
                continue

            for fluorescentMark in molecule.fluorescentMarks:
                if imageAnalyzer.getPixelValue(fluorescentMark.posX, fluorescentMark.posY) < filterValue:
                    continue

                values = imageAnalyzer.getFluorescentMarkSurroundingValues(fluorescentMark, surroundingsSize)

                if self.checkMaximumInCenter(values):
                    correctCount += 1
                else:
                    incorrectCount += 1
        bar.finish()
        print(f'finished scan validity check, but {len(missingImages)} images were missing for scan {scan}')
        return correctCount, incorrectCount

    def getImageToFileStatisticsForScan(self, scan, filterValue=0, surroundingsSize=3, useLineForMolecule=True):
        fileReader = BNXFileReader(BNXFilesystem.getBNXByScan(scan))
        fileReader.open()
        filename = ''
        c = correctCount = incorrectCount = 0
        diffs = []
        while True:
            try:
                molecule = fileReader.getNextMolecule(True)
                # using line for fluorescent mark retrieval is faster and the count is the same for both options
            except EndOfBNXFileException:
                break
            c += 1
            if c % 100 != 0:
                continue
            print(c)

            currentFilename = ImageFilesystem.getImageByScanAndRunAndColumn(scan, molecule.runId, molecule.column)
            if currentFilename != filename:
                filename = currentFilename
                imageAnalyzer = FluorescentMarkImageAnalyzer(filename)

            if useLineForMolecule:
                pixelValuesOnLine, pixelPositions = imageAnalyzer.getPixelValuesOnMoleculeLine(molecule)
                maximaMarksCount = len(LocalMaximaHelper.getLocalMaximaInList(pixelValuesOnLine, filterValue))

            else:
                potentialMarks, potentialMarksPositions = imageAnalyzer.getPotentialMarksOnMolecule(molecule,
                                                                                                    filterValue,
                                                                                                    surroundingsSize)
                maximaMarksCount = len(potentialMarks)

            bnxMarksCount = len(imageAnalyzer.getFluorescentMarkValuesBiggerThan(molecule, filterValue))

            lengthDifference = maximaMarksCount - bnxMarksCount if bnxMarksCount != 0 else None
            diffs.append(lengthDifference)
            if lengthDifference == 0:
                correctCount += 1
            else:
                incorrectCount += 1

        return correctCount, incorrectCount, diffs

    def getImageToFileStatisticsWithCoordinatesCheck(self, scan, filterValue=0, surroundingsSize=3,
                                                     useLineForMolecule=True):
        fileReader = BNXFileReader(BNXFilesystem.getBNXByScan(scan))
        fileReader.open()
        filename = ''
        missingImages = set()
        c = correctCount = incorrectCount = 0
        bar = progressbar.ProgressBar(maxval=fileReader.moleculeCount,
                                      widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        while True:
            c += 1
            if c % 100 != 0:
                fileReader.skipMolecule()
                continue
            try:
                molecule = fileReader.getNextMolecule(useLineForMolecule)
            except EndOfBNXFileException:
                break
            bar.update(c)

            try:
                currentFilename = ImageFilesystem.getImageByScanAndRunAndColumn(scan, molecule.runId, molecule.column)
            except ImageDoesNotExist:
                missingImages.add((molecule.runId, molecule.column))
                continue

            if currentFilename != filename:
                filename = currentFilename
                imageAnalyzer = FluorescentMarkImageAnalyzer(filename)

            if useLineForMolecule:
                potentialMarks = []
                potentialMarksPositions = []
                lineValues, linePositions = imageAnalyzer.getPixelValuesOnMoleculeLine(molecule)
                for i, linePos in enumerate(linePositions):
                    if lineValues[i] > filterValue and self.checkMaximumInCenter(
                            imageAnalyzer.getSurroundingValues(linePos[0], linePos[1], surroundingsSize)):
                        potentialMarks.append(lineValues[i])
                        potentialMarksPositions.append(linePos)

            else:
                potentialMarks, potentialMarksPositions = imageAnalyzer.getPotentialMarksOnMolecule(molecule,
                                                                                                    filterValue,
                                                                                                    surroundingsSize)

            moleculeMarksPositions = [coords.getCoordinates() for coords in molecule.fluorescentMarks]

            for pos in potentialMarksPositions:
                if pos in moleculeMarksPositions:
                    correctCount += 1
                else:
                    incorrectCount += 1
        bar.finish()
        if len(missingImages) != 0:
            print(f'finished scan validity check, but {len(missingImages)} images were missing for scan {scan}')
        return correctCount, incorrectCount

    def createDatasetWithMatchingIntensities(self, scan):
        fileReader = BNXFileReader(BNXFilesystem.getBNXByScan(scan))
        fileReader.open()
        filename = ''
        columns = ['bnx_intensity',
                   'bnx_snr',
                   'intensity',
                   'x',
                   'y',
                   'fov',
                   'scan',
                   'run',
                   'column']
        res = []
        while True:
            try:
                molecule = fileReader.getNextMolecule(
                    False)
            except EndOfBNXFileException:
                df = pd.DataFrame(res, columns=columns)
                df.to_csv('imageIntensities' + str(scan) + '.csv')
                return df

            currentFilename = ImageFilesystem.getImageByScanAndRunAndColumn(scan, molecule.runId, molecule.column)
            if currentFilename != filename:
                filename = currentFilename
                imageAnalyzer = FluorescentMarkImageAnalyzer(filename)

            for mark in molecule.fluorescentMarks:
                res.append([mark.BNXIntensity, mark.SNR, imageAnalyzer.getPixelValue(mark.posX, mark.posY), mark.posX,
                            mark.posY, molecule.startFOV, scan, molecule.runId, molecule.column])

    @staticmethod
    def checkMolecules(imageFilenames):
        allowedDistance = 5
        pairDistances = []
        pixelDistances = []
        found = notFound = 0
        for imageFilename in imageFilenames:
            scan, run, column = ImageFilesystem.getScanAndRunAndColumnFromPath(imageFilename)
            bnxReader = BNXFileReader(BNXFilesystem.getBNXByScan(scan))
            bnxReader.open()
            BNXmolecules = []

            while True:
                try:
                    molecule = bnxReader.getNextMolecule()
                except EndOfBNXFileException:
                    break
                if molecule.runId == run and molecule.column == column:
                    BNXmolecules.append((molecule.startX, molecule.totalStartY, molecule.endX, molecule.totalEndY))
            detectedMolecules = MoleculeDetector.detectMoleculeCoordinates(imageFilename)

            BNXmolecules = np.array(BNXmolecules)
            detectedMolecules = np.array([(x1, y1, x2, y2) for ((x1, y1), (x2, y2)) in detectedMolecules])

            BNXlineCenters = (BNXmolecules[:, :2] + BNXmolecules[:, 2:]) / 2.0
            detectedLineCenters = (detectedMolecules[:, :2] + detectedMolecules[:, 2:]) / 2.0

            pairs = []
            alreadyPairedBNX = set()
            bestBNXDistances = [math.inf] * len(BNXmolecules)

            for detectedIndex in range(len(detectedMolecules)):
                minDist = math.inf
                bestMatchIndex = None
                for moleculeIndex in range(len(BNXmolecules)):
                    distance = math.dist(detectedLineCenters[detectedIndex], BNXlineCenters[moleculeIndex])
                    if distance < minDist and distance < allowedDistance:
                        if moleculeIndex not in alreadyPairedBNX or distance < bestBNXDistances[moleculeIndex]:
                            minDist = distance
                            bestMatchIndex = moleculeIndex
                if bestMatchIndex is not None:
                    pairs.append((detectedIndex, bestMatchIndex))
                    pixelDistances.append((abs(detectedMolecules[detectedIndex] - BNXmolecules[bestMatchIndex])))
                    pairDistances.append(minDist)
                    alreadyPairedBNX.add(bestMatchIndex)
                    bestBNXDistances[bestMatchIndex] = minDist
                    found += 1
                else:
                    pairs.append((detectedIndex, None))
                    notFound += 1

        print(pairDistances[pairDistances is not None])
        print('precision: ', found / (found + notFound))
        print('average pixel distance: ', np.mean(pixelDistances))
        print('average center distance: ', np.mean(pairDistances))
        return pixelDistances, pairDistances


if __name__ == '__main__':

    vc = ValidityChecker()
    parser = argparse.ArgumentParser(
        description='check simmilarity of data in image and bnx file based on selected attributes')
    parser.add_argument("-d", "--direction", help="direction of processing - 0: file to image, 1: image to file",
                        type=int, default=1)
    parser.add_argument("-s", "--scan", help="number of bnx scan to check", type=int, default=1)
    parser.add_argument("-l", "--line", help="type of mark detection - 1 for line, 0 for maxima", type=int, default=1)
    parser.add_argument("-t", "--threshold", help="minimal value of mark intensity to take into account", type=int,
                        default=0)
    parser.add_argument("-sr", "--surroundings",
                        help="size of surroundings to look for local maxima as a radius from center", type=int,
                        default=3)
    parser.add_argument("-f", "--filter", help="convolution filter used", type=str, default='gauss',
                        choices=['none', 'mean', 'median', 'gauss'])
    args = parser.parse_args()

    if args.filter == 'none':
        FluorescentMarkImageAnalyzer = FluorescentMarkImageAnalyzer
    elif args.filter == 'mean':
        FluorescentMarkImageAnalyzer = MeanFilteredImageAnalyzer
    elif args.filter == 'median':
        FluorescentMarkImageAnalyzer = MedianFilteredImageAnalyzer
    elif args.filter == 'gauss':
        FluorescentMarkImageAnalyzer = GaussianFilteredImageAnalyzer
    else:
        raise UndefinedFilterException

    if args.direction == 0:
        correct, incorrect = vc.getFileToImageStatisticsByScan(args.scan, filterValue=args.threshold,
                                                               surroundingsSize=args.surroundings,
                                                               useLineForMolecule=args.line)
    else:
        correct, incorrect = vc.getImageToFileStatisticsWithCoordinatesCheck(args.scan, filterValue=args.threshold,
                                                                             surroundingsSize=args.surroundings,
                                                                             useLineForMolecule=args.line)

    print(f'precision for selected arguments is {round(correct / (correct + incorrect), 4)}')
