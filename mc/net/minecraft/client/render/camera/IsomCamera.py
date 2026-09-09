from mc.net.minecraft.client.render.camera.Frustum import Frustum

class IsomCamera(Frustum):

    def __init__(self):
        pass

    def isVisible(self, aabb):
        return True
