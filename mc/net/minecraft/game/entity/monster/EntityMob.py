from mc.net.minecraft.game.entity.EntityCreature import EntityCreature

class EntityMob(EntityCreature):

    def __init__(self, world):
        super().__init__(world)
        self.health = 20
        self._attackStrength = 2

    def onLivingUpdate(self):
        br = self.getBrightness(1.0)
        if br > 0.5:
            self._entityAge += 2

        super().onLivingUpdate()

    def onEntityUpdate(self):
        super().onEntityUpdate()
        if self._worldObj.difficultySetting == 0:
            self.setEntityDead()

    def _findPlayerToAttack(self):
        if self._worldObj.playerEntity.getDistanceSqToEntity(self) < 256.0:
            return self._worldObj.playerEntity
        else:
            return None

    def attackEntityFrom(self, entity, damage):
        if super().attackEntityFrom(entity, damage):
            if entity != self:
                self._playerToAttack = entity

            return True
        else:
            return False

    def _attackEntity(self, entity, distance):
        if distance < 2.5 and entity.boundingBox.maxY > self.boundingBox.minY and \
           entity.boundingBox.minY < self.boundingBox.maxY:
            self.attackTime = 20
            entity.attackEntityFrom(self, self._attackStrength)

    def _getBlockPathWeight(self, x, y, z):
        return 0.5 - self._worldObj.getBrightness(x, y, z)

    def _writeEntityToNBT(self, compound):
        super()._writeEntityToNBT(compound)

    def _readEntityFromNBT(self, compound):
        super()._readEntityFromNBT(compound)

    def _getEntityString(self):
        return 'Monster'

    def getCanSpawnHere(self, x, y, z):
        light = self._worldObj.getBlockLightValue(int(x), int(y), int(z))
        return light <= self._rand.nextInt(8) and super().getCanSpawnHere(x, y, z)
