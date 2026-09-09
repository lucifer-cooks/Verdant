# cython: language_level=3

cimport cython

import numpy as np
cimport numpy as np

from libc.stdlib cimport malloc, free
from libc.math cimport cos, pi, sqrt, floor, isnan

from mc.net.minecraft.client.render.RenderGlobal cimport RenderGlobal
from mc.net.minecraft.game.physics.MovingObjectPosition import MovingObjectPosition
from mc.net.minecraft.game.level.material.Material import Material
from mc.net.minecraft.game.physics.AxisAlignedBB cimport AxisAlignedBB
from mc.net.minecraft.game.physics.Vec3D import Vec3D
from mc.net.minecraft.game.level.Light cimport Light
from mc.net.minecraft.game.level.EntityMap cimport EntityMap
from mc.net.minecraft.game.level.block.Block cimport Block
from mc.net.minecraft.game.level.block.Blocks import blocks
from mc.net.minecraft.game.level.path.Pathfinder cimport Pathfinder
from mc.JavaUtils cimport Random

import gc

cdef class NextTickListEntry:

    cdef:
        public int xCoord
        public int yCoord
        public int zCoord
        public int blockID
        public int scheduledTime

    def __init__(self, int x, int y, int z, int blockID):
        self.xCoord = x
        self.yCoord = y
        self.zCoord = z
        self.blockID = blockID

cdef short floodFillCounter = 0

