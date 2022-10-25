import math
class MatrixHelper:

    @staticmethod
    def getCircularValuesFromMatrix(matrix):
        size = len(matrix)
        center = math.ceil(size/2)
        half = math.floor(size/2)
        for i in range(half):
            for cell in range(0,center-i-1):
                matrix[i][cell] = matrix[i][-1-cell] = matrix[-1-i][cell] = matrix[-1-i][-1-cell] = 0
        return matrix