import sys

from PIL import Image
import numpy as np
import scipy.ndimage as ndimage

from src.Experiments.HorizontalMask.ShiftAnalyzer import ShiftAnalyzer
from src.Filesystem.ImageFilesystem import ImageFilesystem
from src.Helpers.MatrixHelper import MatrixHelper
from src.Model.Molecule import Molecule
from src.Model.FluorescentMark import FluorescentMark
from src import constants


class FluorescentMarkImageAnalyzer:

    def __init__(self, filename: str):
        self.filename: str = filename
        self.open()

    def open(self) -> None:
        self.image = Image.open(self.filename)

    def getPixelValue(self, x: int, y: int) -> int:
        return self.image.getpixel((x, y))

    #shape s=square c=circle
    def getSurroundingValues(self, x: int, y: int, width: int, shape='s'):
        matrixWidth = 2 * width + 1
        startingX = x - width
        startingY = y - width

        x, y = np.meshgrid(
            np.arange(startingX, startingX + matrixWidth),
            np.arange(startingY, startingY + matrixWidth))

        surroundings = np.array([int(self.getPixelValue(xi, yi)) for xi, yi in zip(x.flat, y.flat)]).reshape(matrixWidth, matrixWidth)

        if shape == 's':
            return surroundings
        else:
            return MatrixHelper.getCircularValuesFromMatrix(surroundings)


    def getFluorescentMarkSurroundingValues(self, fluorescentMark: FluorescentMark, width: int = 1, shape='s'):
        return self.getSurroundingValues(fluorescentMark.posX, fluorescentMark.posY, width, shape)

    def getPositionedFluorescentMarkValues(self, molecule: Molecule):
        marks = []
        count = 0
        for y in range(molecule.totalStartY, molecule.totalEndY):
            if y in [mark.posY for mark in molecule.fluorescentMarks]:
                marks.append(
                    self.getPixelValue(molecule.fluorescentMarks[count].posX, molecule.fluorescentMarks[count].posY))
                count += 1
            else:
                marks.append(None)
        return marks

    def getPositionedInterpolatedFluorescentMarkValues(self, molecule: Molecule):
        marks = []
        count = 0
        for y in range(molecule.totalStartY, molecule.totalEndY):
            if y in [mark.posY for mark in molecule.fluorescentMarks]:
                surroundings = self.getSurroundingValues(molecule.fluorescentMarks[count].posX,
                                                         molecule.fluorescentMarks[count].posY, 1)
                mean = np.matrix(surroundings).mean()
                marks.append(mean)
                count += 1
            else:
                marks.append(None)
        return marks

    def getFluorescentMarkValuesBiggerThan(self, molecule: Molecule, lowerBound: int):
        return [self.getPixelValue(mark.posX, mark.posY) for mark in molecule.fluorescentMarks if
                self.getPixelValue(mark.posX, mark.posY) > lowerBound]

    def getPixelValuesOnMoleculeLine(self, molecule):
        coordinatesOnLine = molecule.lineEquation.getPointsFromStartToEnd()
        x, y = zip(*coordinatesOnLine)
        pixelValuesOnLine = np.array([self.getPixelValue(x[i], y[i]) for i in range(len(coordinatesOnLine))])
        return pixelValuesOnLine, coordinatesOnLine

    def getInterpolatedPixelValuesOnMoleculeLine(self, molecule):
        coordinatesOnLine = molecule.lineEquation.getPointsFromStartToEnd()
        curveValues = []
        for point in coordinatesOnLine:
            surroundings = self.getSurroundingValues(point[0], point[1], 1)
            mean = np.matrix(surroundings).mean()
            curveValues.append(mean)

        return curveValues

    def getPotentialMarksOnMolecule(self, molecule, lowerBound=0, surroundings=3, border=0):
        width = abs(molecule.endX - molecule.startX) + 1 + 2 * border
        height = abs(molecule.totalEndY - molecule.totalStartY) + 1 + 2 * border
        startX = molecule.startX if molecule.startX < molecule.endX else molecule.endX - border
        endX = molecule.endX if molecule.startX < molecule.endX else molecule.startX
        np.set_printoptions(threshold=sys.maxsize)
        moleculeCutout = np.zeros((height, width), dtype=np.uint64)
        moleculePositions = np.zeros((height, width), dtype='i,i')
        for x in range(width):
            for y in range(height):
                posX = startX + x
                posY = molecule.totalStartY + y
                if posX >= 1042 or posY >= 8192:
                    continue
                moleculeCutout[y][x] = self.getPixelValue(posX, posY)
                moleculePositions[y][x] = (posX, posY)

        #surroundings should be based on bnx file (around 10 pixels)
        maxima = ndimage.maximum_filter(moleculeCutout, size=(surroundings*2+1, width)) #apply max filter (mask)
        maximaFiltered = np.where((maxima == moleculeCutout) & (maxima > lowerBound), moleculeCutout, 0) #filter small values
        potentialMarks = np.where((maximaFiltered > 0) & (maximaFiltered == maximaFiltered.max(axis=1, keepdims=True))) #choose the biggest for each row
        positions = list(zip(potentialMarks[1], potentialMarks[0])) #get coordinates
        marks = np.array([moleculeCutout[pos[1]][pos[0]] for pos in positions])

        return marks, [(pos[0] + startX, pos[1] + molecule.totalStartY) for pos in positions]

    def detectMarksOnMolecule(self, molecule, lowerBound=0, surroundings=3):
        intensities, positions = self.getPotentialMarksOnMolecule(molecule, lowerBound, surroundings)
        marksCount = len(positions)
        distances = np.zeros(marksCount, dtype='int')
        SNRs = np.zeros(marksCount, dtype='float')
        for i, position in enumerate(positions):
            x,y = position
            sides = self.image.getpixel((x-1,y)), self.image.getpixel((x+1,y)) #has to be from original image!
            levels = self.image.getpixel((x,y-1)), self.image.getpixel((x,y+1))
            shiftX,shiftY = ShiftAnalyzer.getNucleotideShift2d(
                sides, levels, self.image.getpixel((x,y)), constants.SIGMAX, constants.SIGMAY, (0,0)
            )
            distances[i] =(y - molecule.totalStartY) * constants.PIXEL_TO_NUCLEOTIDE_RATIO + shiftY
            SNRs[i] = round(intensities[i]/constants.NOISE_DEVIATION, 1)
        return distances, intensities, SNRs




