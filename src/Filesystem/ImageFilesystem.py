import os

class ImageFilesystem:

    directory = os.path.dirname(__file__) + '/../../files/images/converted/'

    @staticmethod
    def yieldAllImages():
        return (ImageFilesystem.directory + image for image in os.listdir(ImageFilesystem.directory))

    @staticmethod
    def getFirstImage():
        return ImageFilesystem.getImageByScanAndRunAndColumn(1,1,1)

    @staticmethod
    def getImageByScanAndRunAndColumn(scan, runId, column, channel = 2):
        #total 4 banks, each has 2 runIds -> see readme
        bank = (runId % 8) // 2
        return ImageFilesystem.directory + str(scan) + '/' + 'B' + str(bank) + '_CH' + str(channel) + '_C' + str(f'{column:03}') +  '.tiff'