import argparse
import os

import progressbar

from src import constants
from src.Exception.ImageDoesNotExist import ImageDoesNotExist
from src.Exception.UndefinedFilterException import UndefinedFilterException
from src.Filesystem.ImageFilesystem import ImageFilesystem
from src.ImageAnalysis.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
from src.ImageAnalysis.GaussianFilteredImageAnalyzer import GaussianFilteredImageAnalyzer
from src.ImageAnalysis.MeanFilteredImageAnalyzer import MeanFilteredImageAnalyzer
from src.ImageAnalysis.MedianFilteredImageAnalyzer import MedianFilteredImageAnalyzer
from src.ImageAnalysis.MoleculeDetector import MoleculeDetector


class BNXConverter:
    NUMBER_OF_MOLECULES_LINE = '# Number of molecules: '

    def __init__(self, outputFile, lowerBound=0, surroundings=3, useLine=True, filter='gauss'):
        self.outputFile = os.path.dirname(__file__) + '/../../files/bnx/output/' + outputFile
        self.lowerBound = lowerBound
        self.surroundings = surroundings
        self.useLine = useLine
        self.filter = filter
        self.header = False

    def convertImage(self, scan, run, column):
        molecules = MoleculeDetector.detectMolecules(scan, run, column)
        imageFilename = ImageFilesystem.getImageByScanAndRunAndColumn(scan, run, column, channel=2)
        if self.filter == 'none':
            imageAnalyzer = FluorescentMarkImageAnalyzer(imageFilename)
        elif self.filter == 'mean':
            imageAnalyzer = MeanFilteredImageAnalyzer(imageFilename)
        elif self.filter == 'median':
            imageAnalyzer = MedianFilteredImageAnalyzer(imageFilename)
        elif self.filter == 'gauss':
            imageAnalyzer = GaussianFilteredImageAnalyzer(imageFilename)
        else:
            raise UndefinedFilterException

        bar = progressbar.ProgressBar(maxval=len(molecules),
                                      widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        for i, molecule in enumerate(molecules):
            bar.update(i)
            distances, intensities, SNRs = imageAnalyzer.detectMarksOnMolecule(
                molecule,
                self.lowerBound,
                self.surroundings,
                self.useLine
            )
            molecule.addFluorescentMarksArrays(distances, intensities, SNRs)

        self.flush(molecules)
        bar.finish()
        return len(molecules)

    def convertScan(self, scan):
        for filename in ImageFilesystem.yieldAllImagesInScan(scan):
            scan, run, column = ImageFilesystem.getScanAndRunAndColumnFromPath(filename)
            try:
                ImageFilesystem.getImageByScanAndRunAndColumn(scan, run, column, channel=1)
                ImageFilesystem.getImageByScanAndRunAndColumn(scan, run, column, channel=2)
                self.convertImage(scan, run, column)
            except ImageDoesNotExist:
                print(f'image {filename} missing for some channel for scan {scan}')

    def flush(self, molecules):
        with open(self.outputFile, 'a+') as file:
            if not self.header:
                file.write(BNXConverter.NUMBER_OF_MOLECULES_LINE + str(len(molecules)))
                with open(os.path.dirname(__file__) + '/bnx_header', 'r') as header:
                    for line in header:
                        file.write(line)
                self.header = True
            for molecule in molecules:
                file.write(molecule.createBNXRecord())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='convert images with molecules(channel1) and fluorescent marks(channel2) to BNX file')
    parser.add_argument("-i", "--input", help="input image with path including scan (scan/channel/filename.tiff)", type=str, required=True)
    parser.add_argument("-o", "--output", help="output filename", type=str, required=True)
    parser.add_argument("-l", "--line", help="type of mark detection - 1 for line, 0 for maxima", type=int, default=0)
    parser.add_argument("-t", "--threshold", help="minimal value of mark intensity to take into account", type=int,
                        default=0)
    parser.add_argument("-sr", "--surroundings", help="size of surroundings to look for maxima", type=int, default=3)
    parser.add_argument("-f", "--filter", help="convolution filter used", type=str, default='gauss',
                        choices=['none', 'mean', 'median', 'gauss'])
    args = parser.parse_args()

    converter = BNXConverter(args.output, args.threshold, args.surroundings, args.line, args.filter)
    scan, run, column = ImageFilesystem.getScanAndRunAndColumnFromPath(ImageFilesystem.directory + args.input)
    converter.convertImage(scan, run, column)
