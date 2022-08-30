class LatexHelper:

    def printMatrix(self, matrix):
        result = '\\begin{bmatrix} \n'
        for rowIndex in range(len(matrix)):
            for columnIndex in range(len(matrix)):
                if columnIndex != len(matrix) - 1:
                    result = result + str(matrix[rowIndex][columnIndex]) + ' & '
                else:
                    result = result + str(matrix[rowIndex][columnIndex])
            if rowIndex != len(matrix) - 1:
                result = result + '\\\\ \n'
            else:
                result = result + '\n'
        result = result + '\\end{bmatrix}'
        print(result)
