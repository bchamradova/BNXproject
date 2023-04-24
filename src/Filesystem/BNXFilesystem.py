import os
import re

from src.Exception.BNXDoesNotExist import BNXDoesNotExist


class BNXFilesystem:

    directory = os.path.dirname(__file__) + '/../../files/bnx/'

    @staticmethod
    def yieldAllBNX():
        return (BNXFilesystem.directory + file for file in os.listdir(BNXFilesystem.directory))

    @staticmethod
    def getFirstBNX():
        return BNXFilesystem.getBNXByScan(1)

    @staticmethod
    def getExampleBNX():
        #has only column 1 and runs 1-7
        return BNXFilesystem.directory + '4QVZ_ScanRange_1-1_filtered.filtered.bnx'

    @staticmethod
    def getBNXByScan(scan):
        filename = BNXFilesystem.directory + 'scans/_Scan' + str(f'{scan:02}') + '.bnx'
        if os.path.exists(filename):
            return filename
        else:
            raise BNXDoesNotExist(filename)
    @staticmethod
    def getScanByBNX(path):
        directory, filename = os.path.split(path)
        scan = re.findall(r'\d+', filename)
        return int(scan[0])