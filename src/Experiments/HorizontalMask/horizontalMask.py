import csv
import math

from src import constants
from src.BNXFile.BNXFileReader import BNXFileReader
from src.Exception.EndOfBNXFileException import EndOfBNXFileException
from src.Experiments.HorizontalMask.ShiftAnalyzer import ShiftAnalyzer
from src.Filesystem.BNXFilesystem import BNXFilesystem
from src.Filesystem.ImageFilesystem import ImageFilesystem
from src.Helpers.Graph.GraphVisualizer import GraphVisualizer
from src.Helpers.Latex.LatexFormatter import LatexHelper
from src.ImageAnalysis.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
import numpy as np
from datetime import datetime
from PIL import Image
from NormalDistribution import NormalDistribution
import pandas as pd

# scan 1 obsahuje 1674600 znacek
COUNT = 1000000
MIN_VALUE = 300
MIN_MID_RATIO = 1
MAX_MID_RATIO = 3
MIN_SIDE_RATIO = 1
MEAN = 0
DEVIATION = 1
PRECISION = 4

XINDEX = 0
YINDEX = 0


def selectBestRatio(midRatios, sideRatios, values, coords):
    # first sort by ratios, then find the bigger mid ratios
    idx = np.flip(np.argsort(sideRatios))

    sideSorted = np.array(sideRatios)[idx]
    midSorted = np.array(midRatios)[idx]
    valuesSorted = np.array(values)[idx]
    coordsSorted = np.array(coords)[idx]

    print(valuesSorted)
    print(coordsSorted)

    for i, sideRatio in enumerate(sideSorted):
        if midSorted[i] > 1:
            print('best mid ratio {0}, side ratio {1}, values {2} on coordinates {3} in image {4}'.format(
                midSorted[i], sideRatio, valuesSorted[i], (coordsSorted[i][0], coordsSorted[i][1]), coordsSorted[i][3]))
            return midSorted[i], sideRatio, valuesSorted[i]


def writeToDataset(values, coords, midRatios, sideRatios, axis, bnx):
    params = '#count: {0}, min mark value: {1}, mid ratio: {2}-{3}, side ratio: {4} \n'.format(COUNT, MIN_VALUE,
                                                                                               MIN_MID_RATIO,
                                                                                               MAX_MID_RATIO,
                                                                                               MIN_SIDE_RATIO)
    filename = 'files/' + axis + '_' + datetime.now().strftime("%Y_%m_%d-%H_%M_%S") + '.csv'
    lines = []
    # if run is not from bnx, it is average of both possible runs
    # x,y,left(upper),mid,right(lower),scan,run,column,midRatio,sideRatio
    header = ['x', 'y', 'left' if axis == 'x' else 'upper', 'mid', 'right' if axis == 'x' else 'lower',
              'scan', 'run', 'column', 'midRatio', 'sideRatio', 'isFromBNX']
    for i in range(len(values)):
        if values[i][0] != 0:
            line = [coords[i][0], coords[i][1], values[i][0], values[i][1], values[i][2], coords[i][2], coords[i][3],
                    coords[i][4], midRatios[i], sideRatios[i], bnx]
            lines.append(line)

    with open(filename, 'w', newline='') as file:
        file.write(params)
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(lines)


def checkPixel(ia, width, height, xSideRatios, xMidRatios, xRatioCoords, xValues, ySideRatios, yMidRatios, yRatioCoords,
               yValues):
    mid = ia.getPixelValue(width, height)
    global XINDEX, YINDEX
    if mid < MIN_VALUE:
        return

    left = ia.getPixelValue(width - 1, height)
    right = ia.getPixelValue(width + 1, height)
    upper = ia.getPixelValue(width, height - 1)
    lower = ia.getPixelValue(width, height + 1)

    xSideRatio = left / right if left < right else right / left
    xMidRatio = mid / ((left + right) / 2)

    scan, run, column = ImageFilesystem.getScanAndRunAndColumnFromPath(ia.filename)

    ySideRatio = upper / lower if upper < lower else lower / upper
    yMidRatio = mid / ((upper + lower) / 2)
    if MIN_MID_RATIO < yMidRatio < MAX_MID_RATIO and ySideRatio >= MIN_SIDE_RATIO:
        if MIN_MID_RATIO < xMidRatio < MAX_MID_RATIO and xSideRatio >= MIN_SIDE_RATIO:
            xMinRatioIndex = XINDEX
            # if xSideRatio > xSideRatios[xMinRatioIndex]:
            xSideRatios[xMinRatioIndex] = xSideRatio
            xMidRatios[xMinRatioIndex] = xMidRatio
            xRatioCoords[xMinRatioIndex] = (width, height, scan, run, column)
            xValues[xMinRatioIndex] = (left, mid, right)
            XINDEX += 1
            yMinRatioIndex = YINDEX
            # if ySideRatio > ySideRatios[yMinRatioIndex]:
            ySideRatios[yMinRatioIndex] = ySideRatio
            yMidRatios[yMinRatioIndex] = yMidRatio
            yRatioCoords[yMinRatioIndex] = (width, height, scan, run, column)
            yValues[yMinRatioIndex] = (upper, mid, lower)
            YINDEX += 1


