from mc.net.minecraft.game.entity.monster.EntityMob import EntityMob
from mc.net.minecraft.game.item.Items import items

class EntityCreeper(EntityMob):

    def __init__(self, world):
        super().__init__(world)
        self._texture = 'mob/creeper.png'
        self.__timeSinceIgnited = 0
        self.__lastActiveTime = 0
        self.__fuseTime = 30
        self.__creeperState = -1

    def _writeEntityToNBT(self, compound):
        super()._writeEntityToNBT(compound)

    def _readEntityFromNBT(self, compound):
        super()._readEntityFromNBT(compound)

    def _getEntityString(self):
        return 'Creeper'

    def _updatePlayerActionState(self):
        self.__lastActiveTime = self.__timeSinceIgnited
        if self.__timeSinceIgnited > 0 and self.__creeperState < 0:
            self.__timeSinceIgnited -= 1

        if self.__creeperState >= 0:
            self.__creeperState = 2

        super()._updatePlayerActionState()
        if self.__creeperState != 1:
            self.__creeperState = -1

    def _attackEntity(self, entity, distance):
        if self.__creeperState <= 0 and distance < 3.0 or \
           self.__creeperState > 0 and distance < 7.0:
            if self.__timeSinceIgnited == 0:
                self._worldObj.playSoundAtEntity(self, 'random.fuse', 1.0, 0.5)

            self.__creeperState = 1
            self.__timeSinceIgnited += 1
            if self.__timeSinceIgnited == self.__fuseTime:
                self._worldObj.createExplosion(self, self.posX, self.posY, self.posZ, 3.0)
                self.setEntityDead()

            self._hasAttacked = True

    def getCreeperState(self, a):
        return (self.__lastActiveTime + (self.__timeSinceIgnited - self.__lastActiveTime) * a) / (self.__fuseTime - 2)

    def _getDropItemId(self):
        return items.gunpowder.shiftedIndex
