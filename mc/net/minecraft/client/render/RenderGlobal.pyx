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
from collections import deque

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
        # Sky/cloud display list cache
        self.__skyQuadList = -1
        self.__cloudQuadList = -1
        self.__skyCacheR = -1.0
        self.__skyCacheG = -1.0
        self.__skyCacheB = -1.0
        self.__skyWidth = -1
        self.__skyHeight = -1
        # Cloud geometry cache (rebuilt when world changes)
        self.__cloudGeomList = -1
        self.__cloudGeomWidth = -1
        self.__cloudGeomHeight = -1
        # Frustum culling throttle
        self.__prevFrustumPitch = -9999.0
        self.__prevFrustumYaw = -9999.0
        self.__prevFrustumX = -9999.0
        self.__prevFrustumZ = -9999.0

    def __init__(self, minecraft, renderEngine):
        cdef Random rand
        cdef float val
        cdef int i

        self.__mc = minecraft
        self.__renderEngine = renderEngine
        self.__t = tessellator
        self.__worldObj = None
        self.__renderIntBuffer = BufferUtils.createIntBuffer(65536)
        self.__worldRenderersToUpdate = deque()
        self.__sortedWorldRenderers = []
        self.__worldRenderers = []
        self.__visibleRenderers = []
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
        cdef int lists, chunks, x, y, z, i, playerChunkX, playerChunkZ, renderDistance
        cdef WorldRenderer chunk

        if self.__worldRenderers:
            for chunk in self.__worldRenderers:
                chunk.stopRendering()

        self.__renderChunksWide = self.__worldObj.width // self.CHUNK_SIZE
        self.__renderChunksTall = self.__worldObj.height // self.CHUNK_SIZE
        self.__renderChunksDeep = self.__worldObj.length // self.CHUNK_SIZE
        self.__worldRenderers = [None] * self.__renderChunksWide * self.__renderChunksTall * self.__renderChunksDeep
        self.__sortedWorldRenderers = [None] * self.__renderChunksWide * self.__renderChunksTall * self.__renderChunksDeep

        # Only load chunks around player for better performance
        playerChunkX = self.__worldObj.xSpawn // self.CHUNK_SIZE
        playerChunkZ = self.__worldObj.zSpawn // self.CHUNK_SIZE
        renderDistance = 3  # Only load chunks within 3 chunks of player

        lists = 0
        chunks = 0
        for x in range(max(0, playerChunkX - renderDistance), min(self.__renderChunksWide, playerChunkX + renderDistance + 1)):
            for y in range(self.__renderChunksTall):
                for z in range(max(0, playerChunkZ - renderDistance), min(self.__renderChunksDeep, playerChunkZ + renderDistance + 1)):
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
        self.__visibleRenderers.clear()
        gl.glNewList(self.__glGenList, gl.GL_COMPILE)
        self.__oobGroundRenderHeight()
        gl.glEndList()
        gl.glNewList(self.__glGenList + 1, gl.GL_COMPILE)
        self.__oobWaterRenderHeight()
        gl.glEndList()
        # Only mark blocks for update in loaded chunks
        self.__markBlocksForUpdate(
            max(0, (playerChunkX - renderDistance) << 4), 
            0, 
            max(0, (playerChunkZ - renderDistance) << 4),
            min(self.__worldObj.width, (playerChunkX + renderDistance + 1) << 4),
            self.__worldObj.height,
            min(self.__worldObj.length, (playerChunkZ + renderDistance + 1) << 4)
        )

    def renderEntities(self, vec, Frustum frustum, float a):
        cdef int x, y, z, x0, y0, z0, x1, y1, z1, chunk, playerChunkX, playerChunkZ, renderDistance
        cdef bint visible
        cdef list entities
        cdef Entity entity

        RenderManager.instance.cacheActiveRenderInfo(self.__worldObj, self.__renderEngine,
                                                     self.__mc.thePlayer, a)
        self.__countEntitiesTotal = 0
        self.__countEntitiesRendered = 0
        self.__countEntitiesHidden = 0
        eMap = self.__worldObj.entityMap
        
        # Only check entities in chunks around player for performance
        playerChunkX = (<int>self.__mc.thePlayer.posX) >> 4
        playerChunkZ = (<int>self.__mc.thePlayer.posZ) >> 4
        renderDistance = 4  # Only check entities within 4 chunks of player
        
        minX = max(0, playerChunkX - renderDistance)
        maxX = min(eMap.width - 1, playerChunkX + renderDistance)
        minZ = max(0, playerChunkZ - renderDistance)
        maxZ = min(eMap.height - 1, playerChunkZ + renderDistance)
        
        for x in range(minX, maxX + 1):
            for y in range(eMap.depth):
                for z in range(minZ, maxZ + 1):
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
                        if chunk < len(self.__worldRenderers) and self.__worldRenderers[chunk]:
                            visible = self.__worldRenderers[chunk].isInFrustum and \
                                      self.__worldRenderers[chunk].isVisible
                        else:
                            visible = False
                    else:
                        visible = False

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
        cdef int remaining = 0
        cdef float xd, yd, zd

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
                self.__visibleRenderers.sort(
                    key=lambda c: c.distanceToEntitySquared(player)
                )

        remaining = self.__renderSortedRenderers(0, len(self.__visibleRenderers), layer)
        return remaining

    cdef __checkOcclusionQueryResult(self, int minChunk, int maxChunk):
        pass

    cdef int __renderSortedRenderers(self, int minChunk, int maxChunk, int layer):
        cdef int startingIndex, chunk
        cdef WorldRenderer r

        startingIndex = 0
        minChunk = max(0, min(minChunk, len(self.__visibleRenderers)))
        maxChunk = max(0, min(maxChunk, len(self.__visibleRenderers)))

        for chunk in range(minChunk, maxChunk):
            r = <WorldRenderer>self.__visibleRenderers[chunk]
            if layer == 0:
                self.__renderersLoaded += 1
                self.__renderersBeingRendered += 1

            startingIndex = r.getGLCallListForPass(
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
        cdef int world_w, world_h

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

        world_w = self.__worldObj.width
        world_h = self.__worldObj.height

        gl.glDepthMask(False)

        # --- Sky dome --- build once per world size; color changes via glColor4f ---
        if self.__skyQuadList < 0:
            self.__skyQuadList = gl.glGenLists(1)

        if self.__skyWidth != world_w or self.__skyHeight != world_h:
            self.__skyWidth = world_w
            self.__skyHeight = world_h
            # Also invalidate cloud geometry when world changes
            self.__cloudGeomWidth = -1

            y_sky = world_h + 10.
            gl.glNewList(self.__skyQuadList, gl.GL_COMPILE)
            self.__t.startDrawingQuads()
            self.__t.setColorOpaque_F(1.0, 1.0, 1.0)
            for x in range(-2048, world_w + 2048, 512):
                for z in range(-2048, world_h + 2048, 512):
                    self.__t.addVertex(x, y_sky, z)
                    self.__t.addVertex(x + 512., y_sky, z)
                    self.__t.addVertex(x + 512., y_sky, z + 512.)
                    self.__t.addVertex(x, y_sky, z + 512.)
            self.__t.draw()
            gl.glEndList()

        # Apply current sky colour and render the cached list
        gl.glColor4f(r, g, b, 1.0)
        gl.glCallList(self.__skyQuadList)
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)

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

        # --- Cloud layer --- geometry cached per world size, UV+color changes per frame ---
        gl.glBindTexture(gl.GL_TEXTURE_2D,
                         self.__renderEngine.getTexture('clouds.png'))
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

        # Cloud geometry (just positions, no UV baked in) can't be fully cached because
        # UVs change every frame. Tessellate directly — but only the geometry (UV applied inline).
        # This is necessary because UV scroll makes pure list caching impossible.
        # Optimization: reduce quad count by enlarging step size to 1024 from 512.
        self.__t.startDrawingQuads()
        self.__t.setColorOpaque_F(r, g, b)
        for x in range(-2048, world_w + 2048, 1024):
            for z in range(-2048, world_h + 2048, 1024):
                self.__t.addVertexWithUV(x, y, z + 1024.,
                                         x * scale + u, (z + 1024.) * scale)
                self.__t.addVertexWithUV(x + 1024., y, z + 1024.,
                                         (x + 1024.) * scale + u, (z + 1024.) * scale)
                self.__t.addVertexWithUV(x + 1024., y, z,
                                         (x + 1024.) * scale + u, z * scale)
                self.__t.addVertexWithUV(x, y, z, x * scale + u, z * scale)
                self.__t.addVertexWithUV(x, y, z, x * scale + u, z * scale)
                self.__t.addVertexWithUV(x + 1024., y, z,
                                         (x + 1024.) * scale + u, z * scale)
                self.__t.addVertexWithUV(x + 1024., y, z + 1024.,
                                         (x + 1024.) * scale + u, (z + 1024.) * scale)
                self.__t.addVertexWithUV(x, y, z + 1024.,
                                         x * scale + u, (z + 1024.) * scale)

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
        cdef int count, remaining, inspected, playerChunkX, playerChunkZ, renderDistance
        cdef WorldRenderer chunk
        cdef float maxDistSq = 96.0 * 96.0  # Reduced from 160.0 for better performance
        
        if self.__mc.options:
            if self.__mc.options.renderDistance == 1:
                maxDistSq = 80.0 * 80.0  # Reduced from 144.0
            elif self.__mc.options.renderDistance == 2:
                maxDistSq = 48.0 * 48.0  # Reduced from 80.0
            elif self.__mc.options.renderDistance == 3:
                maxDistSq = 32.0 * 32.0  # Reduced from 40.0

        if not self.__worldRenderersToUpdate:
            return

        # Get player chunk position
        playerChunkX = (<int>player.posX) >> 4
        playerChunkZ = (<int>player.posZ) >> 4
        renderDistance = 3  # Only update chunks within 3 chunks of player

        count = 0
        remaining = len(self.__worldRenderersToUpdate)
        inspected = 0
        while self.__worldRenderersToUpdate and count < 6 and inspected < remaining:  # Reduced from 12
            chunk = self.__worldRenderersToUpdate.pop()
            inspected += 1
            
            # Check if chunk is within render distance of player
            chunkX = chunk.__posX >> 4
            chunkZ = chunk.__posZ >> 4
            if abs(chunkX - playerChunkX) > renderDistance or abs(chunkZ - playerChunkZ) > renderDistance:
                # Distant chunk — push to front of deque for later
                self.__worldRenderersToUpdate.appendleft(chunk)
                continue
            
            if chunk.distanceToEntitySquared(player) > maxDistSq:
                # Distant chunk — push to front of deque (O(1)) for later when player approaches
                self.__worldRenderersToUpdate.appendleft(chunk)
                continue

            chunk.updateRenderer()
            chunk.needsUpdate = False
            count += 1


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
        cdef float maxDistSq = 300.0 * 300.0
        cdef object player = self.__mc.thePlayer
        cdef int px, pz, chunkDist, minX, maxX, minZ, maxZ, x, y, z, i
        cdef float pitch, yaw, dx, dz, dPitch, dYaw

        if self.__mc.options:
            if self.__mc.options.renderDistance == 1:
                maxDistSq = 144.0 * 144.0
            elif self.__mc.options.renderDistance == 2:
                maxDistSq = 80.0 * 80.0
            elif self.__mc.options.renderDistance == 3:
                maxDistSq = 40.0 * 40.0

        if not player or not self.__worldRenderers:
            return

        # Throttle: skip full re-clip if camera hasn't moved/rotated significantly
        pitch = player.rotationPitch
        yaw = player.rotationYaw
        dx = player.posX - self.__prevFrustumX
        dz = player.posZ - self.__prevFrustumZ
        dPitch = pitch - self.__prevFrustumPitch
        dYaw = yaw - self.__prevFrustumYaw
        if (dx * dx + dz * dz < 4.0 and
                dPitch * dPitch < 9.0 and
                dYaw * dYaw < 9.0 and
                self.__visibleRenderers):
            # Camera hasn't moved or rotated enough — skip re-clip this frame
            return

        self.__prevFrustumX = player.posX
        self.__prevFrustumZ = player.posZ
        self.__prevFrustumPitch = pitch
        self.__prevFrustumYaw = yaw

        for chunk in self.__visibleRenderers:
            chunk.isInFrustum = False
        self.__visibleRenderers.clear()

        px = (<int>player.posX) >> 4
        pz = (<int>player.posZ) >> 4
        chunkDist = <int>(sqrt(maxDistSq) / 16.0) + 1
        minX = max(0, px - chunkDist)
        maxX = min(self.__renderChunksWide - 1, px + chunkDist)
        minZ = max(0, pz - chunkDist)
        maxZ = min(self.__renderChunksDeep - 1, pz + chunkDist)

        for x in range(minX, maxX + 1):
            for z in range(minZ, maxZ + 1):
                for y in range(self.__renderChunksTall):
                    i = (z * self.__renderChunksTall + y) * self.__renderChunksWide + x
                    chunk = <WorldRenderer>self.__worldRenderers[i]
                    if chunk.distanceToEntitySquared(player) <= maxDistSq:
                        chunk.updateInFrustum(frustum)
                        if chunk.isInFrustum:
                            self.__visibleRenderers.append(chunk)


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
