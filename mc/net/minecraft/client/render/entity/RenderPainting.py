from mc.net.minecraft.client.render.Tessellator import tessellator
from mc.net.minecraft.client.render.entity.Render import Render
from mc.JavaUtils import Random
from pyglet import gl

class RenderPainting(Render):

    def __init__(self):
        super().__init__()
        self.__random = Random()

    def doRender(self, entity, xd, yd, zd, yaw, a):
        self.__random.setSeed(187)
        gl.glPushMatrix()
        gl.glTranslatef(xd, yd, zd)
        gl.glRotatef(yaw, 0.0, 1.0, 0.0)
        gl.glEnable(gl.GL_NORMALIZE)
        self._loadTexture('art/kz.png')
        gl.glScalef(1.0 / 16.0, 1.0 / 16.0, 1.0 / 16.0)
        offsetY = entity.art.offsetY
        offsetX = entity.art.offsetX
        sizeY = entity.art.sizeY
        sizeX = entity.art.sizeX
        halfX = -sizeX / 2.0
        halfY = -sizeY / 2.0
        for x in range(0, sizeX // 16):
            for y in range(0, sizeY // 16):
                x1 = halfX + (x + 1 << 4)
                x0 = halfX + (x << 4)
                y1 = halfY + (y + 1 << 4)
                y0 = halfY + (y << 4)
                xPos = (x1 + x0) / 2.0
                yPos = (y1 + y0) / 2.0
                posX = int(entity.posX)
                posY = int(entity.posY + yPos / 16.0)
                posZ = int(entity.posZ)
                if entity.direction == 0:
                    posX = int(entity.posX + xPos / 16.0)
                if entity.direction == 1:
                    posZ = int(entity.posZ - xPos / 16.0)
                if entity.direction == 2:
                    posX = int(entity.posX - xPos / 16.0)
                if entity.direction == 3:
                    posZ = int(entity.posZ + xPos / 16.0)

                br = self._renderManager.worldObj.getBrightness(posX, posY, posZ)
                gl.glColor3f(br, br, br)
                u1 = (offsetX + sizeX - (x << 4)) / 256.0
                u0 = (offsetX + sizeX - (x + 1 << 4)) / 256.0
                v1 = (offsetY + sizeY - (y << 4)) / 256.0
                v0 = (offsetY + sizeY - (y + 1 << 4)) / 256.0
                t = tessellator
                t.startDrawingQuads()
                t.setNormal(0.0, 0.0, -1.0)
                t.addVertexWithUV(x1, y0, -0.5, u0, v1)
                t.addVertexWithUV(x0, y0, -0.5, u1, v1)
                t.addVertexWithUV(x0, y1, -0.5, u1, v0)
                t.addVertexWithUV(x1, y1, -0.5, u0, v0)
                t.setNormal(0.0, 0.0, 1.0)
                t.addVertexWithUV(x1, y1, 0.5, 12.0 / 16.0, 0.0)
                t.addVertexWithUV(x0, y1, 0.5, 13.0 / 16.0, 0.0)
                t.addVertexWithUV(x0, y0, 0.5, 13.0 / 16.0, 1.0 / 16.0)
                t.addVertexWithUV(x1, y0, 0.5, 12.0 / 16.0, 1.0 / 16.0)
                t.setNormal(0.0, -1.0, 0.0)
                t.addVertexWithUV(x1, y1, -0.5, 12.0 / 16.0, 0.001953125)
                t.addVertexWithUV(x0, y1, -0.5, 13.0 / 16.0, 0.001953125)
                t.addVertexWithUV(x0, y1, 0.5, 13.0 / 16.0, 0.001953125)
                t.addVertexWithUV(x1, y1, 0.5, 12.0 / 16.0, 0.001953125)
                t.setNormal(0.0, 1.0, 0.0)
                t.addVertexWithUV(x1, y0, 0.5, 12.0 / 16.0, 0.001953125)
                t.addVertexWithUV(x0, y0, 0.5, 13.0 / 16.0, 0.001953125)
                t.addVertexWithUV(x0, y0, -0.5, 13.0 / 16.0, 0.001953125)
                t.addVertexWithUV(x1, y0, -0.5, 12.0 / 16.0, 0.001953125)
                t.setNormal(-1.0, 0.0, 0.0)
                t.addVertexWithUV(x1, y1, 0.5, 385.0 / 512.0, 0.0)
                t.addVertexWithUV(x1, y0, 0.5, 385.0 / 512.0, 1.0 / 16.0)
                t.addVertexWithUV(x1, y0, -0.5, 385.0 / 512.0, 1.0 / 16.0)
                t.addVertexWithUV(x1, y1, -0.5, 385.0 / 512.0, 0.0)
                t.setNormal(1.0, 0.0, 0.0)
                t.addVertexWithUV(x0, y1, -0.5, 385.0 / 512.0, 0.0)
                t.addVertexWithUV(x0, y0, -0.5, 385.0 / 512.0, 1.0 / 16.0)
                t.addVertexWithUV(x0, y0, 0.5, 385.0 / 512.0, 1.0 / 16.0)
                t.addVertexWithUV(x0, y1, 0.5, 385.0 / 512.0, 0.0)
                t.draw()

        gl.glDisable(gl.GL_NORMALIZE)
        gl.glPopMatrix()
