import numpy as np
from src import constants
from src.Experiments.HorizontalMask.NormalDistribution import NormalDistribution


class ShiftAnalyzer():

    def __init__(self, deviationX, deviationY):
        self.deviationX = deviationX
        self.deviationY = deviationY
        self.normalDistribution = NormalDistribution(self.deviationX, self.deviationY)


    def getNucleotideShift(self,left, mid, right, deviation):
        pixelStart = -constants.PIXEL_TO_NUCLEOTIDE_RATIO / 2
        pixelEnd = constants.PIXEL_TO_NUCLEOTIDE_RATIO / 2
        closestDistance = np.inf
        closestShift = None

        for shift in np.arange(pixelStart, pixelEnd + 1, 1):
            position = shift / constants.PIXEL_TO_NUCLEOTIDE_RATIO
            midCdf = NormalDistribution.getCumulativeValueForRange((-0.5, 0.5), deviation, mean=position)
            rightCdf = NormalDistribution.getCumulativeValueForRange((0.5, 1.5), deviation, mean=position)
            leftCdf = NormalDistribution.getCumulativeValueForRange((-1.5, -0.5), deviation, mean=position)
            rightDiffFromDistribution = abs((rightCdf / midCdf) - (right / mid))
            leftDiffFromDistribution = abs((leftCdf / midCdf) - (left / mid))
            distance = rightDiffFromDistribution + leftDiffFromDistribution
            if distance < closestDistance:
                closestDistance = distance
                closestShift = shift
                # print(midCdf/leftCdf - mid/left)
                # print(midCdf/rightCdf- mid/right)

        return closestShift, closestDistance

    def getNucleotideShift2d(self, sides, levels, mid, deviationX, deviationY):
        closestDistance = np.inf
        closesShiftX = None
        closesShiftY = None

        pixelStartX = -constants.PIXEL_TO_NUCLEOTIDE_RATIO / 2 if sides[0] > sides[1] else 0
        pixelEndX = 0 if sides[0] > sides[1] else constants.PIXEL_TO_NUCLEOTIDE_RATIO / 2

        pixelStartY = -constants.PIXEL_TO_NUCLEOTIDE_RATIO / 2 if levels[0] > levels[1] else 0
        pixelEndY = 0 if levels[0] > levels[1] else constants.PIXEL_TO_NUCLEOTIDE_RATIO / 2

        for shiftX in np.arange(pixelStartX, pixelEndX, 10):
            for shiftY in np.arange(pixelStartY, pixelEndY, 10):
                positionX = shiftX / constants.PIXEL_TO_NUCLEOTIDE_RATIO
                positionY = shiftY / constants.PIXEL_TO_NUCLEOTIDE_RATIO
                # mean on sides/levels means that only the specific range for one dimension is checked. but position changes on both
                leftCdf = self.normalDistribution.getCumulativeValueForRange2d((-1.5, -0.5), (positionY, positionY),
                                                                          deviationX,
                                                                          deviationY,
                                                                          (positionX, positionY))
                rightCdf = self.normalDistribution.getCumulativeValueForRange2d((0.5, 1.5), (positionY, positionY),
                                                                           deviationX,
                                                                           deviationY,
                                                                           (positionX, positionY))
                midCdfSide = self.normalDistribution.getCumulativeValueForRange2d((-0.5, 0.5), (positionY, positionY),
                                                                             deviationX, deviationY,
                                                                             (positionX, positionY))
                midCdfLevel = self.normalDistribution.getCumulativeValueForRange2d((positionX, positionX), (-0.5, 0.5),
                                                                              deviationX, deviationY,
                                                                              (positionX, positionY))

                upCdf = self.normalDistribution.getCumulativeValueForRange2d((positionX, positionX), (-1.5, -0.5),
                                                                        deviationX,
                                                                        deviationY,
                                                                        (positionX, positionY))
                downCdf = self.normalDistribution.getCumulativeValueForRange2d((positionX, positionX), (0.5, 1.5),
                                                                          deviationX,
                                                                          deviationY,
                                                                          (positionX, positionY))

                rightDiffFromDistribution = abs((rightCdf / midCdfSide) - (sides[1] / mid))
                leftDiffFromDistribution = abs((leftCdf / midCdfSide) - (sides[0] / mid))
                upDiffFromDistribution = abs((upCdf / midCdfLevel) - (levels[0] / mid))
                downDiffFromDistribution = abs((downCdf / midCdfLevel) - (levels[1] / mid))
                distance = upDiffFromDistribution if levels[0] > levels[1] else downDiffFromDistribution
                if distance <= closestDistance:
                    closestDistance = distance
                    closesShiftX = shiftX
                    closesShiftY = shiftY
        # print(sides, levels, mid, closesShiftX, closesShiftY, closestDistance)
        return closesShiftX, closesShiftY