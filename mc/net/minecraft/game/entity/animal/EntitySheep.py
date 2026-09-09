from mc.net.minecraft.game.entity.animal.EntityAnimal import EntityAnimal
from mc.net.minecraft.game.entity.EntityLiving import EntityLiving
from mc.net.minecraft.game.level.block.Blocks import blocks

from nbtlib.tag import Byte

class EntitySheep(EntityAnimal):

    def __init__(self, world):
        super().__init__(world)
        self.sheared = False
        self._texture = 'mob/sheep.png'
        self.setSize(0.9, 1.3)

    def attackEntityFrom(self, entity, damage):
        if not self.sheared and isinstance(entity, EntityLiving):
            self.sheared = True
            drops = 1 + self._rand.nextInt(3)
            for i in range(drops):
                drop = self.entityDropItem(
                    blocks.clothGray.blockID, 1, 1.0
                )
                drop.motionY += self._rand.nextFloat() * 0.05
                drop.motionX += (self._rand.nextFloat() - self._rand.nextFloat()) * 0.1
                drop.motionZ += (self._rand.nextFloat() - self._rand.nextFloat()) * 0.1

        return super().attackEntityFrom(entity, damage)

    def _writeEntityToNBT(self, compound):
        super()._writeEntityToNBT(compound)
        compound['Sheared'] = Byte(self.sheared)

    def _readEntityFromNBT(self, compound):
        super()._readEntityFromNBT(compound)
        self.sheared = bool(compound.get('Sheared', Byte(False)).real)

    def _getEntityString(self):
        return 'Sheep'

    def _getLivingSound(self):
        return 'mob.sheep'

    def _getHurtSound(self):
        return 'mob.sheep'

    def _getDeathSound(self):
        return 'mob.sheep'
