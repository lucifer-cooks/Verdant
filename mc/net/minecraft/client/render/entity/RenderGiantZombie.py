from mc.net.minecraft.client.render.entity.RenderLiving import RenderLiving
from pyglet import gl

class RenderGiantZombie(RenderLiving):

    def __init__(self, model, shadowSize, scale):
        super().__init__(model, 3.0)
        self.__scale = 6.0

    def _preRenderCallback(self, entity, a):
        gl.glScalef(self.__scale, self.__scale, self.__scale)
