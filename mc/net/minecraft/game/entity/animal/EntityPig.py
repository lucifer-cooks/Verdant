from mc.net.minecraft.game.entity.animal.EntityAnimal import EntityAnimal
from mc.net.minecraft.game.item.Items import items

class EntityPig(EntityAnimal):

    def __init__(self, world):
        super().__init__(world)
        self._texture = 'mob/pig.png'
        self.setSize(0.9, 0.9)

    def _writeEntityToNBT(self, compound):
        super()._writeEntityToNBT(compound)

    def _readEntityFromNBT(self, compound):
        super()._readEntityFromNBT(compound)

    def _getEntityString(self):
        return 'Pig'

    def _getLivingSound(self):
        return 'mob.pig'

    def _getHurtSound(self):
        return 'mob.pig'

    def _getDeathSound(self):
        return 'mob.pigdeath'

    def _getDropItemId(self):
        return items.porkRaw.shiftedIndex
