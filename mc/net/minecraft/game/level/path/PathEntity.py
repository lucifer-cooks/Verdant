from mc.net.minecraft.game.physics.Vec3D import Vec3D

class PathEntity:

    def __init__(self, points):
        self.__points = points
        self.__pathIndex = 0

    def incrementPathIndex(self):
        self.__pathIndex += 1

    def isFinished(self):
        return self.__pathIndex >= len(self.__points)

    def getPosition(self, entity):
        x = self.__points[self.__pathIndex].xCoord + (entity.width + 1.0) * 0.5
        y = self.__points[self.__pathIndex].yCoord
        z = self.__points[self.__pathIndex].zCoord + (entity.width + 1.0) * 0.5
        return Vec3D(x, y, z)
