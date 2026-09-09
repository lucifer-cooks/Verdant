from mc.net.minecraft.client.render.entity.RenderLiving import RenderLiving
from mc.net.minecraft.client.model.ModelSpider import ModelSpider
from pyglet import gl

class RenderSpider(RenderLiving):

    def __init__(self):
        super().__init__(ModelSpider(), 1.0)
        self.setRenderPassModel(ModelSpider())

    def _getDeathMaxRotation(self, entity):
        return 180.0

    def _shouldRenderPass(self, entity, i):
        if i != 0:
            return False

        self._loadTexture('mob/spider_eyes.png')
        a = (1.0 - entity.getBrightness(1.0)) * 0.5
        gl.glEnable(gl.GL_BLEND)
        gl.glDisable(gl.GL_ALPHA_TEST)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glColor4f(1.0, 1.0, 1.0, a)
        return True
