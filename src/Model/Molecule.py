from src import constants
from src.Exception.ImageDoesNotExist import ImageDoesNotExist
from src.Filesystem.ImageFilesystem import ImageFilesystem
from src.Model.FluorescentMark import FluorescentMark
from src.Helpers.LineEquation import LineEquation
from typing import List
from PIL import Image
import numpy as np

class Molecule:
    FOV_DIMENSION = 2048
    PIXEL_TO_NUCLEOTIDE_RATIO = 375

    # MoleculeId	Length	AvgIntensity	SNR	NumberofLabels	OriginalMoleculeId	ScanNumber	ScanDirection	ChipId	Flowcell	RunId	Column	StartFOV	StartX	StartY	EndFOV	EndX	EndY
    def __init__(self, moleculeLength: int, startFOV: int, startX: int, startY: int, endFOV: int, endX: int, endY: int,
                 runID: int, column: int):

        self.moleculeLength = moleculeLength

        self.startFOV = startFOV
        self.startX = startX
        self.startY = startY
        self.endFOV = endFOV
        self.endX = endX
        self.endY = endY
        self.runId = runID
        self.column = column
        self.id = None
        self.avgIntensity = None
        self.SNR = None
        self.originalMoleculeId = None
        self.scanNumber = None
        self.scanDirection = None
        self.chipId = None
        self.flowcell = None

        self.fluorescentMarksDistances = []
        self.fluorescentMarkIntensities = []
        self.fluorescentMarkSNRs = []
        self.numberOfLabels = None

        # only molecules with same startFOV and endFOV
        self.totalStartY = self.startY + (self.startFOV - 1) * self.FOV_DIMENSION
        self.totalEndY = self.endY + (self.endFOV - 1) * self.FOV_DIMENSION

        self.fluorescentMarks: List[FluorescentMark] = []

        self.lineEquation: LineEquation = LineEquation((startX, self.totalStartY), (endX, self.totalEndY))

    def addFluorescentMark(self, fluorescentMark: FluorescentMark) -> None:
        self.fluorescentMarks.append(fluorescentMark)

    def createFluorescentMarksFromArray(self, marks, intensities, SNRs, scan, useLine = True) -> None:
        if not useLine:
            try:
                image = np.array(Image.open(ImageFilesystem.getImageByScanAndRunAndColumn(scan, self.runId, self.column)))
            except ImageDoesNotExist:
                useLine = True
        for index, nucleotideDistance in enumerate(marks):
            pixelDistance = int(nucleotideDistance / constants.PIXEL_TO_NUCLEOTIDE_RATIO)
            if useLine:
                point = self.lineEquation.getCoordinatesInDistanceFromFirstPoint(pixelDistance)
                markX = point[0]
                markY = point[1]
                if markY == constants.IMAGE_HEIGHT:
                    continue
                fluorescentMark = FluorescentMark(markX, markY, pixelDistance, intensities[index], SNRs[index], nucleotideDistance)
                self.addFluorescentMark(fluorescentMark)
            else:
                maxVal = 0
                maxX = self.startX
                for markX in range(self.startX, self.endX+1):
                    value = image[self.totalStartY + pixelDistance][markX]
                    if value > maxVal:
                        maxVal = value
                        maxX = markX
                fluorescentMark = FluorescentMark(maxX,self.totalStartY + pixelDistance, pixelDistance, intensities[index], SNRs[index],
                                                  nucleotideDistance)
                self.addFluorescentMark(fluorescentMark)

    def isMoleculeLengthCorrect(self) -> bool:
        if self.moleculeLength == (self.totalEndY - self.totalStartY + 1) * constants.PIXEL_TO_NUCLEOTIDE_RATIO:
            return True
        else:
            print(str(self.moleculeLength)
                  + " vs "
                  + str((self.totalEndY - self.totalStartY + 1) * constants.PIXEL_TO_NUCLEOTIDE_RATIO))
            print(str(self.endY) + " " + str(self.startY))
            print(str(self.endFOV) + " " + str(self.startFOV))
            return False

    def getDistancesBetweenMarks(self):
        distances = []
        for i,mark in enumerate(self.fluorescentMarks):
            if i == 0:
                continue
            distances.append(mark.nucleotideDistance -self.fluorescentMarks[i-1].nucleotideDistance)
        return distances

    def addFluorescentMarksArrays(self, distances, intensities, SNRs):
        self.fluorescentMarksDistances = distances
        self.fluorescentMarkIntensities = intensities
        self.fluorescentMarkSNRs = SNRs
        self.numberOfLabels = len(distances)

    def createBNXRecord(self):
        moleculeRow = constants.MOLECULE_ROW_IDENTIFIER + '\t'.join(map(str, [
            self.id,    self.moleculeLength,    self.avgIntensity,    self.SNR,    self.numberOfLabels,    self.originalMoleculeId,    self.scanNumber,
            self.scanDirection,    self.chipId,    self.flowcell,    self.runId,    self.column,    self.startFOV,
            self.startX,    self.startY,    self.endFOV,    self.endX, self.endY
        ]))
        distancesRow = constants.DISTANCES_ROW_IDENTIFIER + '\t'.join(map(str, self.fluorescentMarksDistances))
        intensitiesRow = constants.INTENSITIES_ROW_IDENTIFIER + '\t'.join(map(str, self.fluorescentMarkIntensities))
        SNRsRow = constants.SNRS_ROW_IDENTIFIER + '\t'.join(map(str, self.fluorescentMarkSNRs))
        return moleculeRow + '\n' + distancesRow + '\n' + SNRsRow + '\n' + intensitiesRow + '\n'
    def __str__(self) -> str:
        marksString = ""
        for mark in self.fluorescentMarks:
            marksString += "\t" + str(mark) + "\n"
        return "startFOV: " + str(self.startFOV) + " startX: " + str(self.startX) + " startY: " + str(self.totalStartY) \
               + " endFOV: " + str(self.endFOV) + " endX: " + str(self.endX) + " endY: " + str(self.totalEndY) \
               + "\n" + marksString
