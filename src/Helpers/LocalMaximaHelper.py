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
