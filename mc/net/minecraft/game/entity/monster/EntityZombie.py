from mc.net.minecraft.game.entity.monster.EntityMob import EntityMob
from mc.net.minecraft.game.item.Items import items

class EntityZombie(EntityMob):

    def __init__(self, world):
        super().__init__(world)
        self._texture = 'mob/zombie.png'
        self._moveSpeed = 0.5
        self._attackStrength = 5

    def onLivingUpdate(self):
        if self._worldObj.skylightSubtracted > 7:
            br = self.getBrightness(1.0)
            if br > 0.5 and self._worldObj.canBlockSeeTheSky(int(self.posX),
                                                             int(self.posY),
                                                             int(self.posZ)) and \
               self._rand.nextFloat() * 30.0 < (br - 0.4) * 2.0:
                self.fire = 300

        super().onLivingUpdate()

    def _getEntityString(self):
        return 'Zombie'

    def _getDropItemId(self):
        return items.feather.shiftedIndex
