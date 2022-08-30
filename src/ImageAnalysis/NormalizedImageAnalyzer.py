from src.ImageAnalysis.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
from src.ImageAnalysis.NoiseAnalyzer import NoiseAnalyzer as na


class NormalizedImageAnalyzer(FluorescentMarkImageAnalyzer):
    def __init__(self, filename, by='cr'):
        super().__init__(filename)
        self.by = by
        self.normalizedPixelValues = self.getPixelValuesNormalized()

    def getPixelValue(self, x: int, y: int) -> int:
        return self.normalizedPixelValues[y][x]

    def getPixelValuesNormalized(self):
        noiseAnalyzer = na(self.filename)

        # value of pixel = image intensity - column deviation
        if self.by == 'c':
            means = noiseAnalyzer.getColumnValuesMeans()
            return self.subtractMeans(column=means)
        # value of pixel = image intensity - row deviation
        elif self.by == 'r':
            means = noiseAnalyzer.getRowValuesMeans()
            return self.subtractMeans(row=means)
        # value of pixel = image intensity - row+column deviation/2
        elif self.by == 'cr':
            columnMeans = noiseAnalyzer.getColumnValuesMeans()
            rowMeans = noiseAnalyzer.getRowValuesMeans()
            return self.subtractMeans(row=rowMeans, column=columnMeans)

    def subtractMeans(self, row=None, column=None):
        normalizedPixelValues = [[0 for _ in range(na.IMAGE_WIDTH)] for _ in range(na.IMAGE_HEIGHT)]
        for x in range(na.IMAGE_WIDTH):
            for y in range(na.IMAGE_HEIGHT):
                # print(x,y)
                originalValue = super().getPixelValue(x, y)
                if (row is not None) and (column is not None):
                    normalizedPixelValues[y][x] = originalValue - (column[x] + row[y]) / 2
                elif row is not None:
                    normalizedPixelValues[y][x] = originalValue - row[y]
                elif column is not None:
                    normalizedPixelValues[y][x] = originalValue - column[x]
        return normalizedPixelValues