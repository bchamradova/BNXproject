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
        if self.filter == '':
            imageAnalyzer = FluorescentMarkImageAnalyzer(imageFilename)
        elif self.filter == 'mean':
            imageAnalyzer = MeanFilteredImageAnalyzer(imageFilename)
        elif self.filter == 'median':
            imageAnalyzer = MedianFilteredImageAnalyzer(imageFilename)
        elif self.filter == 'gauss':
            imageAnalyzer = GaussianFilteredImageAnalyzer(imageFilename)
        else:
            raise UndefinedFilterException

        for i, molecule in enumerate(molecules):
            print(i)
            distances, intensities, SNRs = imageAnalyzer.detectMarksOnMolecule(
                molecule,
                self.lowerBound,
                self.surroundings
            )
            molecule.addFluorescentMarksArrays(distances, intensities, SNRs)

        self.flush(molecules)

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
    scan = 1
    run = 7
    column = 1
    converter = BNXConverter('filtered_bnx_output.bnx')
    converter.convertImage(scan, run, column)