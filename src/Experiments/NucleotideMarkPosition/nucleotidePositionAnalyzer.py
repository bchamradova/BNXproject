import csv

from src import constants
from src.BNXFile.BNXFileReader import BNXFileReader
from src.Exception.EndOfBNXFileException import EndOfBNXFileException
from src.Filesystem.BNXFilesystem import BNXFilesystem
from src.Filesystem.ImageFilesystem import ImageFilesystem
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

def getPositionsForScan(scan):
    fileReader = BNXFileReader(BNXFilesystem.getBNXByScan(scan))
    fileReader.open()
    filename = ''
    results = ['calculatedY', 'expectedY', 'calculatedX', 'shape']

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
            surroundingValues = ia.getSurroundingValues(mark.posX, mark.posY, 1, shape='c')
            centerOfMass = getCenterOfMass(surroundingValues, 1)
            results.append([centerOfMass[0], mark.nucleotideDistance, centerOfMass[1], 'c'])
            surroundingValues = ia.getSurroundingValues(mark.posX, mark.posY, 1, shape='s')
            centerOfMass = getCenterOfMass(surroundingValues, 1)
            results.append([centerOfMass[0], mark.nucleotideDistance, centerOfMass[1], 's'])
    with open('results/centerOfMass_full_scan_1.csv', 'a') as file:
        wr = csv.writer(file)
        for row in results:
            wr.writerow(row)
    return results


if __name__ == '__main__':
    getPositionsForScan(1)
    print(getCenterOfMass([[0,0,0],[0,0,1],[0,0,0]]))
    # porovnat maxima molekul s ch1 souborem
    # udelat na x symetrickou masku a udelat z toho filtr ktery se pak da aplikovat na najiti posunu
