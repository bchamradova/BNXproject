class ImageDoesNotExist(Exception):

    def __init__(self, filename):
        super().__init__('Required image does not exist in expected path: ' + filename)
