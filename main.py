import numpy as np

from src.BNXFileReader import BNXFileReader
from src.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
from src.LineEquation import LineEquation
from src.ValidityChecker import ValidityChecker
from src.Molecule import Molecule

if __name__ == '__main__':

    #0	2107	74625	7995.88	468.29	34	144	1	-1	chips,SN_4QZBVOWLPRIU7NWU,Run_566b5c70-cc4b-447e-9861-9c0c80d6c937,0	1	1	1	4	584	1701	4	584	1899
    #1	4579	6539	7507	9215	11080	12312	14554	16132	18695	20935	22645	23781	25652	27098	29795	31609	33887	35872	37816	39580	41365	43105	44252	45903	47532	49647	52280	53879	59742	61766	63618	64747	68092	71298	74625

    imageAnalyzer = FluorescentMarkImageAnalyzer("files/images/B1_CH2_C001.png")
    imageAnalyzer.open()
    print(np.matrix(
        imageAnalyzer.getSurroundingValues(
            584, (3 * Molecule.FOV_DIMENSION) + 1701 + 4579 / Molecule.PIXEL_TO_NUCLEOTIDE_RATIO, 5
        )
    ))

    print(np.matrix(
        imageAnalyzer.getSurroundingValues(
            584, (3 * Molecule.FOV_DIMENSION) + 1701 + 39580 / Molecule.PIXEL_TO_NUCLEOTIDE_RATIO, 5
        )
    ))

    #exit()

    validityChecker = ValidityChecker()
    validityChecker.getFileToImageStatistics("files/bnx/4QVZ_ScanRange_1-1_filtered.filtered.bnx","files/images/B1_CH2_C001.png")


