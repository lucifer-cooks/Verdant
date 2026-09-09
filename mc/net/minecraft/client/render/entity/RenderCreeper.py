from mc.net.minecraft.client.render.entity.RenderLiving import RenderLiving
from mc.net.minecraft.client.model.ModelCreeper import ModelCreeper
from pyglet import gl

import math

class RenderCreeper(RenderLiving):

    def __init__(self):
        super().__init__(ModelCreeper(), 0.5)

    def _preRenderCallback(self, creeper, a):
        fuse = creeper.getCreeperState(a)
        scaled = 1.0 + math.sin(fuse * 100.0) * fuse * 0.01
        fuse = min(max(fuse, 0.0), 1.0)
        fuse *= fuse
        fuse *= fuse
        scale = (1.0 + fuse * 0.4) * scaled
        y = (1.0 + fuse * 0.1) / scaled
        gl.glScalef(scale, y, scale)

    def _getColorMultiplier(self, creeper, br, a):
        fuse = creeper.getCreeperState(a)
        if int(fuse * 10.0) % 2 == 0:
            return 0
        else:
            color = int(fuse * 0.2 * 255.0)
            color = min(max(color, 0), 255)
            return color << 24 | 16711680 | 0xFF00 | 255
