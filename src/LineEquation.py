import math


class LineEquation:
    def __init__(self, point1: (int, int), point2: (int, int)):
        self.point1 = point1
        self.point2 = point2
        self.scope = self.calculateSlope()
        self.intercept = self.calculateIntercept()

    def calculateSlope(self) -> float:
        if not ((self.point1[0] - self.point2[0]) == 0):
            return (self.point1[1] - self.point2[1]) / (self.point1[0] - self.point2[0])
        else:
            return 0

    def calculateIntercept(self) -> float:
        x = self.point1[0]
        y = self.point1[1]
        return y - self.scope * x

    def getXCoordinateFromY(self, y: int) -> int:
        if (self.scope == 0):
            raise Exception("cannot get x coordinate from horizontal line" + str(self.point1) + str(self.point2))
        return int((y - self.intercept) / self.scope)

    def getCoordinatesInDistanceFromFirstPoint(self, distance: int) -> (int, int):
        D = math.sqrt((self.point2[0] - self.point1[0]) ** 2 + (self.point1[1] - self.point2[1]) ** 2)
        x = self.point1[0] + (distance / D) * (self.point2[0] - self.point1[0])
        y = self.point1[1] + (distance / D) * (self.point2[1] - self.point1[1])
        return (int(round(x)), int(round(y)))

    def __str__(self) -> str:
        return "y = " + str(self.scope) + "x + " + str(self.intercept)
