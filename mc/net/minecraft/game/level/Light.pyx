# cython: language_level=3

cimport cython

import numpy as np
cimport numpy as np

from libc.stdlib cimport malloc, free

from mc.net.minecraft.client.render.RenderGlobal cimport RenderGlobal
from mc.net.minecraft.game.level.MetadataChunkBlock import MetadataChunkBlock
from mc.net.minecraft.game.level.World cimport World
from mc.net.minecraft.game.level.block.Block cimport Block
from mc.net.minecraft.game.level.block.Blocks import blocks

cdef class Light:

    def __cinit__(self):
        self.__lightingUpdateCounter = 0
        self.__lightingUpdateList = []
        self.__lightingUpdateList3 = np.zeros(65536, dtype=np.int32)
        self.__skyLightList = []
        self.__blockLightList = []
        self.__lightingUpdateList1 = []
        self.__lightingUpdateList2 = []
        self.__metadataChunkBlock = None
        self.__lightValue = 0
        self.__skylightSubtracted = 0

    def __dealloc__(self):
        free(self.__chunks)

    def __init__(self, World world):
        self.__worldObj = world
        self.__worldWidth = world.width
        self.__worldLength = world.length
        self.__worldHeight = world.height
        self.__chunks = <char*>malloc(sizeof(char) * (world.blocksSize // 8))
        for i in range(world.blocksSize // 8):
            self.__chunks[i] = 0

    cdef int[:] __getLightingUpdates(self):
        if len(self.__lightingUpdateList2) > 0:
            return self.__lightingUpdateList2.pop()
        else:
            return np.zeros(32768, dtype=np.int32)

    cdef updateSkylight(self, int x0, int y0, int x1, int y1):
        self.__lightingUpdateList1.append(MetadataChunkBlock(self, x0, y0, 0,
                                                             x1, y1, 1))

    cdef updateDaylightCycle(self, int lightSubtracted):
        lightSubtracted = max(min(lightSubtracted, 15), 0)
        self.__skylightSubtracted = lightSubtracted - self.__worldObj.skylightSubtracted
        if self.__skylightSubtracted != 0:
            self.__lightValue = self.__worldObj.skylightSubtracted
            self.__worldObj.skylightSubtracted = lightSubtracted
            while self.__metadataChunkBlock:
                self.__updateLight(64)

            self.__metadataChunkBlock = MetadataChunkBlock(
                self, 0, 0, 0, self.__worldObj.width, self.__worldObj.height,
                self.__worldObj.length
            )

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef __updateLight(self, int limit):
        cdef int x, z, y, i, light
        cdef RenderGlobal worldAccess

        for x in range(self.__metadataChunkBlock.x, self.__metadataChunkBlock.maxX):
            if limit <= 0 and x != self.__metadataChunkBlock.maxX - 1:
                self.__metadataChunkBlock.x = x
                return

            limit -= 1
            for z in range(self.__metadataChunkBlock.z, self.__metadataChunkBlock.maxZ):
                y = self.__worldObj.heightMap[x + z * self.__worldWidth] - 1
                while y > 0 and \
                      self.__worldObj.lightOpacity[self.__worldObj.blocks[(y * \
                          self.__worldLength + z) * self.__worldWidth + x]] < 100:
                    y -= 1

                y += 1
                for y in range(self.__worldHeight):
                    i = (y * self.__worldLength + z) * self.__worldWidth + x
                    if self.__worldObj.lightValue[self.__worldObj.blocks[i]] == 0:
                        light = self.__worldObj.data[i] & 15
                        if light <= self.__lightValue:
                            if self.__skylightSubtracted < 0 and light > 0:
                                self.__worldObj.data[i] -= 1
                            elif self.__skylightSubtracted > 0 and light < 15:
                                self.__worldObj.data[i] += 1

        for x in range(0, self.__worldWidth, 32):
            for z in range(0, self.__worldLength, 32):
                self.__blockLightList.append(MetadataChunkBlock(
                        self, x, 0, z, x + 32,
                        self.__worldHeight, z + 32
                    ))
                self.__skyLightList.append(MetadataChunkBlock(
                        self, x, 0, z, x + 32,
                        self.__worldHeight, z + 32
                    ))

        for worldAccess in self.__worldObj.worldAccesses:
            worldAccess.updateAllRenderers()

        self.__metadataChunkBlock = None

    cdef updateBlockLight(self, int x0, int y0, int z0, int x1, int y1, int z1):
        self.__blockLightList.append(MetadataChunkBlock(self, x0, y0, z0,
                                                        x1, y1, z1))

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef __updateLists(self, int x0, int y0, int z0, int x1, int y1, int z1):
        cdef int x, y, z, coord, count
        for y in range(y0, y1):
            for z in range(z0, z1):
                for x in range(x0, x1):
                    coord = x + y * self.__worldWidth + z * \
                            self.__worldWidth * self.__worldHeight
                    if (self.__chunks[coord >> 3] & 1 << (coord & 7)) != 0:
                        continue

                    self.__chunks[coord >> 3] = <char>(self.__chunks[coord >> 3] | 1 << (coord & 7))
                    self.__lightingUpdateList3[self.__lightingUpdateCounter] = coord
                    if (self.__chunks[coord >> 3] & 1 << (coord & 7)) == 0:
                        print('OMG ERROR!')

                    self.__lightingUpdateCounter += 1
                    if self.__lightingUpdateCounter > \
                       len(self.__lightingUpdateList3) - 32:
                        self.__lightingUpdateCounter -= 1
                        count = self.__lightingUpdateList3[self.__lightingUpdateCounter]
                        self.__lightingUpdateList3[len(self.__lightingUpdateList3) - 1] = self.__lightingUpdateCounter
                        self.__lightingUpdateList.append(self.__lightingUpdateList3)
                        self.__lightingUpdateList3 = self.__getLightingUpdates()
                        self.__lightingUpdateCounter = 1
                        self.__lightingUpdateList3[0] = count

    @cython.boundscheck(False)
    @cython.wraparound(False)
    cdef updateLight(self):
        cdef int chunkLimit, i, x, z, y, light, oldDepth, yl0, yl1, count, br, \
                 x0, y0, z0, x1, y1, z1, counter, depth, opacity, newDepth, coord
        cdef RenderGlobal worldAccess

        if self.__lightingUpdateList2:
            self.__lightingUpdateList2.pop()

        chunkLimit = 5
        while len(self.__skyLightList) > 0 and chunkLimit > 0:
            chunkLimit -= 1
            chunk = self.__skyLightList.pop(0)
            for worldAccess in self.__worldObj.worldAccesses:
                worldAccess.markBlockRangeNeedsUpdate(
                    chunk.x, chunk.y, chunk.z, chunk.maxX, chunk.maxY, chunk.maxZ
                )

        if self.__metadataChunkBlock:
            self.__updateLight(8)
            return

        for i in range(16):
            if self.__blockLightList:
                chunk = self.__blockLightList.pop(0)
                self.__updateLists(chunk.x, chunk.y, chunk.z,
                                   chunk.maxX, chunk.maxY, chunk.maxZ)

            if self.__lightingUpdateList1:
                chunk = self.__lightingUpdateList1.pop(0)
                for x in range(chunk.x, chunk.x + chunk.maxX):
                    for z in range(chunk.y, chunk.y + chunk.maxY):
                        oldDepth = self.__worldObj.heightMap[x + z * self.__worldWidth]
                        y = self.__worldHeight - 1
                        while y > 0 and self.__worldObj.lightOpacity[self.__worldObj.blocks[(y * \
                              self.__worldLength + z) * self.__worldWidth + x]] == 0:
                            y -= 1

                        self.__worldObj.heightMap[x + z * self.__worldWidth] = y + 1
                        if oldDepth != y:
                            yl0 = oldDepth if oldDepth < y else y
                            yl1 = oldDepth if oldDepth > y else y
                            self.__updateLists(x, yl0, z, x + 1, yl1, z + 1)

            br = self.__worldObj.skylightSubtracted
            x0 = -999
            x1 = -999
            y0 = -999
            y1 = -999
            z0 = -999
            z1 = -999
            count = 1024
            while count > 0 and (self.__lightingUpdateCounter > 0 or \
                                 len(self.__lightingUpdateList) > 0):
                count -= 1
                if self.__lightingUpdateCounter == 0:
                    if len(self.__lightingUpdateList3):
                        self.__lightingUpdateList2.append(self.__lightingUpdateList3)

                    self.__lightingUpdateList3 = self.__lightingUpdateList.pop()
                    self.__lightingUpdateCounter = self.__lightingUpdateList3[len(self.__lightingUpdateList3) - 1]

                if self.__lightingUpdateCounter > len(self.__lightingUpdateList3) - 32:
                    self.__lightingUpdateCounter -= 1
                    counter = self.__lightingUpdateList3[self.__lightingUpdateCounter]
                    self.__lightingUpdateList3[len(self.__lightingUpdateList3) - 1] = self.__lightingUpdateCounter
                    self.__lightingUpdateList.append(self.__lightingUpdateList3)
                    self.__lightingUpdateList3 = self.__getLightingUpdates()
                    self.__lightingUpdateCounter = 1
                    self.__lightingUpdateList3[0] = counter
                    continue

                self.__lightingUpdateCounter -= 1
                counter = self.__lightingUpdateList3[self.__lightingUpdateCounter]
                x = counter % self.__worldWidth
                y = counter // self.__worldWidth % self.__worldHeight
                z = counter // self.__worldWidth // self.__worldHeight \
                    % self.__worldLength
                self.__chunks[counter >> 3] = <char>(self.__chunks[counter >> 3] ^ 1 << (counter & 7))
                depth = self.__worldObj.heightMap[x + z * self.__worldWidth]
                depth = br if y >= depth else 0
                block = self.__worldObj.blocks[(y * self.__worldLength + z) * self.__worldWidth + x]
                opacity = self.__worldObj.lightOpacity[block]
                if opacity > 100:
                    depth = 0
                elif depth < 15:
                    if opacity == 0:
                        opacity = 1

                    newDepth = 0
                    if x > 0:
                        newDepth = (self.__worldObj.data[(y * self.__worldLength + z) * \
                                    self.__worldWidth + (x - 1)] & 15) - opacity
                        if newDepth > depth:
                            depth = newDepth
                    if x < self.__worldWidth - 1:
                        newDepth = (self.__worldObj.data[(y * self.__worldLength + z) * \
                                    self.__worldWidth + x + 1] & 15) - opacity
                        if newDepth > depth:
                            depth = newDepth
                    if y > 0:
                        newDepth = (self.__worldObj.data[((y - 1) * self.__worldLength + z) * \
                                    self.__worldWidth + x] & 15) - opacity
                        if newDepth > depth:
                            depth = newDepth
                    if y < self.__worldHeight - 1:
                        newDepth = (self.__worldObj.data[((y + 1) * self.__worldLength + z) * \
                                    self.__worldWidth + x] & 15) - opacity
                        if newDepth > depth:
                            depth = newDepth
                    if z > 0:
                        newDepth = (self.__worldObj.data[(y * self.__worldLength + (z - 1)) * \
                                    self.__worldWidth + x] & 15) - opacity
                        if newDepth > depth:
                            depth = newDepth
                    if z < self.__worldLength - 1:
                        newDepth = (self.__worldObj.data[(y * self.__worldLength + z + 1) * \
                                    self.__worldWidth + x] & 15) - opacity
                        if newDepth > depth:
                            depth = newDepth

                depth = max(depth, self.__worldObj.lightValue[block])
                i = (y * self.__worldLength + z) * self.__worldWidth + x
                if (self.__worldObj.data[i] & 15) != depth:
                    self.__worldObj.data[i] = <char>((self.__worldObj.data[i] & 240) + depth)
                    if x > 0 and (self.__worldObj.data[(y * self.__worldLength + z) * \
                                  self.__worldWidth + (x - 1)] & 15) != depth - 1:
                        coord = x - 1 + y * self.__worldWidth + z * self.__worldWidth * self.__worldHeight
                        if (self.__chunks[coord >> 3] & 1 << (coord & 7)) == 0:
                            self.__chunks[coord >> 3] = <char>(self.__chunks[coord >> 3] | 1 << (coord & 7))
                            self.__lightingUpdateList3[self.__lightingUpdateCounter] = coord
                            self.__lightingUpdateCounter += 1
                    if x < self.__worldWidth - 1 and \
                       (self.__worldObj.data[(y * self.__worldLength + z) * \
                        self.__worldWidth + x + 1] & 15) != depth - 1:
                        coord = x + 1 + y * self.__worldWidth + z * self.__worldWidth * self.__worldHeight
                        if (self.__chunks[coord >> 3] & 1 << (coord & 7)) == 0:
                            self.__chunks[coord >> 3] = <char>(self.__chunks[coord >> 3] | 1 << (coord & 7))
                            self.__lightingUpdateList3[self.__lightingUpdateCounter] = coord
                            self.__lightingUpdateCounter += 1
                    if y > 0 and (self.__worldObj.data[((y - 1) * self.__worldLength + z) * \
                                  self.__worldWidth + x] & 15) != depth - 1:
                        coord = x + (y - 1) * self.__worldWidth + z * self.__worldWidth * self.__worldHeight
                        if (self.__chunks[coord >> 3] & 1 << (coord & 7)) == 0:
                            self.__chunks[coord >> 3] = <char>(self.__chunks[coord >> 3] | 1 << (coord & 7))
                            self.__lightingUpdateList3[self.__lightingUpdateCounter] = coord
                            self.__lightingUpdateCounter += 1
                    if y < self.__worldHeight - 1 and \
                       (self.__worldObj.data[((y + 1) * self.__worldLength + z) * \
                        self.__worldWidth + x] & 15) != depth - 1:
                        coord = x + (y + 1) * self.__worldWidth + z * self.__worldWidth * self.__worldHeight
                        if (self.__chunks[coord >> 3] & 1 << (coord & 7)) == 0:
                            self.__chunks[coord >> 3] = <char>(self.__chunks[coord >> 3] | 1 << (coord & 7))
                            self.__lightingUpdateList3[self.__lightingUpdateCounter] = coord
                            self.__lightingUpdateCounter += 1
                    if z > 0 and (self.__worldObj.data[(y * self.__worldLength + \
                                  (z - 1)) * self.__worldWidth + x] & 15) != depth - 1:
                        coord = x + y * self.__worldWidth + (z - 1) * self.__worldWidth * self.__worldHeight
                        if (self.__chunks[coord >> 3] & 1 << (coord & 7)) == 0:
                            self.__chunks[coord >> 3] = <char>(self.__chunks[coord >> 3] | 1 << (coord & 7))
                            self.__lightingUpdateList3[self.__lightingUpdateCounter] = coord
                            self.__lightingUpdateCounter += 1
                    if z < self.__worldLength - 1 and \
                       (self.__worldObj.data[(y * self.__worldLength + z + 1) * \
                        self.__worldWidth + x] & 15) != depth - 1:
                        coord = x + y * self.__worldWidth + (z + 1) * self.__worldWidth * self.__worldHeight
                        if (self.__chunks[coord >> 3] & 1 << (coord & 7)) == 0:
                            self.__chunks[coord >> 3] = <char>(self.__chunks[coord >> 3] | 1 << (coord & 7))
                            self.__lightingUpdateList3[self.__lightingUpdateCounter] = coord
                            self.__lightingUpdateCounter += 1

                    if x0 == -999:
                        x0 = x
                        x1 = x
                        y0 = y
                        y1 = y
                        z0 = z
                        z1 = z

                    if x < x0:
                        x0 = x
                    elif x > x1:
                        x1 = x
                    if y > y1:
                        y1 = y
                    elif y < y0:
                        y0 = y
                    if z < z0:
                        z0 = z
                    elif z > z1:
                        z1 = z

            if x0 > -999:
                self.__skyLightList.append(MetadataChunkBlock(
                        self, x0, y0, z0, x1, y1, z1
                    ))

    def debugLightUpdates(self):
        return str(len(self.__blockLightList) + len(self.__skyLightList))
