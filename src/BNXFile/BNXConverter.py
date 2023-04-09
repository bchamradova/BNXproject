from src.Filesystem.ImageFilesystem import ImageFilesystem
from src.ImageAnalysis.FluorescentMarkImageAnalyzer import FluorescentMarkImageAnalyzer
from src.ImageAnalysis.MoleculeDetector import MoleculeDetector


class BNXConverter:
    def __init__(self, outputFile, lowerBound=0, surroundings=3,filter='gauss'):
        self.outputFile = outputFile
        self.lowerBound = lowerBound
        self.surroundings = surroundings
        self.filter = filter


    def convertImage(self, scan, run, column):
        molecules = MoleculeDetector.detectMolecules(scan, run, column)
        imageAnalyzer = FluorescentMarkImageAnalyzer(
            ImageFilesystem.getImageByScanAndRunAndColumn(scan, run, column, channel=2))

        for i,molecule in enumerate(molecules):
            print(i)

            distances, intensities, SNRs = imageAnalyzer.detectMarksOnMolecule(
                molecule,
                self.lowerBound,
                self.surroundings
            )
            molecule.addFluorescentMarksArrays(distances, intensities, SNRs)

        self.flush(molecules)

    def convertScan(self, scan):
        for run in range(1, 8 + 1):
            for column in range(1, 137 + 1):
                self.convertImage(scan, run, column)

    def flush(self, molecules):
        with open(self.outputFile, 'w') as file:
            for molecule in molecules:
                file.write(molecule.createBNXRecord())
