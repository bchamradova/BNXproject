class LocalMaximaHelper:

    @staticmethod
    def getLocalMaximaInList(list, lowestAcceptableValue=0):
        return [value for index, value in enumerate(list)
                if ((index == 0) or (list[index - 1] <= value))
                and ((index == len(list) - 1) or (value > list[index + 1])) and (value >= lowestAcceptableValue)]

    @staticmethod
    def getPositionedLocalMaximaInList(list, lowestAcceptableValue=0):
        maximums = []
        for index, value in enumerate(list):
            if ((index == 0) or (list[index - 1] <= value)) and (
                    (index == len(list) - 1) or (value > list[index + 1])) and (value >= lowestAcceptableValue):
                maximums.append(value)
            else:
                maximums.append(None)
        return maximums

    @staticmethod
    def getMaxima(list, lowestAcceptableValue=0):
        maximums = []
        for index, value in enumerate(list):
            if ((index == 0) or (list[index - 1] <= value)) and (
                    (index == len(list) - 1) or (value > list[index + 1])) and (value >= lowestAcceptableValue):
                maximums.append(value)
            else:
                maximums.append(None)
        return maximums

    @staticmethod
    def checkMaximumInCenter(surroundingPixelValues, surroundings=3):
        centerIndex = int(len(surroundingPixelValues) / 2)
        centerRadius = 1
        maxValue = (max(map(max, surroundingPixelValues)))
        for i in range(centerIndex - centerRadius, centerIndex + centerRadius + 1):
            for j in range(centerIndex - centerRadius, centerIndex + centerRadius + 1):
                if surroundingPixelValues[i][j] == maxValue:
                    return True
        return False

