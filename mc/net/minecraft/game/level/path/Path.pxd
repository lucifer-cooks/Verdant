# cython: language_level=3

cimport cython

from mc.net.minecraft.game.level.path.PathPoint cimport PathPoint

@cython.final
cdef class Path:

    cdef:
        list __pathPoints
        int __count

    cdef PathPoint addPoint(self, PathPoint point)
    cdef clearPath(self)
    cdef PathPoint dequeue(self)
    cdef changeDistance(self, PathPoint point, float distance)
    cdef __sortBack(self, int index)
    cdef __sortForward(self, int index)
    cdef inline bint isPathEmpty(self)
