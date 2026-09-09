from mc.net.minecraft.client.render.entity.RenderLiving import RenderLiving

class RenderSheep(RenderLiving):

    def __init__(self, model, fur, shadowSize):
        super().__init__(model, 0.7)
        self.setRenderPassModel(fur)

    def _shouldRenderPass(self, sheep, i):
        self._loadTexture('mob/sheep_fur.png')
        return i == 0 and not sheep.sheared
