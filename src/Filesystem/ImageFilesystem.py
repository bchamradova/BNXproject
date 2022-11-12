import os

class ImageFilesystem:

    directory = os.path.dirname(__file__) + '/../../files/images/converted/'

    @staticmethod
    def yieldAllImages():
        return (ImageFilesystem.directory + image for image in os.listdir(ImageFilesystem.directory))

    @staticmethod
    def getFirstImage():
        return ImageFilesystem.getImageByNumberAndChannel(2,1)

    @staticmethod
    def getImageByNumberAndChannel(channel, number):
        return ImageFilesystem.directory + 'B1_CH' + str(channel) + '_C' + str(f'{number:03}') +  '.tiff'