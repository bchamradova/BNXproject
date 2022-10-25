from src import constants
from src.BNXFile.BNXFileReader import BNXFileReader
from src.Exception.EndOfBNXFileException import EndOfBNXFileException
from src.Helpers.LocalMaximaHelper import LocalMaximaHelper
from src.ImageAnalysis.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
import numpy as np


def getCenterOfMass(values, surroundingsSize=1):
    vals = np.array(values)
    center = (vals * np.mgrid[0:vals.shape[0], 0:vals.shape[1]]).sum(1).sum(1) / vals.sum()
    nucleotidePosition = [
        constants.PIXEL_TO_NUCLEOTIDE_RATIO * point - constants.PIXEL_TO_NUCLEOTIDE_RATIO * (surroundingsSize - 0.5)
        for point in center
    ]
    return nucleotidePosition


def getCountOfNotCentered(nucleotidePositions):
    count = 0
    for position in nucleotidePositions:
        if position[0] > constants.PIXEL_TO_NUCLEOTIDE_RATIO or \
                position[1] > constants.PIXEL_TO_NUCLEOTIDE_RATIO or \
                position[0] < 0 or \
                position[1] < 0:
            count += 1

    return count


if __name__ == '__main__':

    # [x for x in signal.argrelextrema(nick_signal, np.greater)[0] if nick_signal[x] >= median*snr]
    imageAnalyzer = FluorescentMarkImageAnalyzer(
        'C:\\Users\\blank\\Documents\\7. semestr\\semestrální projektk\\BNXproject\\files\\images\\B1_CH2_C001.png')
    reader = BNXFileReader(
        'C:\\Users\\blank\\Documents\\7. semestr\\semestrální projektk\\BNXproject\\files\\bnx\\4QVZ_ScanRange_1-1_filtered.filtered.bnx')
    reader.open()
    surroundingsSize = 3
    maxCounts = np.zeros(surroundingsSize, dtype=np.uint8)
    sum = np.zeros(surroundingsSize, dtype=np.uint8)
    while True:
        try:
            molecule = reader.getNextMolecule()
        except EndOfBNXFileException:
            break

        values, positions = imageAnalyzer.getPotentialMarksOnMolecule(molecule)

        nupos = np.empty((surroundingsSize,), dtype=object)
        nupos[...]=[[] for _ in range(surroundingsSize)]
        for index,potentialMark in enumerate(positions):

            for i in range(1,surroundingsSize+1):
                surroundingValues = imageAnalyzer.getSurroundingValues(potentialMark[0], potentialMark[1], i, shape='c')
                nupos[i-1].append(getCenterOfMass(surroundingValues, i))

        for i in range(surroundingsSize):
            outOfCenterCount = getCountOfNotCentered(nupos[i])
            sum[i] += outOfCenterCount
            if outOfCenterCount > maxCounts[i]:
                maxCounts[i]=outOfCenterCount

    print(maxCounts, sum)
    # porovnat maxima molekul s ch1 souborem
    # udelat na x symetrickou masku a udelat z toho filtr ktery se pak da aplikovat na najiti posunu
