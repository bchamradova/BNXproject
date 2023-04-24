import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm


class GraphVisualizer:

    def showComparedImageAndBnxValues(self, imageData, bnxData, localMaxima):
        plt.figure(figsize=(12, 8))
        plt.plot(imageData, linestyle='solid', zorder=1)
        # plt.ylim([0,1000])
        # plt.yticks([0,200,400,600,800,1000])
        localMaxima = plt.scatter([i for i in range(len(localMaxima))], localMaxima, marker='o', color='orange',
                                  alpha=0.5, zorder=2)
        bnxMarks = plt.scatter([i for i in range(len(bnxData))], bnxData, marker='x', color='purple', alpha=0.8,
                               zorder=3)
        plt.legend((localMaxima, bnxMarks), ('lokální maxima', 'značky v souboru BNX'), loc=2, fontsize=18)
        plt.xlabel("Pozice na molekule", fontsize=18)
        plt.ylabel("Hodnota intenzity", fontsize=18)
        plt.show()

    def showComparedInterpolatedValues(self, curveValues, interpolatedValues):
        plt.plot(curveValues, linestyle='solid')
        plt.plot(interpolatedValues, linestyle='solid')
        plt.legend(('before', 'after'))
        plt.show()

    def showFileToImageStatisticsComparedByRanges(self, graphDataIndexedBySurroundings):
        for surroundingsRange, plotData in graphDataIndexedBySurroundings.items():
            plt.plot(plotData.lowerBounds, plotData.resultRatios)

        plt.xlabel('Nejnižší přijatelná hodnota')
        plt.ylabel('Poměr validních fluorescenčních značek')
        # plt.legend([key for key, item in graphDataIndexedBySurroundings.items()])
        plt.legend(['3x3', '5x5', '7x7'])
        plt.show()

    def showFileToImageStatisticsComparedByLowerBounds(self, graphDataIndexedByUpperBounds):
        for upperBound, plotData in graphDataIndexedByUpperBounds.items():
            plt.plot(plotData.surroundingsRanges, plotData.resultRatios)

        plt.xlabel('size of checked surroundings')
        plt.ylabel('share of valid marks')
        plt.legend([key for key, item in graphDataIndexedByUpperBounds.items()])
        plt.show()

    def filteredValuesComparedGraph(self):
        bounds = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550]
        diffAvg = [53.1, 53.1, 53.1, 53.1, 29.05, 6.47, 2.1, 1.41, 1.19, 1, 0.82, 0.72]
        plt.plot(bounds, diffAvg)
        plt.xlabel('Nejnižší přijatelná hodnota')
        plt.ylabel('Průměrný rozdíl v počtu \n fluorescenčních značek molekuly')
        plt.show()

    def gaussianDistribution(self, data, title='pixel distribution'):
        plt.plot(data)
        plt.xlabel('pixel value')
        plt.ylabel('probability')
        plt.title(title)
        plt.show()

    def compareHistogramToNormalDistribution(self, data):
        plt.hist(data, density=True, bins=50)
        mu, std = norm.fit(data)
        print('mean: ' + str(mu))
        print('deviation: ' + str(std))
        xmin, xmax = plt.xlim()
        x = np.linspace(xmin, xmax, 100)
        p = norm.pdf(x, mu, std)
        plt.xlabel('pixel value')
        plt.ylabel('probability')
        plt.plot(x, p)
        plt.show()

    def showMeansValues(self, rowData, column=0):
        plt.plot(rowData)
        if column != 1:
            plt.xlabel('row id')
            plt.ylabel('mean value')
        else:
            plt.xlabel('column id')
            plt.ylabel('mean value')
        plt.show()

    @staticmethod
    def showLinePlot(x, y, xtitle, ytitle, label=''):
        plt.plot(x, y)
        plt.xlabel(xtitle)
        plt.ylabel(ytitle)
        plt.ylabel(ytitle)
        plt.title(label)
        plt.show()

    @staticmethod
    def plotSymmetricRatios(sideRatios, midRatios, axis):
        counts, bins = np.histogram(sideRatios)
        plt.hist(bins[:-1], bins, weights=counts)
        plt.xlabel(axis + ' sides ratio')
        plt.ylabel('count')
        plt.show()
        counts, bins = np.histogram(midRatios)
        plt.hist(bins[:-1], bins, weights=counts)
        plt.xlabel(axis +' mid to side ratio')
        plt.ylabel('count')
        plt.show()

