# cython: language_level=3

cimport cython

from libc.math cimport sqrt, sin

from mc.net.minecraft.game.level.World cimport World
from mc.net.minecraft.game.level.block.Blocks import blocks
from mc.net.minecraft.game.level.block.Block cimport Block
from mc.net.minecraft.game.entity.Entity cimport Entity
from mc.net.minecraft.game.entity.player.EntityPlayer import EntityPlayer
from mc.net.minecraft.client.effect.EntityBubbleFX import EntityBubbleFX
from mc.net.minecraft.client.effect.EntityExplodeFX import EntityExplodeFX
from mc.net.minecraft.client.effect.EntitySplashFX import EntitySplashFX
from mc.net.minecraft.client.effect.EntitySmokeFX import EntitySmokeFX
from mc.net.minecraft.client.effect.EntityFlameFX import EntityFlameFX
from mc.net.minecraft.client.effect.EntityLavaFX import EntityLavaFX
from mc.net.minecraft.client.render.camera.Frustum cimport Frustum
from mc.net.minecraft.client.render.EntitySorter import EntitySorter
from mc.net.minecraft.client.render.Tessellator import tessellator
from mc.net.minecraft.client.render.WorldRenderer cimport WorldRenderer
from mc.net.minecraft.client.render.RenderSorter import RenderSorter
from mc.net.minecraft.client.render.RenderBlocks cimport RenderBlocks
from mc.net.minecraft.client.render.ImageBufferDownload import ImageBufferDownload
from mc.net.minecraft.client.render.entity.RenderManager import RenderManager
from mc.JavaUtils import BufferUtils
from mc.JavaUtils cimport Random, getMillis
from pyglet import gl
from functools import cmp_to_key

