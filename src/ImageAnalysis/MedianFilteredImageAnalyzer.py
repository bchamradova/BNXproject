from src.Filesystem.ImageFilesystem import ImageFilesystem
from src.ImageAnalysis.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
import numpy as np


class MedianFilteredImageAnalyzer(FluorescentMarkImageAnalyzer):
    def __init__(self, filename):
        super().__init__(filename)

    def getPixelValue(self, x: int, y: int) -> int:
        surroundings = self.image.crop((x-1, y-1, x+1+1, y+1+1))
        return np.median(np.ma.masked_where(surroundings == 0, surroundings)) #remove 0 filled from the edge values

if __name__=='__main__':
    ia = MedianFilteredImageAnalyzer(ImageFilesystem.getFirstImage())