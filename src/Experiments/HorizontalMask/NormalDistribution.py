import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import norm, multivariate_normal as mvn

class NormalDistribution:
    @staticmethod
    def getSigmaFromK(k, defaultDeviation = 1):
        return defaultDeviation / k

    @staticmethod
    def getCumulativeValueForRange(range, deviation, mean):
        if range[0] == range[1]:
            return norm.pdf(range[0], mean, deviation)
        return abs(norm.cdf(range[0], mean, deviation) - norm.cdf(range[1], mean, deviation))

    @staticmethod
    def cdf2d(x, y, sigmaX, sigmaY, mean):
        return norm.cdf(x, mean[0], sigmaX) * norm.cdf(y, mean[1], sigmaY)

    @staticmethod
    def getCumulativeValueForRange2d(rangeX, rangeY, deviationX, deviationY, mean):
        return abs(
            NormalDistribution.getCumulativeValueForRange(rangeX, deviationX, mean[0]) * NormalDistribution.getCumulativeValueForRange(rangeY, deviationY,
                                                                                                 mean[1]))
        # return abs(cdf2d(rangeX[0], rangeY[0], deviationX, deviationY, mean) - cdf2d(rangeX[1], rangeY[1], deviationX,
        #                                                                             deviationY, mean))

    @staticmethod
    def bivariatePdf(x, y, sigmaX, sigmaY):
        return (1 / (2 * np.pi * sigmaX * sigmaY) * np.exp(-(x ** 2 / (2 * sigmaX ** 2)
                                                             + y ** 2 / (2 * sigmaY ** 2))))

    @staticmethod
    def plotNormalDistributionWithStaticPoints(k, mean):
        xmin, xmax = -5, 5
        x = np.arange(xmin, xmax, 0.01)
        # normalize one pixel = 1 on axis -> middle point from 0.5 to -0.5
        normalizedSigma = NormalDistribution.getSigmaFromK(k)
        normalized = norm.pdf(x, mean, normalizedSigma)
        org = norm.pdf(x, mean, normalizedSigma)
        # midCdf = (norm.cdf(0.5, mean, normalizedSigma) - norm.cdf(-0.5, mean, normalizedSigma))
        midCdf = NormalDistribution.getCumulativeValueForRange((0.5, -0.5), normalizedSigma, mean)
        # sideCdf = (norm.cdf(1.5, mean, normalizedSigma) - norm.cdf(0.5, mean, normalizedSigma))
        sideCdf = NormalDistribution.getCumulativeValueForRange((1.5, 0.5), normalizedSigma, mean)
        normalDistributionRatio = midCdf / sideCdf  # should be the same as pixel ratio
        fig, ax = plt.subplots()
        fig.set_dpi(500)
        plt.plot(x, normalized, color='green')
        plt.plot(x, org, color='lightgrey')
        points = [-1.5, -0.5, 0.5, 1.5]
        plt.scatter(points, norm.pdf(points, mean, normalizedSigma), color='green')
        for point in points:
            plt.axvline(x=point, linestyle=':', color='gray')
        ax.set_ylim(ymin=0)
        plt.ylabel('P(X)')
        plt.xlabel('posun [bp]')
        ax.set_xlim(xmin=xmin, xmax=xmax)
        ax.set_xticks(np.arange((xmin + 0.5) * 1, xmax * 1, 1))
        plt.xticks(rotation=45, horizontalalignment='right')
        ax.set_xticklabels(np.arange((xmin + 0.5) * 375, xmax * 375, 375))
        plt.show()

    @staticmethod
    def plotNormalDistributionWithPointsByK(k, mean, sigma):
        xmin, xmax = -4, 4
        x = np.arange(xmin, xmax, 0.01)
        p = norm.pdf(x, mean, sigma)
        c = norm.cdf(x, mean, sigma)
        step = k / 2
        plt.scatter([-step, step], [norm.pdf(-step, mean, sigma), norm.pdf(step, mean, sigma)])
        plt.scatter([-step - k, step + k], [norm.pdf(step + k, mean, sigma), norm.pdf(-step - k, mean, sigma)])
        plt.plot(x, p)
        plt.plot(x, c)
        plt.show()

    @staticmethod
    def plot2DDistribution(sigmaX, sigmaY, mean):
        size = 100
        x = np.linspace(-5, 5, size, dtype=float)
        y = np.linspace(-5, 5, size, dtype=float)

        x, y = np.meshgrid(x, y)
        z = (1 / (2 * np.pi * sigmaX * sigmaY) * np.exp(-(x ** 2 / (2 * sigmaX ** 2)
                                                          + y ** 2 / (2 * sigmaY ** 2))))
        zcdf = NormalDistribution.cdf2d(x, y, sigmaX, sigmaY, mean)
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.scatter(x, y, z, c=z)
        plt.show()
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.scatter(x, y, zcdf, c=zcdf)
        plt.show()
        plt.contourf(x, y, z, cmap='viridis')
        plt.colorbar()
        plt.show()

    @staticmethod
    def getK(dataMidRatio, mean, sigma):
        # diferencialni evoluce TODO
        k = 0.01
        kValues = []
        ratios = []
        normalDistributionRatio = 0
        dataRatio = dataMidRatio
        while round(normalDistributionRatio, 3) != round(dataRatio, 3):
            k = k + 0.001
            step = k / 2
            # midCdf = (norm.cdf(mean + step, mean, sigma) - norm.cdf(mean - step, mean, sigma))
            midCdf = NormalDistribution.getCumulativeValueForRange((mean + step, mean - step), sigma, mean)
            # sideCdf = (norm.cdf(mean + step + k, mean, sigma) - norm.cdf(mean + step, mean, sigma))
            sideCdf =NormalDistribution.getCumulativeValueForRange((mean + step + k, mean + step), sigma, mean)
            normalDistributionRatio = midCdf / sideCdf
            kValues.append(k)
            ratios.append(normalDistributionRatio / dataRatio)
        # GraphVisualizer.showLinePlot(kValues, ratios, 'k', 'ratio', 'ratios between distribution ratio and data ratio')
        # print(normalDistributionRatio, dataRatio)
        print('k', k)
        return k
