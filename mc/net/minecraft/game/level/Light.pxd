# cython: language_level=3

cimport cython

from mc.net.minecraft.game.level.World cimport World

@cython.final
cdef class Light:

    cdef:
        int __lightingUpdateCounter
        list __lightingUpdateList
        World __worldObj
        int __worldWidth
        int __worldLength
        int __worldHeight
        list __skyLightList
        list __blockLightList
        list __lightingUpdateList1
        list __lightingUpdateList2
        int[:] __lightingUpdateList3
        char* __chunks
        object __metadataChunkBlock
        int __lightValue
        int __skylightSubtracted

    cdef int[:] __getLightingUpdates(self)
    cdef updateSkylight(self, int x0, int y0, int x1, int y1)
    cdef updateDaylightCycle(self, int lightSubtracted)
    cdef __updateLight(self, int limit)
    cdef updateBlockLight(self, int x0, int y0, int z0, int x1, int y1, int z1)
    cdef __updateLists(self, int x0, int y0, int z0, int x1, int y1, int z1)
    cdef updateLight(self)
