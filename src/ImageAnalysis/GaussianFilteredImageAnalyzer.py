from src.Filesystem.ImageFilesystem import ImageFilesystem
from src.ImageAnalysis.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
import numpy as np
from scipy.ndimage import gaussian_filter

class GaussianFilteredImageAnalyzer(FluorescentMarkImageAnalyzer):
    def __init__(self, filename):
        super().__init__(filename)

    def getPixelValue(self, x: int, y: int) -> int:
        surroundings = self.image.crop((x-1, y-1, x+1+1, y+1+1))
        filtered = gaussian_filter(surroundings, sigma=1, truncate=1)
        return filtered[1][1]

if __name__=='__main__':
    ia = GaussianFilteredImageAnalyzer(ImageFilesystem.getFirstImage())