from mc.net.minecraft.client.effect.EntityFX import EntityFX
from mc.JavaUtils import random

class EntitySmokeFX(EntityFX):

    def __init__(self, world, x, y, z, scale=1.0):
        super().__init__(world, x, y, z, 0.0, 0.0, 0.0)
        self._motionX1 *= 0.1
        self._motionY1 *= 0.1
        self._motionZ1 *= 0.1
        self._particleRed = random() * 0.3
        self._particleGreen = self._particleRed
        self._particleBlue = self._particleRed
        self._particleScale *= 12.0 / 16.0
        self._particleScale *= scale
        self.__smokeParticleScale = self._particleScale
        self._particleMaxAge = int(8.0 / (random() * 0.8 + 0.2))
        self._particleMaxAge = int(self._particleMaxAge * scale)
        self.noClip = False

    def renderParticle(self, t, a, xa, ya, za, xa2, ya2):
        scale = (self._particleAge + a) / self._particleMaxAge * 32.0
        scale = min(max(scale, 0.0), 1.0)
        self._particleScale = self.__smokeParticleScale * scale
        super().renderParticle(t, a, xa, ya, za, xa2, ya2)

    def onEntityUpdate(self):
        self.prevPosX = self.posX
        self.prevPosY = self.posY
        self.prevPosZ = self.posZ
        self._particleAge += 1
        if self._particleAge - 1 >= self._particleMaxAge:
            self.setEntityDead()

        self._particleTextureIndex = int(7 - (self._particleAge << 3) / self._particleMaxAge)
        self._motionY1 = self._motionY1 + 0.004
        self.moveEntity(self._motionX1, self._motionY1, self._motionZ1)
        if self.posY == self.prevPosY:
            self._motionX1 *= 1.1
            self._motionZ1 *= 1.1

        self._motionX1 *= 0.96
        self._motionY1 *= 0.96
        self._motionZ1 *= 0.96
        if self.onGround:
            self._motionX1 *= 0.7
            self._motionZ1 *= 0.7
