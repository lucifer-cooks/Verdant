# cython: language_level=3

cimport cython

@cython.final
cdef class PathPoint:

    cdef:
        public int xCoord
        public int yCoord
        public int zCoord
        public int hash
        public int index
        public float totalPathDistance
        public float distanceToNext
        public float distanceToTarget
        public PathPoint previous
        public bint isFirst

    cdef float distanceTo(self, PathPoint point)
    cdef inline bint isAssigned(self)
