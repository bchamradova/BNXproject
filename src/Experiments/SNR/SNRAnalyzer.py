import sys

from src.BNXFile.BNXFileReader import BNXFileReader
from src.Exception.EndOfBNXFileException import EndOfBNXFileException
from src.ImageAnalysis.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
from src.ImageAnalysis.NoiseAnalyzer import NoiseAnalyzer


class SNRAnalyzer:

    def getBNXSNRStats(self, BNXfilename: str):
        fileReader = BNXFileReader(BNXfilename)
        fileReader.open()
        maxSNR = 0
        minSNR = sys.maxsize
        sum = 0
        count = 0
        while True:
            try:
                molecule = fileReader.getNextMolecule()
                for mark in molecule.fluorescentMarks:
                    if mark.SNR > maxSNR:
                        maxSNR = mark.SNR
                    if mark.SNR < minSNR:
                        minSNR = mark.SNR
                    sum += mark.SNR
                    count += 1
            except EndOfBNXFileException:
                break

        print('max, min, avg')
        print(maxSNR, minSNR, sum / count)

    def getImageSNRStatsForMolecules(self, BNXfilename: str, imageFilename: str):
        fileReader = BNXFileReader(BNXfilename)
        ia = FluorescentMarkImageAnalyzer(imageFilename)
        deviation = NoiseAnalyzer(imageFilename).getDeviation()
        fileReader.open()
        maxSNR = 0
        minSNR = sys.maxsize
        sum = 0
        count = 0
        while True:
            try:
                molecule = fileReader.getNextMolecule()
                for mark in molecule.fluorescentMarks:
                    value = ia.getPixelValue(mark.posX, mark.posY)
                    if value / deviation > maxSNR:
                        maxSNR = value / deviation
                    if value / deviation < minSNR:
                        minSNR = value / deviation
                    sum += value / deviation
                    count += 1
            except EndOfBNXFileException:
                break

        print('max, min, avg')
        print(maxSNR, minSNR, sum / count)

    def getImageSNRStats(self, imageFilename):
        ia = FluorescentMarkImageAnalyzer(imageFilename)
        SNRs = []
        maxSNR = 0
        sum = count = 0
        minSNR = sys.maxsize
        na = NoiseAnalyzer(imageFilename)
        deviation = na.getDeviation()
        for x in range(NoiseAnalyzer.IMAGE_WIDTH):
            for y in range(NoiseAnalyzer.IMAGE_HEIGHT):
                SNR = ia.getPixelValue(x, y) / deviation
                SNRs.append(SNR)
                if SNR > maxSNR:
                    maxSNR = SNR
                if SNR < minSNR:
                    minSNR = SNR
        print(maxSNR)
        print(minSNR)
        return SNRs
