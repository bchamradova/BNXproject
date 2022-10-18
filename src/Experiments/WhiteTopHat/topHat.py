import skimage
from PIL import Image
import numpy as np
from scipy import ndimage

from src.Experiments.BNXvsImage.ValidityChecker import ValidityChecker


def applyTopHatToImage(filename):
    image = Image.open(filename)
    data = np.asarray(image)
    transformed = ndimage.white_tophat(data, structure=skimage.morphology.disk(6))
    transformedImage = Image.fromarray(transformed)
    transformedImage.save("C:\\Users\\blank\\Documents\\7. semestr\\semestrální projektk\\BNXproject\\files\\images\\th.png")


if __name__ == '__main__':
    transf = "C:\\Users\\blank\\Documents\\7. semestr\\semestrální projektk\\BNXproject\\files\\images\\th.png"
    actual = "C:\\Users\\blank\\Documents\\7. semestr\\semestrální projektk\\BNXproject\\files\\images\\B1_CH2_C002.png"
    bnx = "C:\\Users\\blank\\Documents\\7. semestr\\semestrální projektk\\BNXproject\\files\\bnx\\4QVZ_ScanRange_1-1_filtered.filtered.bnx"
    #applyTopHatToImage("C:\\Users\\blank\\Documents\\7. semestr\\semestrální projektk\\BNXproject\\files\\images\\B1_CH2_C001.png")
    validityChecker = ValidityChecker()
    validityChecker.getImageToFileStatistics("C:\\Users\\blank\\Documents\\7. semestr\\semestrální projektk\\BNXproject\\files\\bnx\\4QVZ_ScanRange_1-1_filtered.filtered.bnx",
                                             actual)

    validityChecker.getImageToFileStatistics("C:\\Users\\blank\\Documents\\7. semestr\\semestrální projektk\\BNXproject\\files\\bnx\\4QVZ_ScanRange_1-1_filtered.filtered.bnx",
                                             transf)

    validityChecker.getFileToImageStatistics(bnx, actual, minValue=250)
    validityChecker.getFileToImageStatistics(bnx, transf, minValue=250)
