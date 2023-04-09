from src import constants
class PositionHelper:

    @staticmethod
    def getFOVfromY(y) -> (int,int):
        FOV = (y // constants.FOV_SIZE) + 1
        return FOV, y%constants.FOV_SIZE

    @staticmethod
    def getYfromFOVandY(FOV, FOVy) -> int:
        return (FOV-1)*constants.FOV_SIZE + FOVy