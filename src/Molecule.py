from src.FluorescentMark import FluorescentMark
from src.LineEquation import LineEquation
from typing import List


class Molecule:
    FOV_DIMENSION = 2048
    PIXEL_TO_NUCLEOTIDE_RATIO = 375

    def __init__(self, moleculeLength: int, startFOV: int, startX: int, startY: int, endFOV: int, endX: int, endY: int):

        self.moleculeLength = moleculeLength

        self.startFOV = startFOV
        self.startX = startX
        self.startY = startY
        self.endFOV = endFOV
        self.endX = endX
        self.endY = endY

        # only molecles with same startFOV and endFOV
        self.totalStartY = self.startY + (self.startFOV - 1) * self.FOV_DIMENSION
        self.totalEndY = self.endY + (self.endFOV - 1) * self.FOV_DIMENSION

        self.fluorescentMarks: List[FluorescentMark] = []

        self.lineEquation: LineEquation = LineEquation((startX, self.totalStartY), (endX, self.totalEndY))

    def addFluorescentMark(self, fluorescentMark: FluorescentMark) -> None:
        self.fluorescentMarks.append(fluorescentMark)

    def createFluorescentMarksFromArray(self, marks) -> None:
        for nucleotideDistance in marks:
            pixelDistance = int(nucleotideDistance / self.PIXEL_TO_NUCLEOTIDE_RATIO)
            point = self.lineEquation.getCoordinatesInDistanceFromFirstPoint(pixelDistance)
            markX = point[0]
            markY = point[1]
            fluorescentMark = FluorescentMark(markX, markY, pixelDistance)
            self.addFluorescentMark(fluorescentMark)

    def isMoleculeLengthCorrect(self) -> bool:
        if (self.moleculeLength == (self.totalEndY - self.totalStartY + 1) * self.PIXEL_TO_NUCLEOTIDE_RATIO):
            return True
        else:
            print(str(self.moleculeLength)
                  + " vs "
                  + str((self.totalEndY - self.totalStartY + 1) * self.PIXEL_TO_NUCLEOTIDE_RATIO))
            print(str(self.endY) + " " + str(self.startY))
            print(str(self.endFOV) + " " + str(self.startFOV))
            return False

    def __str__(self) -> str:
        marksString = ""
        for mark in self.fluorescentMarks:
            marksString += "\t" + str(mark) + "\n"
        return "startFOV: " + str(self.startFOV) + " startX: " + str(self.startX) + " startY: " + str(self.totalStartY) \
               + " endFOV: " + str(self.endFOV) + " endX: " + str(self.endX) + " endY: " + str(self.totalEndY) \
               + "\n" + marksString
