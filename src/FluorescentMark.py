class FluorescentMark:

    def __init__(self, posX: int, posY: int, distance: int):
        self.posX = posX
        self.posY = posY
        self.distance = distance

    def getCoordinates(self) -> (int, int):
        return (self.posX, self.posY)

    def __str__(self) -> str:
        return "posX: " + str(self.posX) + " posY: " + str(self.posY) + " distance: " + str(self.distance)
