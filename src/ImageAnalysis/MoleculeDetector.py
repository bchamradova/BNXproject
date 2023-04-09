import scipy.ndimage as ndimage
import numpy as np
from src import constants
from PIL import Image
import skimage.measure

from src.Filesystem.ImageFilesystem import ImageFilesystem
from src.Helpers.PositionHelper import PositionHelper
from src.Model.Molecule import Molecule


class MoleculeDetector:
    @staticmethod
    def detectMoleculeCoordinates(filename):
        coordinates = []
        image = ndimage.median_filter(np.array(Image.open(filename)), size=1)
        binaryImage = np.where(image > constants.MOLECULE_DETECTION_THRESHOLD, 1, 0)
        labels = skimage.measure.label(binaryImage, connectivity=2)
        slices = ndimage.find_objects(labels)
        for slice in slices:
            height, width = slice[0].stop - slice[0].start, slice[1].stop - slice[1].start
            if height >= constants.MOLECULE_MIN_HEIGHT:
                col_start, col_stop = slice[0].start, slice[0].stop
                row_start, row_stop = slice[1].start, slice[1].stop
                top_left = (row_start, col_start)
                bottom_right = (row_stop - 1, col_stop - 1)
                coordinates.append((top_left, bottom_right))
        return coordinates

    @staticmethod
    def detectMolecules(scan, run, column):
        moleculeFilename = ImageFilesystem.getImageByScanAndRunAndColumn(scan, run, column, channel=1)
        molCoordinates = MoleculeDetector.detectMoleculeCoordinates(moleculeFilename)
        molecules = []
        for i,coordinates in enumerate(molCoordinates):
            startX, totalStartY, endX, totalEndY = coordinates[0][0], coordinates[0][1], coordinates[1][0], coordinates[1][1]
            startFOV, startY = PositionHelper.getFOVfromY(totalStartY)
            endFOV, endY = PositionHelper.getFOVfromY(totalEndY)
            molecule = Molecule((endY-startY)*constants.PIXEL_TO_NUCLEOTIDE_RATIO, startFOV, startX, startY, endFOV, endX, endY, run, column)
            molecule.id = i
            molecule.avgIntensity = round(np.mean(np.asarray(Image.open(moleculeFilename).crop((startX, startY, endX, endY)))), 1)
            molecule.SNR = round(molecule.avgIntensity / constants.NOISE_DEVIATION, 1)
            molecule.originalMoleculeId = 0
            molecule.scanNumber = scan
            molecule.scanDirection = constants.SCAN_DIRECTION
            molecule.chipId = constants.CHIP_ID
            molecule.flowcell = constants.FLOWCELL
            molecules.append(molecule)
        return molecules


