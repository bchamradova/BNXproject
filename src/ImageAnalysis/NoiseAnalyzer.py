import time
from PIL import Image

from src.BNXFile.BNXFileReader import BNXFileReader
from src.Filesystem.BNXFilesystem import BNXFilesystem
from src.Filesystem.ImageFilesystem import ImageFilesystem
from src.Helpers.Graph.GraphVisualizer import GraphVisualizer
from src.Model.Molecule import Molecule
from scipy.stats import norm
import numpy as np


class NoiseAnalyzer:
    IMAGE_WIDTH = 1024
    IMAGE_HEIGHT = 8192
    LIMIT = 250

    def __init__(self, filename, full=True):
        self.imageFilename = filename
        if full:
            self.imagePixelValues = self.getAllPixelValuesIndexed()

    def getAllPixelValues(self):
        return np.asarray(Image.open(self.imageFilename)).flatten()
        image = Image.open(self.imageFilename)
        values = []
        for x in range(self.IMAGE_WIDTH):
            for y in range(self.IMAGE_HEIGHT):
                values.append(image.getpixel((x, y)))
        return values

    def getPixelValuesInRange(self, xFrom: int, xTo: int, yFrom: int, yTo: int):
        image = Image.open(self.imageFilename)
        values = []
        for x in range(xFrom, xTo):
            for y in range(yFrom, yTo):
                values.append(image.getpixel((x, y)))
        return values

    def getAllPixelValuesIndexed(self):
        start = time.time()
        image = Image.open(self.imageFilename)
        values = [[0 for _ in range(self.IMAGE_WIDTH)] for _ in range(self.IMAGE_HEIGHT)]
        for x in range(self.IMAGE_WIDTH):
            for y in range(self.IMAGE_HEIGHT):
                values[y][x] = (image.getpixel((x, y)))
        # print(np.matrix(values))
        print('read image in ' + str(time.time() - start))
        return values

    def getValuesCounts(self, values):
        minValue = 0
        maxValue = max(values)
        valueCounts = [0 for _ in range(maxValue - minValue + 1)]
        maxValue = 0
        maxIndex = 0
        for value in values:
            valueCounts[value - minValue] += 1
            if valueCounts[value - minValue] > maxValue:
                maxValue = valueCounts[value - minValue]
                maxIndex = value - minValue

        # print("mean: " + str(maxIndex + minValue))
        return [value / len(values) for value in valueCounts[0:NoiseAnalyzer.LIMIT]]

    def getFOVValuesCounts(self):
        graphVisualizer = GraphVisualizer()
        for fov in range(4):
            values = self.getValuesCounts(
                self.getPixelValuesInRange(0, self.IMAGE_WIDTH, fov * Molecule.FOV_DIMENSION,
                                           (fov + 1) * Molecule.FOV_DIMENSION))
            graphVisualizer.gaussianDistribution(values, title='distribution in FOV' + str(fov + 1))

    def getFullValuesCounts(self):
        graphVisualizer = GraphVisualizer()
        values = self.getAllPixelValues()
        graphVisualizer.compareHistogramToNormalDistribution([pixel for pixel in values if pixel < NoiseAnalyzer.LIMIT])
        graphVisualizer.gaussianDistribution(self.getValuesCounts(values))

    def getDeviation(self):
        values = self.getAllPixelValues()
        mu, std = norm.fit([pixel for pixel in values if pixel < NoiseAnalyzer.LIMIT])
        return std

    def getColumnValuesMeans(self):
        means = []
        for column in range(self.IMAGE_WIDTH):
            means.append(self.getColumnMeanAndDeviation(column)[0])
        graphVisualizer = GraphVisualizer()
        graphVisualizer.showMeansValues(means, column=1)
        return means

    def getRowValuesMeans(self):
        means = []
        for row in range(self.IMAGE_HEIGHT):
            means.append(self.getRowMeanAndDeviation(row)[0])
        graphVisualizer = GraphVisualizer()
        graphVisualizer.showMeansValues(means, column=0)
        return means

    def getColumnValuesDeviations(self):
        deviations = []
        for column in range(self.IMAGE_WIDTH):
            deviations.append(self.getColumnMeanAndDeviation(column)[1])
        graphVisualizer = GraphVisualizer()
        graphVisualizer.showMeansValues(deviations, column=1)
        return deviations

    def getRowValuesDeviations(self):
        deviations = []
        for row in range(self.IMAGE_HEIGHT):
            deviations.append(self.getRowMeanAndDeviation(row)[1])
        graphVisualizer = GraphVisualizer()
        graphVisualizer.showMeansValues(deviations, column=0)
        return deviations

    def getColumnMeanAndDeviation(self, column):
        graphVisualizer = GraphVisualizer()
        values = []
        for row in range(self.IMAGE_HEIGHT):
            values.append(self.imagePixelValues[row][column])
        counts = self.getValuesCounts(values)
        mean = counts.index(max(counts))
        mu, std = norm.fit([pixel for pixel in values if pixel < NoiseAnalyzer.LIMIT])
        # print(str(mean))
        if std > 40:
            graphVisualizer.compareHistogramToNormalDistribution(
                [pixel for pixel in values if pixel < NoiseAnalyzer.LIMIT])
        return mu, std

    def getRowMeanAndDeviation(self, row):
        counts = self.getValuesCounts(self.imagePixelValues[row])
        mean = counts.index(max(counts))
        mu, std = norm.fit([pixel for pixel in self.imagePixelValues[row] if pixel < NoiseAnalyzer.LIMIT])
        # print(str(mean))
        return mu, std

    def getMoleculeMeanAndDeviation(self, molecule, noiseThreshold = 200):
        im = Image.open(self.imageFilename)
        moleculeCutout = im.crop((
                                 molecule.startX if molecule.startX < molecule.endX else molecule.endX, molecule.totalStartY,
                                 molecule.endX+1 if molecule.endX > molecule.startX else molecule.startX +1, molecule.totalEndY+1))
        noiseValues = np.asarray(moleculeCutout).flatten()
        underThreshold = np.where(noiseValues < noiseThreshold)

        return np.mean(noiseValues[underThreshold]),np.std(noiseValues[underThreshold])


if __name__== '__main__':
    na = NoiseAnalyzer(ImageFilesystem.getFirstImage(), full=False)
    bnxReader = BNXFileReader(BNXFilesystem.getFirstBNX())
    bnxReader.open()
    mol = bnxReader.getNextMolecule()
    print(na.getMoleculeMeanAndDeviation(mol,250))
