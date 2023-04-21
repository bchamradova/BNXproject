import argparse
import progressbar

from src import constants
from src.Exception.UndefinedFilterException import UndefinedFilterException
from src.Filesystem.ImageFilesystem import ImageFilesystem
from src.ImageAnalysis.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
from src.ImageAnalysis.GaussianFilteredImageAnalyzer import GaussianFilteredImageAnalyzer
from src.ImageAnalysis.MeanFilteredImageAnalyzer import MeanFilteredImageAnalyzer
from src.ImageAnalysis.MedianFilteredImageAnalyzer import MedianFilteredImageAnalyzer
from src.ImageAnalysis.MoleculeDetector import MoleculeDetector


class BNXConverter:
    def __init__(self, outputFile, lowerBound=0, surroundings=3, filter='gauss'):
        self.outputFile = outputFile
        self.lowerBound = lowerBound
        self.surroundings = surroundings
        self.filter = filter

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

        bar = progressbar.ProgressBar(maxval=len(molecules), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        for i, molecule in enumerate(molecules):
            bar.update(i)
            distances, intensities, SNRs = imageAnalyzer.detectMarksOnMolecule(
                molecule,
                self.lowerBound,
                self.surroundings
            )
            molecule.addFluorescentMarksArrays(distances, intensities, SNRs)

        self.flush(molecules)
        bar.finish()

    def convertScan(self, scan):
        for run in range(1, constants.RUN_COUNT + 1):
            for column in range(1, constants.COLUMN_COUNT + 1):
                self.convertImage(scan, run, column)

    def flush(self, molecules):
        with open(self.outputFile, 'w') as file:
            file.write('# Number of molecules: ' + str(len(molecules)))
            with open('bnx_header', 'r') as header:
                for line in header:
                    file.write(line)
            for molecule in molecules:
                file.write(molecule.createBNXRecord())

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='convert images with molecules(channel1) and fluorescent marks(channel2) to BNX file')
    parser.add_argument("-i", "--input", help="input image",type=str,required=True)
    parser.add_argument("-o", "--output", help="output filename name", type=str, required=True)
    parser.add_argument("-l", "--line", help="type of mark detection - 1 for line, 0 for maxima", type=int, default=1)
    parser.add_argument("-t", "--threshold", help="minimal value of intensity to take into account", type=int,
                        default=0)
    parser.add_argument("-sr", "--surroundings", help="size of surroundings", type=int, default=3)
    parser.add_argument("-f", "--filter", help="convolution filter used", type=str, default='gauss',
                        choices=['none', 'mean', 'median', 'gauss'])
    args = parser.parse_args()

    converter = BNXConverter(args.output, args.threshold, args.surroundings, args.filter)
    scan, run, column = ImageFilesystem.getScanAndRunAndColumnFromPath(ImageFilesystem.directory + args.input)
    converter.convertImage(scan, run, column)
