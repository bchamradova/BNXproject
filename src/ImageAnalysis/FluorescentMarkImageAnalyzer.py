import sys

from PIL import Image
import numpy as np
from src.Model.Molecule import Molecule
from src.Model.FluorescentMark import FluorescentMark
from src.ImageAnalysis.NoiseAnalyzer import NoiseAnalyzer


class FluorescentMarkImageAnalyzer:

    def __init__(self, filename: str):
        self.filename: str = filename
        self.open()

    def open(self) -> None:
        self.image = Image.open(self.filename)

    def getPixelValue(self, x: int, y: int) -> int:
        return self.image.getpixel((x, y))

    def getSurroundingValues(self, x: int, y: int, width: int):
        matrixWidth = 2 * width + 1
        surroundings = [[0 for _ in range(matrixWidth)] for _ in range(matrixWidth)]
        startingX = x - width
        startingY = y - width
        for i in range(matrixWidth):
            for j in range(matrixWidth):
                try:
                    surroundings[i][j] = self.getPixelValue(startingX + j, startingY + i)
                except IndexError:
                    surroundings[i][j] = 0

        return surroundings

    def getFluorescentMarkSurroundingValues(self, fluorescentMark: FluorescentMark, width: int = 1):
        return self.getSurroundingValues(fluorescentMark.posX, fluorescentMark.posY, width)

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
        pixelValuesOnLine = []
        for point in coordinatesOnLine:
            pixelValuesOnLine.append(self.getPixelValue(point[0], point[1]))
        return pixelValuesOnLine

    def getInterpolatedPixelValuesOnMoleculeLine(self, molecule):
        coordinatesOnLine = molecule.lineEquation.getPointsFromStartToEnd()
        curveValues = []
        for point in coordinatesOnLine:
            surroundings = self.getSurroundingValues(point[0], point[1], 1)
            mean = np.matrix(surroundings).mean()
            curveValues.append(mean)

        return curveValues
