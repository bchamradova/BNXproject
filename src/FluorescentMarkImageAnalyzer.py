from PIL import Image
import numpy as np
from src.Molecule import Molecule
from src.FluorescentMark import FluorescentMark


class FluorescentMarkImageAnalyzer:

    def __init__(self, filename: str):
        self.filename: str = filename

    def open(self) -> None:
        self.image = Image.open(self.filename)

    def getPixelValue(self, x: int, y: int):
        return self.image.getpixel((x, y))

    def getSurroundingValues(self, x: int, y: int, width: int):
        matrixWidth = 2 * width + 1
        surroundings = [[0 for i in range(matrixWidth)] for j in range(matrixWidth)]
        startingX = x - width
        startingY = y - width
        for i in range(matrixWidth):
            for j in range(matrixWidth):
                try:
                    surroundings[i][j] = self.getPixelValue(startingX + i, startingY + j)
                except IndexError:
                    surroundings[i][j] = 0

        return surroundings

    def getFluorescentMarkSurroundingValues(self, fluorescentMark: FluorescentMark, width: int = 1):
        return self.getSurroundingValues(fluorescentMark.posX, fluorescentMark.posY, width)
