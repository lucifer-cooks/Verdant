from mc.net.minecraft.client.render.entity.Render import Render
from pyglet import gl

import math

class RenderLiving(Render):

    def __init__(self, model, shadowSize):
        super().__init__()
        self._mainModel = model
        self._shadowSize = shadowSize
        self.__renderPassModel = None

    def setRenderPassModel(self, model):
        self.__renderPassModel = model

    def renderLiving(self, entity, xd, yd, zd, yaw, a):
        gl.glPushMatrix()
        gl.glDisable(gl.GL_CULL_FACE)
        try:
            renderYaw = entity.prevRenderYawOffset + \
                        (entity.renderYawOffset - entity.prevRenderYawOffset) * a
            rotationYaw = entity.prevRotationYaw + \
                          (entity.rotationYaw - entity.prevRotationYaw) * a
            rotationPitch = entity.prevRotationPitch + \
                            (entity.rotationPitch - entity.prevRotationPitch) * a
            gl.glTranslatef(xd, yd, zd)
            z = entity.ticksExisted + a
            gl.glRotatef(180.0 - renderYaw, 0.0, 1.0, 0.0)
            if entity.deathTime > 0:
                fall = (entity.deathTime + a - 1.0) / 20.0 * 1.6
                fall = min(math.sqrt(fall), 1.0)
                gl.glRotatef(fall * self._getDeathMaxRotation(entity), 0.0, 0.0, 1.0)

            gl.glScalef(-(1.0 / 16.0), -(1.0 / 16.0), 1.0 / 16.0)
            self._preRenderCallback(entity, a)
            gl.glTranslatef(0.0, -24.0, 0.0)
            gl.glEnable(gl.GL_NORMALIZE)
            y = entity.prevLimbYaw + (entity.limbYaw - entity.prevLimbYaw) * a
            x = entity.limbSwing - entity.limbYaw * (1.0 - a)
            y = min(y, 1.0)
            self._loadDownloadableImageTexture(entity.skinUrl, entity.getTexture())
            gl.glEnable(gl.GL_ALPHA_TEST)
            self._mainModel.render(x, y, z, rotationYaw - renderYaw,
                                   rotationPitch, 1.0)
            for i in range(4):
                if self._shouldRenderPass(entity, i):
                    self.__renderPassModel.render(x, y, z, rotationYaw - renderYaw,
                                                  rotationPitch, 1.0)
                    gl.glDisable(gl.GL_BLEND)
                    gl.glEnable(gl.GL_ALPHA_TEST)

            br = entity.getBrightness(a)
            color = self._getColorMultiplier(entity, br, a)
            if ((color % 0x100000000) >> 24) > 0 or entity.hurtTime > 0 or \
               entity.deathTime > 0:
                gl.glDisable(gl.GL_TEXTURE_2D)
                gl.glDisable(gl.GL_ALPHA_TEST)
                gl.glEnable(gl.GL_BLEND)
                gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
                gl.glDepthFunc(gl.GL_EQUAL)
                if entity.hurtTime > 0 or entity.deathTime > 0:
                    gl.glColor4f(br, 0.0, 0.0, 0.4)
                    self._mainModel.render(x, y, z, rotationYaw - renderYaw,
                                           rotationPitch, 1.0)
                    for i in range(4):
                        if self._shouldRenderPass(entity, i):
                            gl.glColor4f(br, 0.0, 0.0, 0.4)
                            self.__renderPassModel.render(
                                x, y, z, rotationYaw - renderYaw, rotationPitch, 1.0
                            )

                if ((color % 0x100000000) >> 24) > 0:
                    r = (color >> 16 & 255) / 255.0
                    g = (color >> 8 & 255) / 255.0
                    b = (color & 255) / 255.0
                    a = ((color % 0x100000000) >> 24) / 255.0
                    gl.glColor4f(r, g, b, a)
                    self._mainModel.render(x, y, z, rotationYaw - renderYaw,
                                           rotationPitch, 1.0)
                    for i in range(4):
                        if self._shouldRenderPass(entity, i):
                            gl.glColor4f(r, g, b, a)
                            self.__renderPassModel.render(
                                x, y, z, rotationYaw - renderYaw, rotationPitch, 1.0
                            )

                gl.glDepthFunc(gl.GL_LEQUAL)
                gl.glDisable(gl.GL_BLEND)
                gl.glEnable(gl.GL_ALPHA_TEST)
                gl.glEnable(gl.GL_TEXTURE_2D)

            gl.glDisable(gl.GL_NORMALIZE)
        except Exception as e:
            print(str(e))

        gl.glEnable(gl.GL_CULL_FACE)
        gl.glPopMatrix()

    def _shouldRenderPass(self, entity, i):
        return False

    def _getDeathMaxRotation(self, entity):
        return 90.0

    def _getColorMultiplier(self, entity, br, a):
        return 0

    def _preRenderCallback(self, entity, a):
        pass

    def doRender(self, entity, xd, yd, zd, yaw, a):
        self.renderLiving(entity, xd, yd, zd, yaw, a)
