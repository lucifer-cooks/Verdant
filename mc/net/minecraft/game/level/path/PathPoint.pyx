# cython: language_level=3

from libc.math cimport sqrt

cdef class PathPoint:

    def __init__(self, int x, int y, int z):
        self.xCoord = x
        self.yCoord = y
        self.zCoord = z
        self.hash = x | y << 10 | z << 20
        self.index = -1
        self.totalPathDistance = 0.0
        self.distanceToNext = 0.0
        self.distanceToTarget = 0.0
        self.previous = None
        self.isFirst = False

    cdef float distanceTo(self, PathPoint point):
        cdef float xd = point.xCoord - self.xCoord
        cdef float yd = point.yCoord - self.yCoord
        cdef float zd = point.zCoord - self.zCoord
        return sqrt(xd * xd + yd * yd + zd * zd)

    def __eq__(self, point):
        return point.hash == self.hash

    def __hash__(self):
        return self.hash

    cdef inline bint isAssigned(self):
        return self.index >= 0

    def toString(self):
        return f'{self.xCoord}, {self.yCoord}, {self.zCoord}'
