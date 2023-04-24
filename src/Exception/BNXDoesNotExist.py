class BNXDoesNotExist(Exception):

    def __init__(self, filename):
        super().__init__('Required bnx does not exist in expected path: ' + filename)