@cython.final
cdef class RenderGlobal:
    CHUNK_SIZE = 16

    def __cinit__(self):
        self.__countEntitiesTotal = 0
        self.__countEntitiesRendered = 0
        self.__countEntitiesHidden = 0
        self.__renderersLoaded = 0
        self.__renderersBeingClipped = 0
        self.__renderersBeingOccluded = 0
        self.__renderersBeingRendered = 0
        self.__cloudOffsetX = 0

    def __init__(self, minecraft, renderEngine):
        cdef Random rand
        cdef float val
        cdef int i

        self.__mc = minecraft
        self.__renderEngine = renderEngine
        self.__t = tessellator
        self.__worldObj = None
        self.__renderIntBuffer = BufferUtils.createIntBuffer(65536)
        self.__worldRenderersToUpdate = []
        self.__sortedWorldRenderers = []
        self.__worldRenderers = []
        self.__globalRenderBlocks = None
        RenderManager.instance = RenderManager()
        self.__prevSortX = -9999.0
        self.__prevSortY = -9999.0
        self.__prevSortZ = -9999.0
        self.damagePartialTime = 0.0
        self.__glGenList = gl.glGenLists(2)
        self.__glRenderListBase = gl.glGenLists(786432)
        self.__occlusionResult = BufferUtils.createIntBuffer(64)
        self.__occlusionEnabled = gl.gl_info.have_extension('GL_ARB_occlusion_query')
        if self.__occlusionEnabled:
            self.__occlusionResult.clear()
            self.__occlusionResult.glGetInteger(gl.GL_QUERY_COUNTER_BITS)
            if self.__occlusionResult.getAt(0) == 0:
                self.__occlusionEnabled = False
            else:
                self.__glOcclusionQueryBase = BufferUtils.createIntBuffer(262144)
                self.__glOcclusionQueryBase.clear()
                self.__glOcclusionQueryBase.position(0)
                self.__glOcclusionQueryBase.limit(262144)
                self.__glOcclusionQueryBase.glGenQueriesARB()

        self.__glSkyList = gl.glGenLists(1)
        gl.glNewList(self.__glSkyList, gl.GL_COMPILE)

        rand = Random(10842)
        for i in range(500):
            gl.glRotatef(rand.nextFloat() * 360.0, 1.0, 0.0, 0.0)
            gl.glRotatef(rand.nextFloat() * 360.0, 0.0, 1.0, 0.0)
            gl.glRotatef(rand.nextFloat() * 360.0, 0.0, 0.0, 1.0)
            t = tessellator
            val = 0.25 + rand.nextFloat() * 0.25
            t.startDrawingQuads()
            t.addVertexWithUV(-val, -100.0, val, 1.0, 1.0)
            t.addVertexWithUV(val, -100.0, val, 0.0, 1.0)
            t.addVertexWithUV(val, -100.0, -val, 0.0, 0.0)
            t.addVertexWithUV(-val, -100.0, -val, 1.0, 0.0)
            t.draw()

        gl.glEndList()

    def changeWorld(self, World world):
        if self.__worldObj:
            self.__worldObj.removeWorldAccess(self)

        self.__prevSortX = -9999.0
        self.__prevSortY = -9999.0
        self.__prevSortZ = -9999.0
        RenderManager.instance.set(world)
        self.__worldObj = world
        self.__globalRenderBlocks = RenderBlocks(world)
        if world:
            world.addWorldAccess(self)
            self.loadRenderers()

    def loadRenderers(self):
        cdef int lists, chunks, x, y, z, i
        cdef WorldRenderer chunk

        if self.__worldRenderers:
            for chunk in self.__worldRenderers:
                chunk.stopRendering()

        self.__renderChunksWide = self.__worldObj.width // self.CHUNK_SIZE
        self.__renderChunksTall = self.__worldObj.height // self.CHUNK_SIZE
        self.__renderChunksDeep = self.__worldObj.length // self.CHUNK_SIZE
        self.__worldRenderers = [None] * self.__renderChunksWide * self.__renderChunksTall * self.__renderChunksDeep
        self.__sortedWorldRenderers = [None] * self.__renderChunksWide * self.__renderChunksTall * self.__renderChunksDeep

        lists = 0
        chunks = 0
        for x in range(self.__renderChunksWide):
            for y in range(self.__renderChunksTall):
                for z in range(self.__renderChunksDeep):
                    i = (z * self.__renderChunksTall + y) * self.__renderChunksWide + x
                    self.__worldRenderers[i] = WorldRenderer(self.__worldObj, x << 4, y << 4,
                                                             z << 4, RenderGlobal.CHUNK_SIZE,
                                                             self.__glRenderListBase + lists)
                    if self.__occlusionEnabled:
                        self.__worldRenderers[i].glOcclusionQuery = self.__glOcclusionQueryBase.getAt(chunks)

                    chunks += 1
                    self.__sortedWorldRenderers[i] = self.__worldRenderers[i]
                    lists += 3

        for chunk in self.__worldRenderersToUpdate:
            chunk.needsUpdate = False

        self.__worldRenderersToUpdate.clear()
        gl.glNewList(self.__glGenList, gl.GL_COMPILE)
        self.__oobGroundRenderHeight()
        gl.glEndList()
        gl.glNewList(self.__glGenList + 1, gl.GL_COMPILE)
        self.__oobWaterRenderHeight()
        gl.glEndList()
        self.__markBlocksForUpdate(
            0, 0, 0, self.__worldObj.width, self.__worldObj.height,
            self.__worldObj.length
        )

    def renderEntities(self, vec, Frustum frustum, float a):
        cdef int x, y, z, x0, y0, z0, x1, y1, z1, chunk
        cdef bint visible
        cdef list entities
        cdef Entity entity

        RenderManager.instance.cacheActiveRenderInfo(self.__worldObj, self.__renderEngine,
                                                     self.__mc.thePlayer, a)
        self.__countEntitiesTotal = 0
        self.__countEntitiesRendered = 0
        self.__countEntitiesHidden = 0
        eMap = self.__worldObj.entityMap
        for x in range(eMap.width):
            for y in range(eMap.depth):
                for z in range(eMap.height):
                    entities = eMap.entityGrid[(z * eMap.depth + y) * eMap.width + x]
                    if not entities:
                        continue

                    x0 = (x << 3) + 4
                    y0 = (y << 3) + 4
                    z0 = (z << 3) + 4
                    self.__countEntitiesTotal += len(entities)
                    if x0 >= 0 and y0 >= 0 and z0 >= 0 and \
                       x0 < self.__worldObj.width and y0 < self.__worldObj.height and \
                       z0 < self.__worldObj.length:
                        x1 = x0 // 16
                        y1 = y0 // 16
                        z1 = z0 // 16
                        chunk = (z1 * self.__renderChunksTall + y1) * self.__renderChunksWide + x1
                        visible = self.__worldRenderers[chunk].isInFrustum and \
                                  self.__worldRenderers[chunk].isVisible
                    else:
                        visible = True

                    if visible:
                        for entity in entities:
                            if entity.shouldRender(vec) and \
                               frustum.isVisible(entity.boundingBox) and \
                               (entity != self.__worldObj.playerEntity or \
                                self.__mc.options.thirdPersonView):
                                    self.__countEntitiesRendered += 1
                                    RenderManager.instance.renderEntity(entity, a)
                    else:
                        self.__countEntitiesHidden += len(entities)

    def getDebugInfoRenders(self):
        return f'C: {self.__renderersBeingRendered} / {self.__renderersLoaded}' \
               f'. F: {self.__renderersBeingClipped}, O: {self.__renderersBeingOccluded}'

    def getDebugInfoEntities(self):
        return f'E: {self.__countEntitiesRendered} / {self.__countEntitiesTotal}' \
               f'. B: {self.__countEntitiesHidden}, I: ' + \
               str(self.__countEntitiesTotal - self.__countEntitiesHidden - self.__countEntitiesRendered)

    def sortAndRender(self, player, int layer):
        cdef int chunk, minChunk, maxChunk, queryRate
        cdef float xd, yd, zd, d

        if layer == 0:
            self.__renderersLoaded = 0
            self.__renderersBeingClipped = 0
            self.__renderersBeingOccluded = 0
            self.__renderersBeingRendered = 0

        xd = player.posX - self.__prevSortX
        yd = player.posY - self.__prevSortY
        zd = player.posZ - self.__prevSortZ
        if xd * xd + yd * yd + zd * zd > 16.0:
            self.__prevSortX = player.posX
            self.__prevSortY = player.posY
            self.__prevSortZ = player.posZ
            self.__sortedWorldRenderers = sorted(
                self.__sortedWorldRenderers,
                key=cmp_to_key(EntitySorter(player).compare)
            )

        if self.__occlusionEnabled and layer == 0:
            maxChunk = 8
            self.__checkOcclusionQueryResult(0, 8)

            for chunk in range(8):
                self.__sortedWorldRenderers[chunk].isVisible = True

            remaining = 0 + self.__renderSortedRenderers(0, 8, layer)
            while True:
                minChunk = maxChunk
                maxChunk <<= 1
                maxChunk = min(maxChunk, len(self.__sortedWorldRenderers))

                gl.glDisable(gl.GL_TEXTURE_2D)
                gl.glDisable(gl.GL_LIGHTING)
                gl.glDisable(gl.GL_ALPHA_TEST)
                gl.glColorMask(False, False, False, False)
                gl.glDepthMask(False)
                self.__checkOcclusionQueryResult(minChunk, maxChunk)

                for chunk in range(minChunk, maxChunk):
                    if not self.__sortedWorldRenderers[chunk].isInFrustum:
                        self.__sortedWorldRenderers[chunk].isVisible = True

                    if self.__sortedWorldRenderers[chunk].isInFrustum and not \
                       self.__sortedWorldRenderers[chunk].isWaitingOnOcclusionQuery:
                        d = sqrt(self.__sortedWorldRenderers[chunk].distanceToEntitySquared(player))
                        queryRate = <int>(1.0 + d / 64.0)
                        if self.__cloudOffsetX % queryRate == chunk % queryRate:
                            gl.glBeginQueryARB(
                                gl.GL_SAMPLES_PASSED,
                                self.__sortedWorldRenderers[chunk].glOcclusionQuery
                            )
                            self.__sortedWorldRenderers[chunk].callOcclusionQueryList()
                            gl.glEndQueryARB(gl.GL_SAMPLES_PASSED)
                            self.__sortedWorldRenderers[chunk].isWaitingOnOcclusionQuery = True

                gl.glColorMask(True, True, True, True)
                gl.glDepthMask(True)
                gl.glEnable(gl.GL_TEXTURE_2D)
                gl.glEnable(gl.GL_ALPHA_TEST)
                remaining += self.__renderSortedRenderers(minChunk, maxChunk, layer)
                if maxChunk >= len(self.__sortedWorldRenderers):
                    break
        else:
            remaining = 0 + self.__renderSortedRenderers(
                0, len(self.__sortedWorldRenderers), layer
            )

        return remaining

    cdef __checkOcclusionQueryResult(self, int minChunk, int maxChunk):
        cdef int chunk
        for chunk in range(minChunk, maxChunk):
            if self.__sortedWorldRenderers[chunk].isWaitingOnOcclusionQuery:
                self.__occlusionResult.clear()
                self.__occlusionResult.glGetQueryObjectivARB(
                    self.__sortedWorldRenderers[chunk].glOcclusionQuery,
                    gl.GL_QUERY_RESULT_AVAILABLE
                )
                if self.__occlusionResult.getAt(0) != 0:
                    self.__sortedWorldRenderers[chunk].isWaitingOnOcclusionQuery = False
                    self.__occlusionResult.clear()
                    self.__occlusionResult.glGetQueryObjectivARB(
                        self.__sortedWorldRenderers[chunk].glOcclusionQuery,
                        gl.GL_QUERY_RESULT
                    )
                    self.__sortedWorldRenderers[chunk].isVisible = self.__occlusionResult.getAt(0) != 0

    cdef int __renderSortedRenderers(self, int minChunk, int maxChunk, int layer):
        cdef int startingIndex, chunk

        startingIndex = 0
        for chunk in range(minChunk, maxChunk):
            if layer == 0:
                self.__renderersLoaded += 1
                if not self.__sortedWorldRenderers[chunk].isInFrustum:
                    self.__renderersBeingClipped += 1
                if self.__sortedWorldRenderers[chunk].isInFrustum and not \
                   self.__sortedWorldRenderers[chunk].isVisible:
                    self.__renderersBeingOccluded ++ 1
                if self.__sortedWorldRenderers[chunk].isInFrustum and \
                   self.__sortedWorldRenderers[chunk].isVisible:
                    self.__renderersBeingRendered += 1

            if self.__sortedWorldRenderers[chunk].isInFrustum and \
               self.__sortedWorldRenderers[chunk].isVisible:
                startingIndex = (<WorldRenderer>self.__sortedWorldRenderers[chunk]).getGLCallListForPass(
                    self.__chunkBuffer, startingIndex, layer
                )

        self.__renderIntBuffer.clear()
        self.__renderIntBuffer.putInts(self.__chunkBuffer, 0, startingIndex)
        self.__renderIntBuffer.flip()
        if self.__renderIntBuffer.remaining() > 0:
            self.__renderIntBuffer.glCallLists()

        return self.__renderIntBuffer.remaining()

    def renderAllRenderLists(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.__renderEngine.getTexture('terrain.png'))
        self.__renderIntBuffer.glCallLists()

    def updateClouds(self):
        self.__cloudOffsetX += 1

    def renderSky(self, float partialTicks):
        cdef int x, z
        cdef float r, g, b, nr, y, xd, yd, zd, br, scale, u

        gl.glDisable(gl.GL_TEXTURE_2D)
        skyColor = self.__worldObj.getSkyColor(partialTicks)
        r = skyColor.xCoord
        g = skyColor.yCoord
        b = skyColor.zCoord
        if self.__mc.options.anaglyph:
            nr = (r * 30.0 + g * 59.0 + b * 11.0) / 100.0
            g = (r * 30.0 + g * 70.0) / 100.0
            b = (r * 30.0 + b * 70.0) / 100.0
            r = nr

        gl.glDepthMask(False)
        self.__t.startDrawingQuads()
        self.__t.setColorOpaque_F(r, g, b)
        y = self.__worldObj.height + 10.
        for x in range(-2048, self.__worldObj.width + 2048, 512):
            for z in range(-2048, self.__worldObj.height + 2048, 512):
                self.__t.addVertex(x, y, z)
                self.__t.addVertex(x + 512., y, z)
                self.__t.addVertex(x + 512., y, z + 512.)
                self.__t.addVertex(x, y, z + 512.)

        self.__t.draw()
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glDisable(gl.GL_FOG)
        gl.glDisable(gl.GL_ALPHA_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_ONE, gl.GL_ONE)
        gl.glPushMatrix()
        xd = self.__worldObj.playerEntity.lastTickPosX + \
             (self.__worldObj.playerEntity.posX - \
              self.__worldObj.playerEntity.lastTickPosX) * partialTicks
        yd = self.__worldObj.playerEntity.lastTickPosY + \
             (self.__worldObj.playerEntity.posY - \
              self.__worldObj.playerEntity.lastTickPosY) * partialTicks
        zd = self.__worldObj.playerEntity.lastTickPosZ + \
             (self.__worldObj.playerEntity.posZ - \
              self.__worldObj.playerEntity.lastTickPosZ) * partialTicks
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)
        gl.glTranslatef(xd, yd, zd)
        gl.glRotatef(0.0, 0.0, 0.0, 1.0)
        gl.glRotatef(self.__worldObj.getCelestialAngle(partialTicks) * 360.0,
                     1.0, 0.0, 0.0)
        gl.glBindTexture(gl.GL_TEXTURE_2D,
                         self.__renderEngine.getTexture('terrain/sun.png'))
        self.__t.startDrawingQuads()
        self.__t.addVertexWithUV(-30.0, 100.0, -30.0, 0.0, 0.0)
        self.__t.addVertexWithUV(30.0, 100.0, -30.0, 1.0, 0.0)
        self.__t.addVertexWithUV(30.0, 100.0, 30.0, 1.0, 1.0)
        self.__t.addVertexWithUV(-30.0, 100.0, 30.0, 0.0, 1.0)
        self.__t.draw()
        gl.glBindTexture(gl.GL_TEXTURE_2D,
                         self.__renderEngine.getTexture('terrain/moon.png'))
        self.__t.startDrawingQuads()
        self.__t.addVertexWithUV(-20.0, -100.0, 20.0, 1.0, 1.0)
        self.__t.addVertexWithUV(20.0, -100.0, 20.0, 0.0, 1.0)
        self.__t.addVertexWithUV(20.0, -100.0, -20.0, 0.0, 0.0)
        self.__t.addVertexWithUV(-20.0, -100.0, -20.0, 1.0, 0.0)
        self.__t.draw()
        gl.glDisable(gl.GL_TEXTURE_2D)
        br = self.__worldObj.getStarBrightness(partialTicks)
        gl.glColor4f(br, br, br, br)
        gl.glCallList(self.__glSkyList)
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glDisable(gl.GL_BLEND)
        gl.glEnable(gl.GL_ALPHA_TEST)
        gl.glEnable(gl.GL_FOG)
        gl.glPopMatrix()
        gl.glDepthMask(True)
        gl.glBindTexture(gl.GL_TEXTURE_2D,
                         self.__renderEngine.getTexture('clouds.png'))
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)
        cloudColor = self.__worldObj.getCloudColor(partialTicks)
        r = cloudColor.xCoord
        g = cloudColor.yCoord
        b = cloudColor.zCoord
        if self.__mc.options.anaglyph:
            nr = (r * 30.0 + g * 59.0 + b * 11.0) / 100.0
            g = (r * 30.0 + g * 70.0) / 100.0
            b = (r * 30.0 + b * 70.0) / 100.0
            r = nr

        y = self.__worldObj.cloudHeight
        scale = 0.5 / 1024
        u = (self.__cloudOffsetX + partialTicks) * scale * 0.03
        self.__t.startDrawingQuads()
        self.__t.setColorOpaque_F(r, g, b)
        for x in range(-2048, self.__worldObj.width + 2048, 512):
            for z in range(-2048, self.__worldObj.height + 2048, 512):
                self.__t.addVertexWithUV(x, y, z + 512.,
                                         x * scale + u, (z + 512.) * scale)
                self.__t.addVertexWithUV(x + 512., y, z + 512.,
                                         (x + 512.) * scale + u, (z + 512.) * scale)
                self.__t.addVertexWithUV(x + 512., y, z,
                                         (x + 512.) * scale + u, z * scale)
                self.__t.addVertexWithUV(x, y, z, x * scale + u, z * scale)
                self.__t.addVertexWithUV(x, y, z, x * scale + u, z * scale)
                self.__t.addVertexWithUV(x + 512., y, z,
                                         (x + 512.) * scale + u, z * scale)
                self.__t.addVertexWithUV(x + 512., y, z + 512.,
                                         (x + 512.) * scale + u, (z + 512.) * scale)
                self.__t.addVertexWithUV(x, y, z + 512.,
                                         x * scale + u, (z + 512.) * scale)

        self.__t.draw()

    def oobGroundRenderer(self):
        cdef float br = self.__worldObj.getBrightness(
            0, self.__worldObj.getGroundLevel(), 0
        )
        gl.glBindTexture(gl.GL_TEXTURE_2D,
                         self.__renderEngine.getTexture('dirt.png'))
        if self.__worldObj.getGroundLevel() > self.__worldObj.getWaterLevel() and \
           self.__worldObj.defaultFluid == blocks.waterMoving.blockID:
            gl.glBindTexture(gl.GL_TEXTURE_2D,
                             self.__renderEngine.getTexture('grass.png'))

        gl.glColor4f(br, br, br, 1.0)
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glCallList(self.__glGenList)

    cdef __oobGroundRenderHeight(self):
        cdef int s, d, x, z
        cdef float groundLevel

        groundLevel = self.__worldObj.getGroundLevel()
        s = min(min(128, self.__worldObj.width), self.__worldObj.length)
        d = 2048 // s
        self.__t.startDrawingQuads()
        for x in range(-s * d, self.__worldObj.width + s * d, s):
            for z in range(-s * d, self.__worldObj.length + s * d, s):
                if groundLevel < 0.0 or x < 0 or z < 0 or \
                   x >= self.__worldObj.width or z >= self.__worldObj.length:
                    self.__t.addVertexWithUV(x, groundLevel, z + s, 0.0, s)
                    self.__t.addVertexWithUV(x + s, groundLevel, z + s, s, s)
                    self.__t.addVertexWithUV(x + s, groundLevel, z, s, 0.0)
                    self.__t.addVertexWithUV(x, groundLevel, z, 0.0, 0.0)

        self.__t.draw()

    def oobWaterRenderer(self):
        cdef float br
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glEnable(gl.GL_BLEND)
        gl.glBindTexture(gl.GL_TEXTURE_2D,
                         self.__renderEngine.getTexture('water.png'))
        br = self.__worldObj.getBrightness(0, self.__worldObj.getWaterLevel(), 0)
        gl.glColor4f(br, br, br, 1.0)
        gl.glCallList(self.__glGenList + 1)
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)
        gl.glDisable(gl.GL_BLEND)

    cdef __oobWaterRenderHeight(self):
        cdef int x, z, s, d
        cdef float y, minX, minZ, waterLevel

        waterLevel = self.__worldObj.getWaterLevel()
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        s = min(min(128, self.__worldObj.width), self.__worldObj.length)
        d = 2048 // s
        self.__t.startDrawingQuads()
        minX = blocks.waterMoving.minX
        minZ = blocks.waterMoving.minZ

        for x in range(-s * d, self.__worldObj.width + s * d, s):
            for z in range(-s * d, self.__worldObj.length + s * d, s):
                y = waterLevel + blocks.waterMoving.minY
                if waterLevel < 0.0 or x < 0 or z < 0 or \
                   x >= self.__worldObj.width or z >= self.__worldObj.length:
                    self.__t.addVertexWithUV(x + minX, y, (z + s) + minZ, 0.0, s)
                    self.__t.addVertexWithUV((x + s) + minX, y, (z + s) + minZ, s, s)
                    self.__t.addVertexWithUV((x + s) + minX, y, z + minZ, s, 0.0)
                    self.__t.addVertexWithUV(x + minX, y, z + minZ, 0.0, 0.0)

                    self.__t.addVertexWithUV(x + minX, y, z + minZ, 0.0, 0.0)
                    self.__t.addVertexWithUV((x + s) + minX, y, z + minZ, s, 0.0)
                    self.__t.addVertexWithUV((x + s) + minX, y, (z + s) + minZ, s, s)
                    self.__t.addVertexWithUV(x + minX, y, (z + s) + minZ, 0.0, s)

        self.__t.draw()
        gl.glDisable(gl.GL_BLEND)

    def updateRenderers(self, player):
        cdef int last, i
        cdef WorldRenderer chunk

        self.__worldRenderersToUpdate = sorted(
            self.__worldRenderersToUpdate,
            key=cmp_to_key(RenderSorter(player).compare)
        )

        last = len(self.__worldRenderersToUpdate) - 1
        for i in range(last + 1):
            chunk = self.__worldRenderersToUpdate[last - i]
            if chunk.distanceToEntitySquared(player) > 2500.0 and i > 4:
                return

            self.__worldRenderersToUpdate.remove(chunk)
            chunk.updateRenderer()
            chunk.needsUpdate = False

    def drawBlockBreaking(self, h, int mode, item):
        cdef int id_, blockId
        cdef Block block

        gl.glEnable(gl.GL_BLEND)
        gl.glEnable(gl.GL_ALPHA_TEST)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)
        gl.glColor4f(1.0, 1.0, 1.0, (sin(getMillis() / 100.0) * 0.2 + 0.4) * 0.5)
        if self.damagePartialTime > 0.0:
            gl.glBlendFunc(gl.GL_DST_COLOR, gl.GL_SRC_COLOR)
            id_ = self.__renderEngine.getTexture('terrain.png')
            gl.glBindTexture(gl.GL_TEXTURE_2D, id_)
            gl.glColor4f(1.0, 1.0, 1.0, 0.5)
            gl.glPushMatrix()
            blockId = self.__worldObj.getBlockId(h.blockX, h.blockY, h.blockZ)
            block = blocks.blocksList[blockId] if blockId > 0 else None
            gl.glDisable(gl.GL_ALPHA_TEST)
            self.__t.startDrawingQuads()
            self.__t.disableColor()
            if not block:
                block = blocks.stone

            self.__globalRenderBlocks.renderBlockUsingTexture(
                block, h.blockX, h.blockY, h.blockZ,
                240 + <int>(self.damagePartialTime * 10.0)
            )
            self.__t.draw()
            gl.glEnable(gl.GL_ALPHA_TEST)
            gl.glDepthMask(True)
            gl.glPopMatrix()

        gl.glDisable(gl.GL_BLEND)
        gl.glDisable(gl.GL_ALPHA_TEST)

    def drawSelectionBox(self, h, int mode):
        cdef int block

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glColor4f(0.0, 0.0, 0.0, 0.4)
        gl.glLineWidth(2.0)
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glDepthMask(False)
        block = self.__worldObj.getBlockId(h.blockX, h.blockY, h.blockZ)
        if block > 0:
            blocks.blocksList[block].getSelectedBoundingBoxFromPool(
                self.__mc.objectMouseOver.blockX, self.__mc.objectMouseOver.blockY,
                self.__mc.objectMouseOver.blockZ
            ).expand(0.002, 0.002, 0.002).render()

        gl.glDepthMask(True)
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glDisable(gl.GL_BLEND)

    cdef __markBlocksForUpdate(self, int x0, int y0, int z0, int x1, int y1, int z1):
        cdef int x, y, z, i
        cdef WorldRenderer chunk

        x0 //= RenderGlobal.CHUNK_SIZE
        x1 //= RenderGlobal.CHUNK_SIZE
        y0 //= RenderGlobal.CHUNK_SIZE
        y1 //= RenderGlobal.CHUNK_SIZE
        z0 //= RenderGlobal.CHUNK_SIZE
        z1 //= RenderGlobal.CHUNK_SIZE

        if x0 < 0: x0 = 0
        if y0 < 0: y0 = 0
        if z0 < 0: z0 = 0
        if x1 >= self.__renderChunksWide: x1 = self.__renderChunksWide - 1
        if y1 >= self.__renderChunksTall: y1 = self.__renderChunksTall - 1
        if z1 >= self.__renderChunksDeep: z1 = self.__renderChunksDeep - 1

        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    i = (z * self.__renderChunksTall + y) * self.__renderChunksWide + x
                    chunk = self.__worldRenderers[i]
                    if not chunk.needsUpdate:
                        chunk.needsUpdate = True
                        self.__worldRenderersToUpdate.append(chunk)

    cdef markBlockAndNeighborsNeedsUpdate(self, int x, int y, int z):
        self.__markBlocksForUpdate(x - 1, y - 1, z - 1, x + 1, y + 1, z + 1)

    cdef markBlockRangeNeedsUpdate(self, int x0, int y0, int z0,
                                   int x1, int y1, int z1):
        self.__markBlocksForUpdate(x0 - 1, y0 - 1, z0 - 1, x1 + 1, y1 + 1, z1 + 1)

    def clipRenderersByFrustum(self, Frustum frustum):
        cdef WorldRenderer chunk
        for chunk in self.__worldRenderers:
            chunk.updateInFrustum(frustum)

    def playSound(self, str sound, float x, float y, float z,
                  float volume, float pitch):
        self.__mc.sndManager.playSound(sound, x, y, z, volume, pitch)

    def spawnParticle(self, str particle, float x, float y, float z,
                      float xr, float yr, float zr):
        cdef float xd = self.__worldObj.playerEntity.posX - x
        cdef float yd = self.__worldObj.playerEntity.posY - y
        cdef float zd = self.__worldObj.playerEntity.posZ - z
        if xd * xd + yd * yd + zd * zd > 256.0:
            return

        if particle == 'bubble':
            self.__mc.effectRenderer.addEffect(
                EntityBubbleFX(self.__worldObj, x, y, z, xr, yr, zr)
            )
        elif particle == 'smoke':
            self.__mc.effectRenderer.addEffect(
                EntitySmokeFX(self.__worldObj, x, y, z)
            )
        elif particle == 'explode':
            self.__mc.effectRenderer.addEffect(
                EntityExplodeFX(self.__worldObj, x, y, z, xr, yr, zr)
            )
        elif particle == 'flame':
            self.__mc.effectRenderer.addEffect(
                EntityFlameFX(self.__worldObj, x, y, z)
            )
        elif particle == 'lava':
            self.__mc.effectRenderer.addEffect(
                EntityLavaFX(self.__worldObj, x, y, z)
            )
        elif particle == 'splash':
            self.__mc.effectRenderer.addEffect(
                EntitySplashFX(self.__worldObj, x, y, z)
            )
        elif particle == 'largesmoke':
            self.__mc.effectRenderer.addEffect(
                EntitySmokeFX(self.__worldObj, x, y, z, 2.5)
            )

    def playMusic(self, str music, float x, float y, float z, float _):
        self.__mc.sndManager.playRandomMusicIfReady(x, y, z)

    def obtainEntitySkin(self, entity):
        if entity.skinUrl:
            self.__renderEngine.obtainImageData(entity.skinUrl, ImageBufferDownload())

    def releaseEntitySkin(self, entity):
        if entity.skinUrl:
            self.__renderEngine.releaseImageData(entity.skinUrl)

    cdef updateAllRenderers(self):
        gl.glNewList(self.__glGenList, gl.GL_COMPILE)
        self.__oobGroundRenderHeight()
        gl.glEndList()
        gl.glNewList(self.__glGenList + 1, gl.GL_COMPILE)
        self.__oobWaterRenderHeight()
        gl.glEndList()
