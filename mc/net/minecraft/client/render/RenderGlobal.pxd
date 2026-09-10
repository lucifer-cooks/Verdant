# cython: language_level=3

cimport cython

from mc.net.minecraft.game.level.World cimport World
from mc.net.minecraft.client.render.RenderBlocks cimport RenderBlocks
from mc.net.minecraft.client.render.Tessellator cimport Tessellator
from mc.JavaUtils cimport IntBuffer

@cython.final
cdef class RenderGlobal:

    cdef:
        object __mc
        object __renderEngine
        World __worldObj
        IntBuffer __renderIntBuffer
        Tessellator __t

        object __worldRenderersToUpdate
        list __sortedWorldRenderers
        list __worldRenderers
        list __visibleRenderers

        object __globalRenderBlocks

        IntBuffer __glOcclusionQueryBase
        bint __occlusionEnabled

        int __cloudOffsetX

        int __skyQuadList
        int __cloudQuadList
        float __skyCacheR
        float __skyCacheG
        float __skyCacheB
        int __skyWidth
        int __skyHeight
        int __cloudGeomList
        int __cloudGeomWidth
        int __cloudGeomHeight
        float __prevFrustumPitch
        float __prevFrustumYaw
        float __prevFrustumX
        float __prevFrustumZ

        int __glSkyList

        int __countEntitiesTotal
        int __countEntitiesRendered
        int __countEntitiesHidden

        int[50000] __chunkBuffer

        IntBuffer __occlusionResult

        int __renderersLoaded
        int __renderersBeingClipped
        int __renderersBeingOccluded
        int __renderersBeingRendered

        float __prevSortX
        float __prevSortY
        float __prevSortZ

        public float damagePartialTime

        int __glGenList
        int __glRenderListBase

        int __renderChunksWide
        int __renderChunksTall
        int __renderChunksDeep

    cdef __checkOcclusionQueryResult(self, int minChunk, int maxChunk)
    cdef int __renderSortedRenderers(self, int minChunk, int maxChunk, int layer)
    cdef __oobGroundRenderHeight(self)
    cdef __oobWaterRenderHeight(self)
    cdef __markBlocksForUpdate(self, int x0, int y0, int z0, int x1, int y1, int z1)
    cdef markBlockAndNeighborsNeedsUpdate(self, int x, int y, int z)
    cdef markBlockRangeNeedsUpdate(self, int x0, int y0, int z0,
                                   int x1, int y1, int z1)
    cdef updateAllRenderers(self)
