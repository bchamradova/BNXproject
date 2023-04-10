import math
import os
import re

COLUMN_RUN_IDENTIFIER = 70


class ImageFilesystem:

    directory = os.path.dirname(__file__) + '/../../files/images/converted/'

    @staticmethod
    def yieldAllImages():
        return (os.path.join(path, name) for path, subdirs, files in os.walk(ImageFilesystem.directory) for name in files)

    @staticmethod
    def yieldAllImagesInScan(scan):
        return (ImageFilesystem.directory + str(scan) + '/' + image for image in os.listdir(ImageFilesystem.directory + str(scan) + '/'))
    @staticmethod
    def getFirstImage():
        return ImageFilesystem.getImageByScanAndRunAndColumn(1,1,1)

    @staticmethod
    def getImageByScanAndRunAndColumn(scan, runId, column, channel = 2):
        #total 4 banks, each has 2 runIds -> see readme
        bank = math.ceil((runId % 8) / 2) if runId % 8 != 0 else 4
        #each scan has 8 runs -> scan = run/8 -> check input
        if (math.ceil(runId / 8) != scan):
            raise Exception('scan doesnt match runId o.o')
        return ImageFilesystem.directory + str(scan) + '/' +'channel' + str(channel) + '/B' + str(bank) + '_CH' + str(channel) + '_C' + str(f'{column:03}') +  '.tiff'

    @staticmethod
    def getScanAndRunAndColumnFromPath(path):
        directory, filename = os.path.split(path)
        scan = int(directory[directory.find(ImageFilesystem.directory)+len(ImageFilesystem.directory):directory.rfind('/channel')])
        fileNumbers = re.findall(r'\d+', filename)
        bank = int(fileNumbers[0])
        channel = int(fileNumbers[1])
        column = int(fileNumbers[2])
        run = (scan-1)*8 + bank * 2 - 1 if column < COLUMN_RUN_IDENTIFIER else (scan-1)*8 + bank * 2
        return scan,run, column
