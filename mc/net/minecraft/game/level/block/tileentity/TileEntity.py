class TileEntity:

    def __init__(self):
        self.worldObj = None
        self.xCoord = 0
        self.yCoord = 0
        self.zCoord = 0

    def readFromNBT(self, compound):
        pass

    def writeToNBT(self, compound):
        pass

    def updateEntity(self):
        pass
