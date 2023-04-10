from src.Filesystem.ImageFilesystem import ImageFilesystem
from src.ImageAnalysis.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
import numpy as np


class MeanFilteredImageAnalyzer(FluorescentMarkImageAnalyzer):
    def __init__(self, filename):
        super().__init__(filename)

    '''ImageFilter does not support 16bit images :(
    def open(self):
        self.image = Image.open(self.filename)
        self.image = self.image.filter(ImageFilter.BoxBlur(1))
    '''

    def getPixelValue(self, x: int, y: int) -> int:
        surroundings = self.image.crop((x-1, y-1, x+1+1, y+1+1))
        return np.mean(np.ma.masked_where(surroundings == 0, surroundings)) #remove 0 filled from the edge values

if __name__=='__main__':
    ia = MeanFilteredImageAnalyzer(ImageFilesystem.getFirstImage())