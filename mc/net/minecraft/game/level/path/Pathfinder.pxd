# cython: language_level=3

cimport cython

from mc.net.minecraft.game.level.path.Path cimport Path
from mc.net.minecraft.game.level.path.PathPoint cimport PathPoint
from mc.net.minecraft.game.level.World cimport World
from mc.net.minecraft.game.entity.Entity cimport Entity

@cython.final
cdef class Pathfinder:

    cdef:
        World __worldMap
        Path __path
        dict __pointMap
        list __pathOptions

    cdef createEntityPathTo(self, Entity fromEntity, Entity toEntity, float distance)
    cdef createEntityPath(self, Entity entity, int x, int y, int z, float distance)
    cdef __addToPath(self, Entity entity, float x, float y, float z, float distance)
    cdef PathPoint __getSafePoint(self, Entity entity, int x, int y, int z,
                                  PathPoint sizePoint, int yOffset)
    cdef PathPoint __openPoint(self, int x, int y, int z)
    cdef int __getVerticalOffset(self, int x, int y, int z, PathPoint sizePoint)
    @staticmethod
    cdef __createEntityPath(PathPoint point)
