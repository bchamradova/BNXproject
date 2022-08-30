class FileToImageResultWithBounds:
    def __init__(self):
        self.resultRatios = []
        self.lowerBounds = []

    def addResult(self, result, lowerBound):
        self.lowerBounds.append(lowerBound)
        self.resultRatios.append(result)


class FileToImageResultWithRanges:
    def __init__(self):
        self.resultRatios = []
        self.surroundingsRanges = []

    def addResult(self, result, surroundingRange):
        self.surroundingsRanges.append(surroundingRange)
        self.resultRatios.append(result)