cdef class World:
    MAX_TICKS = 200
    TIME_CYCLE = 24000

    def __cinit__(self):
        cdef int i
        cdef float br
        cdef Block block

        self.__maxTicks = World.MAX_TICKS

        for i in range(16):
            br = 1.0 - i / 15.0
            self.__lightBrightnessTable[i] = (1.0 - br) / (br * 3.0 + 1.0) * 0.95 + 0.05

        for i, block in enumerate(blocks.blocksList):
            self.__isBlockNormal[i] = False if block is None else block.isOpaqueCube()
            self.__isTickOnLoad[i] = blocks.tickOnLoad[i]

        self.rotSpawn = 0.0

        self.defaultFluid = blocks.waterMoving.blockID

        self.worldAccesses = []
        self.__tickList = set()

        self.map = {}
        self.__list = []

        self.rand = Random()
        self.__rand = Random()
        self.__randId = self.rand.nextInt()

        self.skyColor = 0x99CCFF
        self.fogColor = 0xFFFFFF
        self.cloudColor = 0xFFFFFF

        self.__playTime = 0
        self.__updateLCG = 0

        self.multiplier = 3
        self.addend = 1013904223

        self.survivalWorld = True

        self.skyBrightness = 15
        self.skylightSubtracted = 15

        self.pathFinder = Pathfinder(self)

        self.worldTime = 0
        self.difficultySetting = 2
        self.__timeCycle = World.TIME_CYCLE

    def __dealloc__(self):
        free(self.blocks)
        free(self.data)
        free(self.heightMap)

    def load(self):
        if not self.blocks:
            raise RuntimeError('The level is corrupt!')

        self.worldAccesses = []
        self.heightMap = <int*>malloc(sizeof(int) * (self.width * self.length))
        for i in range(self.width * self.length):
            self.heightMap[i] = self.height

        self.__lightUpdates.updateSkylight(0, 0, self.width, self.length)
        self.__randId = self.rand.nextInt()
        self.__tickList = set()

        if not self.entityMap:
            self.entityMap = EntityMap(self.width, self.height, self.length)

    def generate(self, int w, int h, int d, bytearray b, bytearray data):
        cdef int x, y, z, i, skyBrightness, br
        cdef char blockId

        self.width = w
        self.height = h
        self.length = d
        self.blocks = <char*>malloc(sizeof(char) * len(b))
        self.blocksSize = len(b)

        for i in range(256):
            self.lightOpacity[i] = blocks.lightOpacity[i]
            self.lightValue[i] = blocks.lightValue[i]

        for x in range(self.width):
            for z in range(self.length):
                y = 0
                while y < self.height:
                    blockId = 0
                    if y <= 1 and y < self.groundLevel - 1 and \
                       b[((y + 1) * self.length + z) * self.width + x]:
                        blockId = blocks.lavaStill.blockID
                    elif y < self.groundLevel - 1:
                        blockId = blocks.bedrock.blockID
                    elif y < self.groundLevel:
                        if self.groundLevel > self.waterLevel and \
                           self.defaultFluid == blocks.waterMoving.blockID:
                            blockId = blocks.grass.blockID
                        else:
                            blockId = blocks.dirt.blockID
                    elif y < self.waterLevel:
                        blockId = self.defaultFluid

                    b[(y * self.length + z) * self.width + x] = blockId
                    if y == 1 and x != 0 and z != 0 and x != self.width - 1 and z != self.length - 1:
                        y = self.height - 2

                    y += 1

        for i in range(len(b)):
            self.blocks[i] = b[i]

        self.heightMap = <int*>malloc(sizeof(int) * (w * d))
        for i in range(w * d):
            self.heightMap[i] = h

        if data:
            self.data = <char*>malloc(sizeof(char) * len(data))
            for i in range(len(data)):
                self.data[i] = data[i]

            self.__lightUpdates = Light(self)
        else:
            self.data = <char*>malloc(sizeof(char) * len(b))
            for i in range(len(b)):
                self.data[i] = 0

            self.__lightUpdates = Light(self)
            skyBrightness = self.skylightSubtracted
            for x in range(self.width):
                for z in range(self.length):
                    y = self.height - 1
                    while y > 0 and self.lightOpacity[self.getBlockId(x, y, z)] == 0:
                        y -= 1

                    self.heightMap[x + z * self.width] = y + 1
                    for y in range(self.height):
                        i = (y * self.length + z) * self.width + x
                        br = self.heightMap[x + z * self.width]
                        br = skyBrightness if y >= br else 0
                        br = max(br, self.lightValue[<char>(self.blocks[i])])
                        self.data[i] = <char>((self.data[i] & 240) + br)

            self.__lightUpdates.updateBlockLight(0, 0, 0, self.width,
                                                 self.height, self.length)

        for worldAccess in self.worldAccesses:
            worldAccess.loadRenderers()

        self.__tickList.clear()
        self.findSpawn()
        self.load()
        gc.collect()

    cdef findSpawn(self):
        cdef int i, x, y, z, xx, yy, zz
        cdef Random random = Random()

        x = 0
        y = 0
        z = 0
        i = 0
        while True:
            i += 1
            x = random.nextInt(self.width // 2) + self.width // 4
            z = random.nextInt(self.length // 2) + self.length // 4
            y = self.__getFirstUncoveredBlock(x, z) + 1
            if i == 10000:
                self.xSpawn = x
                self.ySpawn = self.height + 100
                self.zSpawn = z
                self.rotSpawn = 180.0
                break

            if y >= 4 and y > self.waterLevel:

                def checkSolid():
                    for xx in range(x - 3, x + 4):
                        for yy in range(y - 1, y + 3):
                            for zz in range(z - 5, z + 4):
                                if self.getBlockMaterial(xx, yy, zz).isSolid():
                                    return True

                    return False

                def checkOpaque():
                    for xx in range(x - 3, x + 4):
                        for zz in range(z - 5, z + 4):
                            if not blocks.opaqueCubeLookup[self.getBlockId(xx, y - 2,
                                                                           zz)]:
                                return True

                    return False

                if checkSolid() or checkOpaque():
                    continue

                self.xSpawn = x
                self.ySpawn = y
                self.zSpawn = z
                self.rotSpawn = 180.0
                break

    def addWorldAccess(self, worldAccess):
        for entity in self.entityMap.all:
            worldAccess.obtainEntitySkin(entity)

        self.worldAccesses.append(worldAccess)

    def finalize(self):
        pass

    def removeWorldAccess(self, worldAccess):
        self.worldAccesses.remove(worldAccess)

    def getCollidingBoundingBoxes(self, AxisAlignedBB box):
        cdef int minX, maxX, minY, maxY, minZ, maxZ, x, y, z
        cdef Block block
        cdef AxisAlignedBB aabb

        boxes = []
        minX = <int>box.minX
        maxX = <int>box.maxX + 1
        minY = <int>box.minY
        maxY = <int>box.maxY + 1
        minZ = <int>box.minZ
        maxZ = <int>box.maxZ + 1
        if box.minX < 0.0:
            minX -= 1
        if box.minY < 0.0:
            minY -= 1
        if box.minZ < 0.0:
            minZ -= 1

        for x in range(minX, maxX):
            for y in range(minY, maxY):
                for z in range(minZ, maxZ):
                    block = blocks.blocksList[self.getBlockId(x, y, z)]
                    if block:
                        aabb = block.getCollisionBoundingBoxFromPool(x, y, z)
                        if aabb and box.intersectsWith(aabb):
                            boxes.append(aabb)
                    elif self.groundLevel < 0 and (y < self.groundLevel or y < self.waterLevel):
                        aabb = blocks.bedrock.getCollisionBoundingBoxFromPool(x, y, z)
                        if aabb and box.intersectsWith(aabb):
                            boxes.append(aabb)

        return boxes

    cpdef swap(self, int x0, int y0, int z0, int x1, int y1, int z1):
        cdef int block1 = self.getBlockId(x0, y0, z0)
        cdef int block2 = self.getBlockId(x1, y1, z1)
        self.setBlock(x0, y0, z0, block2)
        self.setBlock(x1, y1, z1, block1)
        self.notifyBlocksOfNeighborChange(x0, y0, z0, block2)
        self.notifyBlocksOfNeighborChange(x1, y1, z1, block1)

    cpdef bint setBlock(self, int x, int y, int z, int blockType):
        cdef char oldBlock
        cdef RenderGlobal worldAccess

        if x <= 0 or y <= 0 or z <= 0 or x >= self.width - 1 or y >= self.height - 1 or z >= self.length - 1:
            return False

        oldBlock = self.blocks[(y * self.length + z) * self.width + x]
        if blockType == oldBlock:
            return False

        if blockType == 0 and (x == 0 or z == 0 or x == self.width - 1 or \
            z == self.length - 1) and y >= self.groundLevel and y < self.waterLevel:
            blockType = blocks.waterMoving.blockID

        self.blocks[(y * self.length + z) * self.width + x] = <char>blockType
        self.setBlockMetadata(x, y, z, 0)
        if oldBlock != 0:
            blocks.blocksList[oldBlock].onBlockRemoval(self, x, y, z)

        if blockType != 0:
            blocks.blocksList[blockType].onBlockAdded(self, x, y, z)

        if self.lightOpacity[oldBlock] != self.lightOpacity[blockType] or \
           self.lightValue[oldBlock] != 0 or self.lightValue[blockType] != 0:
            self.__lightUpdates.updateSkylight(x, z, 1, 1)
            self.__lightUpdates.updateBlockLight(x, y, z, x + 1, y + 1, z + 1)

        for worldAccess in self.worldAccesses:
            worldAccess.markBlockAndNeighborsNeedsUpdate(x, y, z)

        return True

    cpdef bint setBlockWithNotify(self, int x, int y, int z, int blockType):
        if self.setBlock(x, y, z, blockType):
            self.notifyBlocksOfNeighborChange(x, y, z, blockType)
            return True
        else:
            return False

    cpdef notifyBlocksOfNeighborChange(self, int x, int y, int z, int blockType):
        self.__notifyBlockOfNeighborChange(x - 1, y, z, blockType)
        self.__notifyBlockOfNeighborChange(x + 1, y, z, blockType)
        self.__notifyBlockOfNeighborChange(x, y - 1, z, blockType)
        self.__notifyBlockOfNeighborChange(x, y + 1, z, blockType)
        self.__notifyBlockOfNeighborChange(x, y, z - 1, blockType)
        self.__notifyBlockOfNeighborChange(x, y, z + 1, blockType)

    cpdef bint setTileNoUpdate(self, int x, int y, int z, int blockType):
        if x < 0 or y < 0 or z < 0 or x >= self.width or y >= self.height or z >= self.length:
            return False
        if blockType == self.blocks[(y * self.length + z) * self.width + x]:
            return False

        self.blocks[(y * self.length + z) * self.width + x] = <char>blockType
        self.__lightUpdates.updateBlockLight(x, y, z, x + 1, y + 1, z + 1)
        return True

    cdef __notifyBlockOfNeighborChange(self, int x, int y, int z, int blockType):
        if x < 0 or y < 0 or z < 0 or x >= self.width or y >= self.height or z >= self.length:
            return

        cdef Block block = blocks.blocksList[self.blocks[(y * self.length + z) * self.width + x]]
        if block:
            block.onNeighborBlockChange(self, x, y, z, blockType)

    cpdef inline int getBlockId(self, int x, int y, int z):
        if x < 0:
            x = 0
        elif x >= self.width:
            x = self.width - 1
        if y < 0:
            y = 0
        elif y >= self.height:
            y = self.height - 1
        if z < 0:
            z = 0
        elif z >= self.length:
            z = self.length - 1

        return self.blocks[(y * self.length + z) * self.width + x] & 255

    cpdef inline bint isBlockNormalCube(self, int x, int y, int z):
        cdef Block block = blocks.blocksList[self.getBlockId(x, y, z)]
        return block.isOpaqueCube() if block else False

    def updateEntities(self):
        self.entityMap.updateEntities()
        for entity in self.__list:
            entity.updateEntity()

    def updateLighting(self):
        self.__lightUpdates.updateLight()

    cdef float getStarBrightness(self, float alpha):
        cdef float theta = self.getCelestialAngle(alpha)
        theta = 1.0 - (cos(theta * pi * 2.0) * 2.0 + 12.0 / 16.0)
        theta = min(max(theta, 0.0), 1.0)
        return theta * theta * 0.5

    def getSkyColor(self, float alpha):
        cdef float theta, x, y, z

        theta = self.getCelestialAngle(alpha)
        theta = cos(theta * pi * 2.0) * 2.0 + 0.5
        theta = min(max(theta, 0.0), 1.0)

        x = (self.skyColor >> 16 & 255) / 255.0
        y = (self.skyColor >> 8 & 255) / 255.0
        z = (self.skyColor & 255) / 255.0
        x *= theta
        y *= theta
        z *= theta
        return Vec3D(x, y, z)

    cdef float getCelestialAngle(self, float alpha):
        if self.skyBrightness > 15:
            return 0.0
        else:
            return (self.worldTime + alpha) / self.__timeCycle - 0.15

    def getFogColor(self, float alpha):
        cdef float theta, x, y, z

        theta = self.getCelestialAngle(alpha)
        theta = cos(theta * pi * 2.0) * 2.0 + 0.5
        theta = min(max(theta, 0.0), 1.0)

        x = (self.fogColor >> 16 & 255) / 255.0
        y = (self.fogColor >> 8 & 255) / 255.0
        z = (self.fogColor & 255) / 255.0
        x *= theta * 0.94 + 0.06
        y *= theta * 0.94 + 0.06
        z *= theta * 0.91 + 0.09
        return Vec3D(x, y, z)

    def getCloudColor(self, float alpha):
        cdef float theta, x, y, z

        theta = self.getCelestialAngle(alpha)
        theta = cos(theta * pi * 2.0) * 2.0 + 0.5
        theta = min(max(theta, 0.0), 1.0)

        x = (self.cloudColor >> 16 & 255) / 255.0
        y = (self.cloudColor >> 8 & 255) / 255.0
        z = (self.cloudColor & 255) / 255.0
        x *= theta * 0.9 + 0.1
        y *= theta * 0.9 + 0.1
        z *= theta * 0.85 + 0.15
        return Vec3D(x, y, z)

    def getSkyBrightness(self):
        cdef int br
        cdef float theta = self.getCelestialAngle(1.0)
        theta = cos(theta * pi * 2.0) * 1.5 + 0.5
        theta = min(max(theta, 0.0), 1.0)
        br = <int>(theta * ((15 * self.skyBrightness) / 15.0 - 4.0) + 4.0)
        return max(min(br, 15), 4)

    @cython.cdivision(True)
    @cython.boundscheck(False)
    @cython.wraparound(False)
    def tick(self):
        cdef int br, wShift, lShift, h, w, d, ticks, i, randValue, x, y, z, blockId
        cdef char b
        cdef NextTickListEntry posType

        self.worldTime += 1
        if self.worldTime == self.__timeCycle:
            self.worldTime = 0

        br = self.getSkyBrightness();
        if self.skylightSubtracted > br:
            self.__updateChunkLight(self.skylightSubtracted - 1)
        if self.skylightSubtracted < br:
            self.__updateChunkLight(self.skylightSubtracted + 1)

        self.__playTime += 1

        wShift = 1
        lShift = 1

        while 1 << wShift < self.width:
            wShift += 1
        while 1 << lShift < self.length:
            lShift += 1

        l = self.length - 1
        w = self.width - 1
        h = self.height - 1

        ticks = min(len(self.__tickList), self.__maxTicks)
        for i in range(ticks):
            posType = self.__tickList.pop()
            if posType.scheduledTime > 0:
                posType.scheduledTime -= 1
                self.__tickList.add(posType)
            else:
                b = self.blocks[(posType.yCoord * self.length + posType.zCoord) * self.width + posType.xCoord]
                if self.__isInLevelBounds(posType.xCoord, posType.yCoord, posType.zCoord) and \
                   b == posType.blockID and b > 0:
                    blocks.blocksList[b].updateTick(
                        self, posType.xCoord, posType.yCoord,
                        posType.zCoord, self.rand
                    )

        self.__updateLCG += self.width * self.length * self.height
        ticks = self.__updateLCG // self.__maxTicks
        self.__updateLCG -= ticks * self.__maxTicks
        for i in range(ticks):
            self.__randId = self.__randId * self.multiplier + self.addend
            randValue = self.__randId >> 2
            x = randValue & w
            y = randValue >> wShift + lShift & h
            z = randValue >> wShift & l
            blockId = self.blocks[(y * self.length + z) * self.width + x]
            if self.__isTickOnLoad[blockId]:
                blocks.blocksList[blockId].updateTick(self, x, y, z, self.rand)

    def entitiesInLevelList(self, cls):
        count = 0
        for obj in self.entityMap.all:
            if isinstance(obj, cls):
                count += 1

        return count

    cdef inline bint __isInLevelBounds(self, int x, int y, int z):
        return x >= 0 and y >= 0 and z >= 0 and x < self.width and y < self.height and z < self.length

    cpdef inline int getGroundLevel(self):
        return self.groundLevel

    cdef inline int getWaterLevel(self):
        return self.waterLevel

    cdef bint getIsAnyLiquid(self, AxisAlignedBB box):
        cdef int minX, maxX, minY, maxY, minZ, maxZ, x, y, z
        cdef Block block

        minX = <int>floor(box.minX)
        maxX = <int>floor(box.maxX + 1.0)
        minY = <int>floor(box.minY)
        maxY = <int>floor(box.maxY + 1.0)
        minZ = <int>floor(box.minZ)
        maxZ = <int>floor(box.maxZ + 1.0)
        if box.minX < 0.0:
            minX -= 1
        if box.minY < 0.0:
            minY -= 1
        if box.minZ < 0.0:
            minZ -= 1

        if minX < 0: minX = 0
        if minY < 0: minY = 0
        if minZ < 0: minZ = 0
        if maxX > self.width: maxX = self.width
        if maxY > self.height: maxY = self.height
        if maxZ > self.length: maxZ = self.length
        for x in range(minX, maxX):
            for y in range(minY, maxY):
                for z in range(minZ, maxZ):
                    block = blocks.blocksList[self.getBlockId(x, y, z)]
                    if block and block.material.getIsLiquid():
                        return True

        return False

    cdef bint isBoundingBoxBurning(self, AxisAlignedBB box):
        cdef int minX, maxX, minY, maxY, minZ, maxZ, x, y, z, blockId

        minX = <int>floor(box.minX)
        maxX = <int>floor(box.maxX + 1.0)
        minY = <int>floor(box.minY)
        maxY = <int>floor(box.maxY + 1.0)
        minZ = <int>floor(box.minZ)
        maxZ = <int>floor(box.maxZ + 1.0)
        for x in range(minX, maxX):
            for y in range(minY, maxY):
                for z in range(minZ, maxZ):
                    blockId = self.getBlockId(x, y, z)
                    if blockId == blocks.fire.blockID or blockId == blocks.lavaMoving.blockID or \
                       blockId == blocks.lavaStill.blockID:
                        return True

        return False

    cdef bint handleMaterialAcceleration(self, AxisAlignedBB box, material):
        cdef int minX, maxX, minY, maxY, minZ, maxZ, x, y, z
        cdef Block block

        minX = <int>floor(box.minX)
        maxX = <int>floor(box.maxX + 1.0)
        minY = <int>floor(box.minY)
        maxY = <int>floor(box.maxY + 1.0)
        minZ = <int>floor(box.minZ)
        maxZ = <int>floor(box.maxZ + 1.0)
        for x in range(minX, maxX):
            for y in range(minY, maxY):
                for z in range(minZ, maxZ):
                    block = blocks.blocksList[self.getBlockId(x, y, z)]
                    if block and block.material == material:
                        return True

        return False

    cpdef inline scheduleBlockUpdate(self, int x, int y, int z, int blockType):
        cdef int tickDelay
        cdef NextTickListEntry posType

        posType = NextTickListEntry(x, y, z, blockType)
        if blockType > 0:
            tickDelay = (<Block>blocks.blocksList[blockType]).tickRate()
            posType.scheduledTime = tickDelay

        self.__tickList.add(posType)

    cpdef bint checkIfAABBIsClear(self, AxisAlignedBB aabb):
        return len(self.entityMap.getEntitiesWithinAABB(None, aabb)) == 0

    cpdef bint checkIfAABBIsClearSpawn(self, AxisAlignedBB aabb):
        entities = self.entityMap.getEntitiesWithinAABB(None, aabb)
        for entity in entities:
            if entity.preventEntitySpawning:
                return False

        return True

    def getEntitiesWithinAABBExcludingEntity(self, entity, AxisAlignedBB aabb):
        return self.entityMap.getEntitiesWithinAABB(entity, aabb)

    cpdef inline bint isSolid(self, float x, float y, float z, float offset):
        if self.__isBlockOpaque(x - 0.1, y - 0.1, z - 0.1):
            return True
        elif self.__isBlockOpaque(x - 0.1, y - 0.1, z + 0.1):
            return True
        elif self.__isBlockOpaque(x - 0.1, y + 0.1, z - 0.1):
            return True
        elif self.__isBlockOpaque(x - 0.1, y + 0.1, z + 0.1):
            return True
        elif self.__isBlockOpaque(x + 0.1, y - 0.1, z - 0.1):
            return True
        elif self.__isBlockOpaque(x + 0.1, y - 0.1, z + 0.1):
            return True
        elif self.__isBlockOpaque(x + 0.1, y + 0.1, z - 0.1):
            return True
        else:
            return self.__isBlockOpaque(x + 0.1, y + 0.1, z + 0.1)

    cdef inline bint __isBlockOpaque(self, float x, float y, float z):
        cdef int block = self.getBlockId(<int>x, <int>y, <int>z)
        return block > 0 and (<Block>blocks.blocksList[block]).isOpaqueCube()

    cpdef __getFirstUncoveredBlock(self, int x, int z):
        cdef int y = self.height
        cdef int blockId = self.getBlockId(x, y - 1, z)
        while self.getBlockId(x, y - 1, z) == 0 or \
              blocks.blocksList[self.getBlockId(x, y - 1, z)].material == Material.air:
            y -= 1
            if y == 0:
                break

        return y

    cpdef setSpawnLocation(self, int x, int y, int z, float rotationYaw):
        self.xSpawn = x
        self.ySpawn = y
        self.zSpawn = z
        self.rotSpawn = rotationYaw

    cpdef inline float getBrightness(self, int x, int y, int z):
        return self.__lightBrightnessTable[self.getBlockLightValue(x, y, z)]

    cpdef inline char getBlockLightValue(self, int x, int y, int z):
        if x < 0:
            x = 0
        elif x >= self.width:
            x = self.width - 1
        if y < 0:
            y = 0
        elif y >= self.height:
            y = self.height - 1
        if z < 0:
            z = 0
        elif z >= self.length:
            z = self.length - 1

        if self.blocks[(y * self.length + z) * self.width + x] == blocks.stairSingle.blockID:
            if y < self.height - 1:
                return <char>(self.data[((y + 1) * self.length + z) * self.width + x] & 15)
            else:
                return 15
        else:
            return <char>(self.data[(y * self.length + z) * self.width + x] & 15)

    cpdef inline char getBlockMetadata(self, int x, int y, int z):
        if x < 0:
            x = 0
        elif x >= self.width:
            x = self.width - 1
        if y < 0:
            y = 0
        elif y >= self.height:
            y = self.height - 1
        if z < 0:
            z = 0
        elif z >= self.length:
            z = self.length - 1

        return <char>((self.data[(y * self.length + z) * self.width + x] % 0x100000000) >> 4 & 15)

    cpdef setBlockMetadata(self, int x, int y, int z, int metadata):
        cdef int dataIdx
        cdef RenderGlobal worldAccess

        if x < 0:
            x = 0
        elif x >= self.width:
            x = self.width - 1
        if y < 0:
            y = 0
        elif y >= self.height:
            y = self.height - 1
        if z < 0:
            z = 0
        elif z >= self.length:
            z = self.length - 1

        dataIdx = (y * self.length + z) * self.width + x
        self.data[dataIdx] = <char>((self.data[dataIdx] & 15) + (metadata << 4))

        for worldAccess in self.worldAccesses:
            worldAccess.markBlockAndNeighborsNeedsUpdate(x, y, z)

    def getBlockMaterial(self, int x, int y, int z):
        cdef int block = self.getBlockId(x, y, z)
        if block == 0:
            return Material.air

        return blocks.blocksList[block].material

    cpdef inline bint isWater(self, int x, int y, int z):
        cdef int block = self.getBlockId(x, y, z)
        return block > 0 and blocks.blocksList[block].material == Material.water

    @cython.cdivision(True)
    def rayTraceBlocks(self, vec1, vec2):
        cdef int x0, y0, z0, x1, y1, z1, radius, blockId
        cdef float x, y, z, xSide, ySide, zSide, xd, yd, zd
        cdef char sideHit
        cdef Block block

        if isnan(vec1.xCoord) or isnan(vec1.yCoord) or isnan(vec1.zCoord):
            return None
        if isnan(vec2.xCoord) or isnan(vec2.yCoord) or isnan(vec2.zCoord):
            return None

        x0 = <int>floor(vec2.xCoord)
        y0 = <int>floor(vec2.yCoord)
        z0 = <int>floor(vec2.zCoord)
        x1 = <int>floor(vec1.xCoord)
        y1 = <int>floor(vec1.yCoord)
        z1 = <int>floor(vec1.zCoord)
        radius = 20
        blockId = self.getBlockId(x1, y1, z1)
        while radius >= 0:
            radius -= 1

            if isnan(vec1.xCoord) or isnan(vec1.yCoord) or isnan(vec1.zCoord):
                return None

            if x1 == x0 and y1 == y0 and z1 == z0:
                return None

            x = 999.0
            y = 999.0
            z = 999.0
            if x0 > x1:
                x = x1 + 1.0
            elif x0 < x1:
                x = x1

            if y0 > y1:
                y = y1 + 1.0
            elif y0 < y1:
                y = y1

            if z0 > z1:
                z = z1 + 1.0
            elif z0 < z1:
                z = z1

            xSide = 999.0
            ySide = 999.0
            zSide = 999.0
            xd = vec2.xCoord - vec1.xCoord
            yd = vec2.yCoord - vec1.yCoord
            zd = vec2.zCoord - vec1.zCoord
            if x != 999.0:
                xSide = (x - vec1.xCoord) / xd

            if y != 999.0:
                ySide = (y - vec1.yCoord) / yd

            if z != 999.0:
                zSide = (z - vec1.zCoord) / zd

            sideHit = 0
            if xSide < ySide and xSide < zSide:
                if x0 > x1:
                    sideHit = 4
                else:
                    sideHit = 5

                vec1.xCoord = x
                vec1.yCoord += yd * xSide
                vec1.zCoord += zd * xSide
            elif ySide < zSide:
                if y0 > y1:
                    sideHit = 0
                else:
                    sideHit = 1

                vec1.xCoord += xd * ySide
                vec1.yCoord = y
                vec1.zCoord += zd * ySide
            else:
                if z0 > z1:
                    sideHit = 2
                else:
                    sideHit = 3

                vec1.xCoord += xd * zSide
                vec1.yCoord += yd * zSide
                vec1.zCoord = z

            posVec = Vec3D(vec1.xCoord, vec1.yCoord, vec1.zCoord)
            posVec.xCoord = floor(vec1.xCoord)
            x1 = <int>posVec.xCoord
            if sideHit == 5:
                x1 -= 1
                posVec.xCoord += 1.0

            posVec.yCoord = floor(vec1.yCoord)
            y1 = <int>posVec.yCoord
            if sideHit == 1:
                y1 -= 1
                posVec.yCoord += 1.0

            posVec.zCoord = floor(vec1.zCoord)
            z1 = <int>posVec.zCoord
            if sideHit == 3:
                z1 -= 1
                posVec.zCoord += 1.0

            blockId = self.getBlockId(x1, y1, z1)
            if blockId > 0:
                block = blocks.blocksList[blockId]
                if block.isCollidable():
                    hitResult = block.collisionRayTrace(self, x1, y1, z1, vec1, vec2)
                    if hitResult:
                        return hitResult

    cpdef bint growTrees(self, int x, int y, int z):
        cdef int logs, xx, yy, zz, i, leafExt, leafExtLeft, offset
        cdef bint willGrow
        cdef char block

        logs = self.rand.nextInt(3) + 4
        willGrow = True

        if y <= 0 or y + logs + 1 > self.height:
            return False

        for yy in range(y, y + 2 + logs):
            offset = 1
            if yy == y:
                offset = 0
            if yy >= y + 1 + logs - 2:
                offset = 2

            for xx in range(x - offset, x + offset + 1):
                if not willGrow:
                    break

                for zz in range(z - offset, z + offset + 1):
                    if not willGrow:
                        break

                    if xx >= 0 and yy >= 0 and zz >= 0 and xx < self.width and \
                       yy < self.height and zz < self.length:
                        block = self.blocks[(yy * self.length + zz) * self.width + xx] & 0xFF
                        if block != 0:
                            willGrow = False
                    else:
                        willGrow = False

        if not willGrow:
            return False

        block = self.blocks[((y - 1) * self.length + z) * self.width + x] & 0xFF
        if (block != blocks.grass.blockID and block != blocks.dirt.blockID) or \
           y >= self.height - logs - 1:
            return False

        self.setBlockWithNotify(x, y - 1, z, blocks.dirt.blockID)
        for yy in range(y - 3 + logs, y + logs + 1):
            leafExtLeft = yy - (y + logs)
            leafExt = <int>(1 - leafExtLeft / 2)
            for xx in range(x - leafExt, x + leafExt + 1):
                for zz in range(z - leafExt, z + leafExt + 1):
                    if (abs(xx - x) != leafExt or abs(zz - z) != leafExt or \
                        self.rand.nextInt(2) != 0 and leafExtLeft != 0) and not \
                       blocks.opaqueCubeLookup[self.getBlockId(xx, yy, zz)]:
                        self.setBlockWithNotify(xx, yy, zz, blocks.leaves.blockID)

        for i in range(logs):
            if not blocks.opaqueCubeLookup[self.getBlockId(x, y + i, z)]:
                self.setBlockWithNotify(x, y + i, z, blocks.wood.blockID)

        return True

    def getPlayerEntity(self):
        return self.playerEntity

    def spawnEntityInWorld(self, entity):
        cdef RenderGlobal worldAccess

        self.entityMap.insert(entity)
        entity.setWorld(self)
        for worldAccess in self.worldAccesses:
            worldAccess.obtainEntitySkin(entity)

    def releaseEntitySkin(self, entity):
        cdef RenderGlobal worldAccess

        self.entityMap.remove(entity)
        for worldAccess in self.worldAccesses:
            worldAccess.releaseEntitySkin(entity)

    @cython.cdivision(True)
    def createExplosion(self, entity, float x, float y, float z, float radius):
        cdef int minX, maxX, minY, maxY, minZ, maxZ, xx, yy, zz, posX, posY, posZ, \
                 blockId, pos, i
        cdef float xd, yd, zd, d, radX, radY, radZ, fallout, nextX, nextY, nextZ, \
                   density, pX, pY, pZ, xr, yr, zr
        cdef list entities, positions
        cdef Block block

        self.playSoundAtPlayer(
            x, y, z, 'random.explode', 4.0,
            (1.0 + (self.rand.nextFloat() - self.rand.nextFloat()) * 0.2) * 0.7
        )
        explodePositions = set()

        for xx in range(16):
            for yy in range(16):
                for zz in range(16):
                    if xx == 0 or xx == 15 or yy == 0 or \
                       yy == 15 or zz == 0 or zz == 15:
                        radX = xx / 15.0 * 2.0 - 1.0
                        radY = yy / 15.0 * 2.0 - 1.0
                        radZ = zz / 15.0 * 2.0 - 1.0
                        d = sqrt(radX * radX + radY * radY + radZ * radZ)
                        radX /= d
                        radY /= d
                        radZ /= d
                        fallout = radius * (0.7 + self.rand.nextFloat() * 0.6)
                        nextX = x
                        nextY = y
                        nextZ = z
                        while fallout > 0.0:
                            posX = <int>nextX
                            posY = <int>nextY
                            posZ = <int>nextZ
                            blockId = self.getBlockId(posX, posY, posZ)
                            if blockId > 0:
                                fallout -= ((<Block>blocks.blocksList[blockId]).getExplosionResistance() + 0.3) * 0.3

                            if fallout > 0.0:
                                pos = posX + (posY << 10) + (posZ << 10 << 10)
                                explodePositions.add(pos)

                            nextX += radX * 0.3
                            nextY += radY * 0.3
                            nextZ += radZ * 0.3
                            fallout -= 0.3

        radius *= 2.0
        minX = <int>(x - radius - 1.0)
        maxX = <int>(x + radius + 1.0)
        minY = <int>(y - radius - 1.0)
        maxY = <int>(y + radius + 1.0)
        minZ = <int>(z - radius - 1.0)
        maxZ = <int>(z + radius + 1.0)
        entities = self.entityMap.getEntities(entity, minX, minY, minZ, maxX, maxY, maxZ)
        vec = Vec3D(x, y, z)
        for e in entities:
            xd = e.posX - x
            yd = e.posY - y
            zd = e.posZ - z
            d = sqrt(xd * xd + yd * yd + zd * zd) / radius
            if d > 1.0:
                continue

            d = sqrt(xd * xd + yd * yd + zd * zd)
            if not d:
                continue

            xd /= d
            yd /= d
            zd /= d
            density = self.__getBlockDensity(vec, e.boundingBox)
            d = (1.0 - (d / radius)) * density
            e.attackEntityFrom(entity, <int>((d * d + d) / 2.0 * 8.0 * radius + 1.0))
            e.motionX += xd * d
            e.motionY += yd * d
            e.motionZ += zd * d

        radius /= 2.0
        positions = list(explodePositions)
        for i in range(len(positions) - 1, -1, -1):
            pos = positions[i]
            posX = pos & 1023
            posY = pos >> 10 & 1023
            posZ = pos >> 20 & 1023
            if posX >= 0 and posY >= 0 and posZ >= 0 and posX < self.width and \
               posY < self.height and posZ < self.length:
                blockId = self.getBlockId(posX, posY, posZ)
                pX = posX + self.rand.nextFloat()
                pY = posY + self.rand.nextFloat()
                pZ = posZ + self.rand.nextFloat()
                xr = pX - x
                yr = pY - y
                zr = pZ - z
                d = sqrt(xr * xr + yr * yr + zr * zr)
                xr /= d
                yr /= d
                zr /= d
                d = 0.5 / (d / radius + 0.1)
                d *= self.rand.nextFloat() * self.rand.nextFloat() + 0.3
                xr *= d
                yr *= d
                zr *= d
                self.spawnParticle(
                    'explode', (pX + x) / 2.0, (pY + y) / 2.0, (pZ + z) / 2.0,
                    xr, yr, zr
                )
                self.spawnParticle('smoke', pX, pY, pZ, xr, yr, zr)

                if blockId > 0:
                    block = <Block>blocks.blocksList[blockId]
                    block.dropBlockAsItemWithChance(
                        self, posX, posY, posZ,
                        self.getBlockMetadata(posX, posY, posZ), 0.3
                    )
                    self.setBlockWithNotify(posX, posY, posZ, 0)
                    block.onBlockDestroyedByExplosion(self, posX, posY, posZ)

    @cython.cdivision(True)
    cdef float __getBlockDensity(self, vec, AxisAlignedBB box):
        cdef float xd, yd, zd, minX, minY, minZ, x, y, z
        cdef int noHits, total

        xd = 1.0 / ((box.maxX - box.minX) * 2.0 + 1.0)
        yd = 1.0 / ((box.maxY - box.minY) * 2.0 + 1.0)
        zd = 1.0 / ((box.maxZ - box.minZ) * 2.0 + 1.0)
        noHits = 0
        total = 0
        minX = 0.0
        while minX <= 1.0:
            minY = 0.0
            while minY <= 1.0:
                minZ = 0.0
                while minZ <= 1.0:
                    x = box.minX + (box.maxX - box.minX) * minX
                    y = box.minY + (box.maxY - box.minY) * minY
                    z = box.minZ + (box.maxZ - box.minZ) * minZ
                    if not self.rayTraceBlocks(Vec3D(x, y, z), vec):
                        noHits += 1

                    total += 1
                    minZ += zd

                minY += yd

            minX += xd

        return noHits / total

    def findSubclassOf(self, cls):
        for entity in self.entityMap.all:
            if issubclass(entity.__class__, cls):
                return entity

    cdef int fluidFlowCheck(self, int x, int y, int z, int source, int tt):
        cdef int orgX, orgZ, pos, flooded, sourceBlock, floodedBlocks, lastDistance, i, \
                 lastVal, coord, zd, xd
        cdef bint sourceFlow, negative, lastNorth, lastSouth, lastBelow, \
                  north, south, below
        cdef char blockId

        if x < 0 or y < 0 or z < 0 or x >= self.width or y >= self.height or z >= self.length:
            return -1

        orgX = x
        orgZ = z
        pos = ((y << 10) + z << 10) + x
        flooded = 1
        self.__coords[0] = x + (z << 10)
        sourceBlock = -9999
        if source == blocks.waterStill.blockID or source == blocks.waterMoving.blockID:
            sourceBlock = blocks.waterSource.blockID
        if source == blocks.lavaStill.blockID or source == blocks.lavaMoving.blockID:
            sourceBlock = blocks.lavaSource.blockID

        global floodFillCounter
        floodedBlocks = 0
        while True:
            sourceFlow = False
            lastDistance = -1
            floodedBlocks = 0
            floodFillCounter += 1
            if floodFillCounter == 30000:
                for i in range(1048576):
                    self.__floodFillCounters[i] = 0

                floodFillCounter = 1

            while True:
                negative = False
                while True:
                    if flooded <= 0:
                        y += 1
                        for i in range(1048576):
                            lastVal = self.__floodedBlocks[i]
                            self.__floodedBlocks[i] = self.__coords[i]
                            self.__coords[i] = lastVal

                        flooded = floodedBlocks
                        negative = True
                        break

                    flooded -= 1
                    coord = self.__coords[flooded]
                    if self.__floodFillCounters[coord] != floodFillCounter:
                        break

                if negative:
                    break

                x = coord % 1024
                z = coord // 1024
                zd = z - orgZ
                zd *= zd

                while x > 0 and self.__floodFillCounters[coord - 1] != floodFillCounter and \
                     (self.blocks[(y * self.length + z) * self.width + x - 1] == source or \
                      self.blocks[(y * self.length + z) * self.width + x - 1] == tt):
                    coord -= 1
                    x -= 1

                if x > 0 and self.blocks[(y * self.length + z) * self.width + x - 1] == sourceBlock:
                    sourceFlow = True

                lastNorth = False
                lastSouth = False
                lastBelow = False
                while x < self.width and self.__floodFillCounters[coord] != floodFillCounter and \
                     (self.blocks[(y * self.length + z) * self.width + x] == source or \
                      self.blocks[(y * self.length + z) * self.width + x] == tt):
                    if z > 0:
                        blockId = self.blocks[(y * self.length + z - 1) * self.width + x]
                        if blockId == sourceBlock:
                            sourceFlow = True

                        north = self.__floodFillCounters[coord - 1024] != floodFillCounter and \
                                (blockId == source or blockId == tt)
                        if north and not lastNorth:
                            self.__coords[flooded] = coord - 1024
                            flooded += 1

                        lastNorth = north

                    if z < self.length - 1:
                        blockId = self.blocks[(y * self.length + z + 1) * self.width + x]
                        if blockId == sourceBlock:
                            sourceFlow = True

                        south = self.__floodFillCounters[coord + 1024] != floodFillCounter and \
                                (blockId == source or blockId == tt)
                        if south and not lastSouth:
                            self.__coords[flooded] = coord + 1024
                            flooded += 1

                        lastSouth = south

                    if y < self.height - 1:
                        blockId = self.blocks[((y + 1) * self.length + z) * self.width + x]
                        below = blockId == source or blockId == tt
                        if below and not lastBelow:
                            self.__floodedBlocks[floodedBlocks] = coord
                            floodedBlocks += 1

                        lastBelow = below

                    xd = x - orgX
                    xd *= xd
                    xd += zd
                    if xd > lastDistance:
                        lastDistance = xd
                        pos = ((y << 10) + z << 10) + x

                    self.__floodFillCounters[coord] = floodFillCounter
                    coord += 1
                    x += 1

                if x < self.width and self.blocks[(y * self.length + z) * self.width + x] == sourceBlock:
                    sourceFlow = True

            if floodedBlocks <= 0:
                break

        if sourceFlow:
            return -9999
        else:
            return pos

    cdef int floodFill(self, int x, int y, int z, int source, int tt):
        cdef int i, flooded, coord
        cdef bint lastNorth, lastSouth, north, south
        cdef char blockId

        if x < 0 or y < 0 or z < 0 or x >= self.width or y >= self.height or z >= self.length:
            return 0

        global floodFillCounter
        floodFillCounter += 1
        if floodFillCounter == 30000:
            for i in range(1048576):
                self.__floodFillCounters[i] = 0

            floodFillCounter = 1

        flooded = 1
        self.__coords[0] = x + (z << 10)
        while True:
            while True:
                if flooded <= 0:
                    return 1

                flooded -= 1
                coord = self.__coords[flooded]
                if self.__floodFillCounters[coord] != floodFillCounter:
                    break

            x = coord % 1024
            z = coord // 1024
            if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1 or \
               z == 0 or z == self.length - 1:
                return 2

            while x > 0 and self.__floodFillCounters[coord - 1] != floodFillCounter and \
                  (self.blocks[(y * self.length + z) * self.width + x - 1] == source or \
                   self.blocks[(y * self.length + z) * self.width + x - 1] == tt):
                x -= 1
                coord -= 1

            if x > 0 and self.blocks[(y * self.length + z) * self.width + x - 1] == 0:
                return 0

            lastNorth = False
            lastSouth = False
            while x < self.width and self.__floodFillCounters[coord] != floodFillCounter and \
                 (self.blocks[(y * self.length + z) * self.width + x] == source or \
                  self.blocks[(y * self.length + z) * self.width + x] == tt):
                if x == 0 or x == self.width - 1:
                    return 2

                if z > 0:
                    blockId = self.blocks[(y * self.length + z - 1) * self.width + x]
                    if blockId == 0:
                        return 0

                    north = self.__floodFillCounters[coord - 1024] != floodFillCounter and \
                            (blockId == source or blockId == tt)
                    if north and not lastNorth:
                        self.__coords[flooded] = coord - 1024
                        flooded += 1

                    lastNorth = north

                if z < self.length - 1:
                    blockId = self.blocks[(y * self.length + z + 1) * self.width + x]
                    if blockId == 0:
                        return 0

                    south = self.__floodFillCounters[coord + 1024] != floodFillCounter and \
                            (blockId == source or blockId == tt)
                    if south and not lastSouth:
                        self.__coords[flooded] = coord + 1024
                        flooded += 1

                    lastSouth = south

                self.__floodFillCounters[coord] = floodFillCounter
                coord += 1
                x += 1

            if x < self.width and self.blocks[(y * self.length + z) * self.width + x] == 0:
                break

        return 0

    def playSoundAtEntity(self, entity, str name, float volume, float pitch):
        cdef float d, xd, yd, zd
        cdef RenderGlobal worldAccess
        for worldAccess in self.worldAccesses:
            d = 16.0
            if volume > 1.0:
                d = 16.0 * volume

            if self.playerEntity.getDistanceSqToEntity(entity) < d * d:
                worldAccess.playSound(
                    name, entity.posX, entity.posY - entity.yOffset,
                    entity.posZ, volume, pitch
                )

    def playMusic(self, float x, float y, float z, str name, float _):
        cdef RenderGlobal worldAccess

        try:
            for worldAccess in self.worldAccesses:
                worldAccess.playMusic(name, x, y, z, 0.0)
        except Exception as e:
            print(e)

    def playSoundAtPlayer(self, float x, float y, float z, str name,
                          float volume, float pitch):
        cdef float d, xd, yd, zd
        cdef RenderGlobal worldAccess

        try:
            for worldAccess in self.worldAccesses:
                d = 16.0
                if volume > 1.0:
                    d = 16.0 * volume

                xd = x - self.playerEntity.posX
                yd = y - self.playerEntity.posY
                zd = z - self.playerEntity.posZ
                if xd * xd + yd * yd + zd * zd < d * d:
                    worldAccess.playSound(name, x, y, z, volume, pitch)
        except Exception as e:
            print(e)

    def extinguishFire(self, int x, int y, int z, int sideHit):
        if sideHit == 0:
            y -= 1
        elif sideHit == 1:
            y += 1
        elif sideHit == 2:
            z -= 1
        elif sideHit == 3:
            z += 1
        elif sideHit == 4:
            x -= 1
        elif sideHit == 5:
            x += 1

        if self.getBlockId(x, y, z) == blocks.fire.blockID:
            self.playSoundAtPlayer(
                x + 0.5, y + 0.5, z + 0.5, 'random.fizz', 0.5,
                2.6 + (self.rand.nextFloat() - self.rand.nextFloat()) * 0.8
            )
            self.setBlockWithNotify(x, y, z, 0)

    def setBlockTileEntity(self, int x, int y, int z, entity):
        entity.worldObj = self
        entity.xCoord = x
        entity.yCoord = y
        entity.zCoord = z
        self.map[x + (y << 10) + (z << 10 << 10)] = entity
        self.__list.append(entity)

    def removeBlockTileEntity(self, int x, int y, int z):
        if x + (y << 10) + (z << 10 << 10) in self.map:
            self.__list.remove(self.map.pop(x + (y << 10) + (z << 10 << 10)))

    def getBlockTileEntity(self, int x, int y, int z):
        cdef int coord = x + (y << 10) + (z << 10 << 10)
        tileEntity = self.map.get(coord)
        if not tileEntity:
            blocks.blocksList[self.getBlockId(x, y, z)].onBlockAdded(self, x, y, z)
            tileEntity = self.map.get(coord)

        return tileEntity

    def spawnParticle(self, str particle, float x, float y, float z,
                      float xr, float yr, float zr):
        cdef RenderGlobal worldAccess
        for worldAccess in self.worldAccesses:
            worldAccess.spawnParticle(particle, x, y, z, xr, yr, zr)

    def randomDisplayUpdates(self, int xo, int yo, int zo):
        cdef int i, x, y, z, blockId
        for i in range(1000):
            x = xo + self.rand.nextInt(16) - self.rand.nextInt(16)
            y = yo + self.rand.nextInt(16) - self.rand.nextInt(16)
            z = zo + self.rand.nextInt(16) - self.rand.nextInt(16)
            blockId = self.getBlockId(x, y, z)
            if blockId > 0:
                blocks.blocksList[blockId].randomDisplayTick(self, x, y, z, self.__rand)

    def getBlocks(self):
        cdef int i
        blocks = bytearray(self.blocksSize)
        for i in range(self.blocksSize):
            blocks[i] = self.blocks[i]

        return blocks

    def getData(self):
        cdef int i
        data = bytearray(self.blocksSize)
        for i in range(self.blocksSize):
            data[i] = self.data[i]

        return data

    def debugSkylightUpdates(self):
        return str(len(self.__tickList)) + '. L: ' + \
               str(self.__lightUpdates.debugLightUpdates())

    def setLevel(self):
        cdef int i
        cdef RenderGlobal worldAccess
        for i in range(len(self.worldAccesses)):
            worldAccess = self.worldAccesses[i]
            for entity in self.entityMap.all:
                worldAccess.releaseEntitySkin(self.entityMap.all[i])

    cdef __updateChunkLight(self, int lightSubtracted):
        self.__lightUpdates.updateDaylightCycle(lightSubtracted)

    def canBlockSeeTheSky(self, int x, int y, int z):
        if self.heightMap[x + z * self.width] <= y:
            return True

        while y < self.height:
            if blocks.opaqueCubeLookup[self.getBlockId(x, y, z)]:
                return False

            y += 1

        return True
