from mc.net.minecraft.game.entity.monster.EntityMob import EntityMob
from mc.net.minecraft.game.item.Items import items

import math

class EntitySpider(EntityMob):

    def __init__(self, world):
        super().__init__(world)
        self._texture = 'mob/spider.png'
        self.setSize(1.4, 0.9)
        self._moveSpeed = 0.8

    def _findPlayerToAttack(self):
        br = self.getBrightness(1.0)
        if br < 0.5:
            d = self._worldObj.playerEntity.getDistanceSqToEntity(self)
            if d < 256.0:
                return self._worldObj.playerEntity

        return None

    def _attackEntity(self, entity, distance):
        br = self.getBrightness(1.0)
        if br > 0.5 and self._rand.nextInt(100) == 0:
            self._playerToAttack = None
        elif distance > 2.0 and distance < 6.0 and self._rand.nextInt(10) == 0:
            if self.onGround:
                xd = entity.posX - self.posX
                zd = entity.posZ - self.posZ
                d = math.sqrt(xd * xd + zd * zd)
                self.motionX = xd / d * 0.5 * 0.8 + self.motionX * 0.2
                self.motionZ = zd / d * 0.5 * 0.8 + self.motionZ * 0.2
                self.motionY = 0.4
                return
        else:
            super()._attackEntity(entity, distance)

    def _writeEntityToNBT(self, compound):
        super()._writeEntityToNBT(compound)

    def _readEntityFromNBT(self, compound):
        super()._readEntityFromNBT(compound)

    def _getEntityString(self):
        return 'Spider'

    def _getDropItemId(self):
        return items.silk.shiftedIndex
