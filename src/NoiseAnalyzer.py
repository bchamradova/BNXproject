import time
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt

from src.GraphVisualizer import GraphVisualizer
from src.Molecule import Molecule


class NoiseAnalyzer:
    IMAGE_WIDTH = 1024
    IMAGE_HEIGHT = 8192

    def getAllPixelValues(self, imageFilename: str):
        image = Image.open(imageFilename)
        values = []
        for x in range(self.IMAGE_WIDTH):
            for y in range(self.IMAGE_HEIGHT):
                values.append(image.getpixel((x, y)))
        return values

    def getPixelValuesInRange(self, imageFilename: str, xFrom: int, xTo: int, yFrom: int, yTo: int):
        image = Image.open(imageFilename)
        values = []
        for x in range(xFrom, xTo):
            for y in range(yFrom, yTo):
                values.append(image.getpixel((x, y)))
        return values

    def getAllPixelValuesIndexed(self, imageFilename: str):
        start = time.time()
        image = Image.open(imageFilename)
        values = [[0 for i in range(self.IMAGE_WIDTH)] for i in range(self.IMAGE_HEIGHT)]
        for x in range(self.IMAGE_WIDTH):
            for y in range(self.IMAGE_HEIGHT):
                values[y][x] = (image.getpixel((x, y)))
        # print(np.matrix(values))
        print('read image in ' + str(time.time() - start))
        return values

    def getValuesCounts(self, values):
        minValue = 0
        maxValue = max(values)
        valueCounts = [0 for i in range(maxValue - minValue + 1)]
        maxValue = 0
        maxIndex = 0
        for value in values:
            valueCounts[value - minValue] += 1
            if (valueCounts[value - minValue] > maxValue):
                maxValue = valueCounts[value - minValue]
                maxIndex = value - minValue

        # print("mean: " + str(maxIndex + minValue))
        return [value / len(values) for value in valueCounts[0:300]]

    def getFOVValuesCounts(self, imageFilename: str):
        graphVisualizer = GraphVisualizer()
        for fov in range(4):
            values = self.getValuesCounts(
                self.getPixelValuesInRange(imageFilename, 0, self.IMAGE_WIDTH, fov * Molecule.FOV_DIMENSION,
                                           (fov + 1) * Molecule.FOV_DIMENSION))
            graphVisualizer.gaussianDistribution(values, title='distribution in FOV' + str(fov + 1))

    def getFullValuesCounts(self, imageFilename: str):
        graphVisualizer = GraphVisualizer()
        values = self.getAllPixelValues(imageFilename)
        graphVisualizer.compareHistogramToNormalDistribution([pixel for pixel in values if pixel < 300])
        graphVisualizer.gaussianDistribution(self.getValuesCounts(values))

    def getColumnValuesMeans(self, imageFilename):
        means = []
        pixelValues = self.getAllPixelValuesIndexed(imageFilename)
        for column in range(self.IMAGE_WIDTH):
            values = []
            for row in range(self.IMAGE_HEIGHT):
                values.append(pixelValues[row][column])
            counts = self.getValuesCounts(values)
            mean = counts.index(max(counts))
            # print(str(mean))
            means.append(mean)
        graphVisualizer = GraphVisualizer()
        graphVisualizer.showMeansValues(means, column=1)
        return means

    def getRowValuesMeans(self, imageFilename):
        means = []
        pixelValues = self.getAllPixelValuesIndexed(imageFilename)
        for row in range(self.IMAGE_HEIGHT):
            counts = self.getValuesCounts(pixelValues[row])
            mean = counts.index(max(counts))
            # print(str(mean))
            means.append(mean)
        graphVisualizer = GraphVisualizer()
        graphVisualizer.showMeansValues(means, column=0)
        return means

    def removeOutliers(self, values):
        pass
