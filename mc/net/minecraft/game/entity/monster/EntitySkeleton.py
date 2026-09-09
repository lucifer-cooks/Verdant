from mc.net.minecraft.game.entity.monster.EntityMob import EntityMob
from mc.net.minecraft.game.entity.projectile.EntityArrow import EntityArrow
from mc.net.minecraft.game.item.Items import items

import math

class EntitySkeleton(EntityMob):

    def __init__(self, world):
        super().__init__(world)
        self._texture = 'mob/skeleton.png'

    def onLivingUpdate(self):
        if self._worldObj.skylightSubtracted > 7:
            br = self.getBrightness(1.0)
            if br > 0.5 and self._worldObj.canBlockSeeTheSky(int(self.posX),
                                                             int(self.posY),
                                                             int(self.posZ)) and \
               self._rand.nextFloat() * 30.0 < (br - 0.4) * 2.0:
                self.fire = 300

        super().onLivingUpdate()

    def _attackEntity(self, entity, distance):
        if distance >= 10.0:
            return

        xd = entity.posX - self.posX
        zd = entity.posZ - self.posZ
        if self.attackTime == 0:
            arrow = EntityArrow(self._worldObj, self)
            arrow.posY += 1
            yd = entity.posY - 0.2 - arrow.posY
            d = math.sqrt(xd * xd + zd * zd) * 0.2
            self._worldObj.playSoundAtEntity(
                self, 'random.bow', 1.0, 1.0 / (self._rand.nextFloat() * 0.4 + 0.8)
            )
            self._worldObj.spawnEntityInWorld(arrow)
            arrow.setArrowHeading(xd, yd + d, zd, 0.6, 12.0)
            self.attackTime = 30

        self.rotationYaw = (math.atan2(zd, xd) * 180.0 / math.pi) - 90.0
        self._hasAttacked = True

    def _writeEntityToNBT(self, compound):
        super()._writeEntityToNBT(compound)

    def _readEntityFromNBT(self, compound):
        super()._readEntityFromNBT(compound)

    def _getEntityString(self):
        return 'Skeleton'

    def _getDropItemId(self):
        return items.arrow.shiftedIndex
