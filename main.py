import sys
import numpy as np

from src.BNXFile.BNXFileReader import BNXFileReader
from src.Experiments.SNR.SNRAnalyzer import SNRAnalyzer
from src.ImageAnalysis.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
from src.ImageAnalysis.NoiseAnalyzer import NoiseAnalyzer
from src.Experiments.NormalizedImage.NormalizedImageChecker import NormalizedImageChecker
from src.Experiments.BNXvsImage.ValidityChecker import ValidityChecker
from src.Exception.EndOfBNXFileException import EndOfBNXFileException



if __name__ == '__main__':

    '''s = SNRAnalyzer()
    s.getBNXSNRStats('files/bnx/4QVZ_ScanRange_1-1_filtered.filtered.bnx')
    s.getImageSNRStats('files/images/B1_CH2_C001.png')
    s.getImageSNRStatsForMolecules('files/bnx/4QVZ_ScanRange_1-1_filtered.filtered.bnx','files/images/B1_CH2_C001.png')
    exit()
    nic = NormalizedImageChecker()
    nic.getCountsOfMarksComparedByMolecules('files/bnx/4QVZ_ScanRange_1-1_filtered.filtered.bnx',
                                            'files/images/B1_CH2_C001.png')
    exit()

    
    na = NoiseAnalyzer('files/images/B1_CH2_C001.png')
    na.getFullValuesCounts()
    na.getFOVValuesCounts()
    na.getColumnValuesMeans()
    na.getRowValuesMeans()
    exit()'''

    # 0	2107	74625	7995.88	468.29	34	144	1	-1	chips,SN_4QZBVOWLPRIU7NWU,Run_566b5c70-cc4b-447e-9861-9c0c80d6c937,0	1	1	1	4	584	1701	4	584	1899
    # 1	4579	6539	7507	9215	11080	12312	14554	16132	18695	20935	22645	23781	25652	27098	29795	31609	33887	35872	37816	39580	41365	43105	44252	45903	47532	49647	52280	53879	59742	61766	63618	64747	68092	71298	74625

    imageAnalyzer = FluorescentMarkImageAnalyzer("files/images/B1_CH2_C001.png")
    imageAnalyzer.open()
    '''print(np.matrix(
        imageAnalyzer.getSurroundingValues(
            584, (3 * Molecule.FOV_DIMENSION) + 1701 + int(4579 / Molecule.PIXEL_TO_NUCLEOTIDE_RATIO), 5
        )
    ))

    print("--------")

    print(np.matrix(
        imageAnalyzer.getSurroundingValues(
            584, (3 * Molecule.FOV_DIMENSION) + 1701 + 39580 / Molecule.PIXEL_TO_NUCLEOTIDE_RATIO, 5
        )
    ))

    print(np.matrix(
        imageAnalyzer.getSurroundingValues(
            584, (3 * Molecule.FOV_DIMENSION) + 1701 + 39580 / Molecule.PIXEL_TO_NUCLEOTIDE_RATIO, 5
        )
    ))
    exit()'''

    validityChecker = ValidityChecker()
    validityChecker.getImageToFileStatistics("files/bnx/4QVZ_ScanRange_1-1_filtered.filtered.bnx",
                                             "files/images/B1_CH2_C001.png")
    exit()
    # validityChecker.getFileToImageStatistics("files/bnx/4QVZ_ScanRange_1-1_filtered.filtered.bnx","files/images/B1_CH2_C001.png", 1, 0)
    # validityChecker.getFileToImageStatisticsValidityComparedByRanges("files/bnx/4QVZ_ScanRange_1-1_filtered.filtered.bnx", "files/images/B1_CH2_C001.png", 5, 500, 50)
    validityChecker.getFileToImageStatisticsValidityComparedByLowerBounds(
        "files/bnx/4QVZ_ScanRange_1-1_filtered.filtered.bnx", "files/images/B1_CH2_C001.png", 20, 250, 1)

    # validityChecker.getImageToFileGraphs("files/bnx/4QVZ_ScanRange_1-1_filtered.filtered.bnx", "files/images/B1_CH2_C001.png")
    # validityChecker.getImageToFileStatistics("files/bnx/4QVZ_ScanRange_1-1_filtered.filtered.bnx", "files/images/B1_CH2_C001.png")

    fileReader = BNXFileReader("files/bnx/4QVZ_ScanRange_1-1_filtered.filtered.bnx")
    fileReader.open()

    imageAnalyzer = FluorescentMarkImageAnalyzer("files/images/B1_CH2_C001.png")
    imageAnalyzer.open()