def getSymmetricRatios(numberOfImages=np.inf, numberOfScans=43, bnx=None):
    xSideRatios = np.zeros(COUNT, dtype=float)
    xMidRatios = np.zeros(COUNT, dtype=float)
    # x,y,scan,run,column
    xRatioCoords = np.zeros(COUNT, dtype='i,i,i,f,i')
    xValues = np.zeros(COUNT, dtype='i,i,i')

    ySideRatios = np.zeros(COUNT, dtype=float)
    yMidRatios = np.zeros(COUNT, dtype=float)
    yRatioCoords = np.zeros(COUNT, dtype='i,i,i,f,i')
    yValues = np.zeros(COUNT, dtype='i,i,i')

    if bnx is None:
        for scanNumber in range(1, numberOfScans + 1):
            imageNumber = 0
            for imageFilename in ImageFilesystem.yieldAllImagesInScan(scanNumber):
                imageNumber += 1
                if imageNumber > numberOfImages:
                    break
                print(imageFilename)
                ia = FluorescentMarkImageAnalyzer(imageFilename)

                # ratios from 0 to 1, 1 being the best
                for width in range(1, constants.IMAGE_WIDTH - 1):
                    for height in range(1, constants.IMAGE_HEIGHT - 1):
                        checkPixel(ia, width, height, xSideRatios, xMidRatios, xRatioCoords, xValues, ySideRatios,
                                   yMidRatios, yRatioCoords, yValues)
    else:
        fileReader = BNXFileReader(bnx)
        fileReader.open()
        x = 0
        while True:
            try:
                molecule = fileReader.getNextMolecule()
                print(x / 142871)
                x += 1
            except EndOfBNXFileException:
                break
            image = ImageFilesystem.getImageByScanAndRunAndColumn(BNXFilesystem.getScanByBNX(bnx), molecule.runId,
                                                                  molecule.column)
            ia = FluorescentMarkImageAnalyzer(
                image)
            for mark in molecule.fluorescentMarks:
                width = mark.posX
                height = mark.posY
                if width == 0 or height == 0 or height == constants.IMAGE_HEIGHT or width == constants.IMAGE_WIDTH:
                    continue
                checkPixel(ia, width, height, xSideRatios, xMidRatios, xRatioCoords, xValues, ySideRatios, yMidRatios,
                           yRatioCoords, yValues)

    # GraphVisualizer.plotSymmetricRatios(xSideRatios, xMidRatios, 'x')
    # GraphVisualizer.plotSymmetricRatios(ySideRatios, yMidRatios, 'y')

    selectBestRatio(xMidRatios, xSideRatios, xValues, xRatioCoords)
    selectBestRatio(yMidRatios, ySideRatios, yValues, yRatioCoords)

    fromBNX = 0 if bnx is None else 1
    writeToDataset(xValues, xRatioCoords, xMidRatios, xSideRatios, 'x', fromBNX)
    writeToDataset(yValues, yRatioCoords, yMidRatios, ySideRatios, 'y', fromBNX)

    return [xMidRatios, xSideRatios, xValues, xRatioCoords], [yMidRatios, ySideRatios, yValues, yRatioCoords]




def checkShiftsForScan(scan, sigmaX, sigmaY, mean, dimension='2'):
    fileReader = BNXFileReader(BNXFilesystem.getBNXByScan(scan))
    fileReader.open()
    filename = ''
    results = ['mid', 'left', 'right', 'up', 'down', 'calculatedX','expectedDistance', 'calculatedDistance',  'expectedY', 'calculatedY']

    c = 0
    while True:
        try:
            molecule = fileReader.getNextMolecule(
                False)
        except EndOfBNXFileException:
            break
        c += 1
        if c % 1000 != 0:
            continue
        print(c)

        currentFilename = ImageFilesystem.getImageByScanAndRunAndColumn(scan, molecule.runId, molecule.column)
        if currentFilename != filename:
            filename = currentFilename
            ia = FluorescentMarkImageAnalyzer(filename)

        for mark in molecule.fluorescentMarks:
            mid = ia.getPixelValue(mark.posX, mark.posY)
            if mid>500:
                sides = (ia.getPixelValue(mark.posX - 1, mark.posY), ia.getPixelValue(mark.posX + 1, mark.posY))
                levels = (ia.getPixelValue(mark.posX, mark.posY - 1), ia.getPixelValue(mark.posX, mark.posY + 1))
                shiftX, shiftY = ShiftAnalyzer.getNucleotideShift2d(sides, levels, mid, sigmaX, sigmaY, mean)
                calculatedDistance = mark.nucleotideDistance + shiftY #wtf mark.nucleotideDistance%375 + constants.PIXEL_TO_NUCLEOTIDE_RATIO / 2 + shiftY
                results.append(
                    [mid, sides[0], sides[1], levels[0], levels[1], constants.PIXEL_TO_NUCLEOTIDE_RATIO / 2 + shiftX,
                     mark.nucleotideDistance, calculatedDistance,
                     mark.nucleotideDistance % constants.PIXEL_TO_NUCLEOTIDE_RATIO,
                     constants.PIXEL_TO_NUCLEOTIDE_RATIO / 2 + shiftY]
                )

    with open('files/results/horizontal_mask_scan_1.csv', 'a') as file:
        wr = csv.writer(file)
        for row in results:
            wr.writerow(row)
    return results


if __name__ == '__main__':

    SIGMAX = NormalDistribution.getSigmaFromK(NormalDistribution.getK(1.1725, MEAN, DEVIATION))
    SIGMAY = NormalDistribution.getSigmaFromK(NormalDistribution.getK(1.1263, MEAN, DEVIATION))

    #NormalDistribution.plot2DDistribution(SIGMAX, SIGMAY, (0,0))
    checkShiftsForScan(1, SIGMAX, SIGMAY, MEAN)
    #print(getNucleotideShift2d((379, 445), (1,1), 481, SIGMAX, SIGMAY, MEAN))  # melo by byt 185 poked %37
    #print(getNucleotideShift(379, 445, 481, SIGMAX))  # 5
