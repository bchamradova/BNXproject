from src.BNXFile.BNXFileReader import BNXFileReader
from src.Exception.EndOfBNXFileException import EndOfBNXFileException
from src.Filesystem.BNXFilesystem import BNXFilesystem
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
def getMarkDistances(scan):
    bnxReader = BNXFileReader(BNXFilesystem.getBNXByScan(scan))
    bnxReader.open()
    distances = []
    while True:
        try:
            molecule = bnxReader.getNextMolecule()
        except EndOfBNXFileException:
            break
        distances.extend(molecule.getDistancesBetweenMarks())
    print('average distance', np.mean(distances))
    print('median', np.median(distances))
    print('min', np.amin(distances))
    print('max', np.amax(distances))
    print('median', np.std(distances))

    sns.boxplot(distances)
    plt.show()
    sns.histplot(distances)
    plt.show()
    return distances



if __name__ == '__main__':
    getMarkDistances(1)
