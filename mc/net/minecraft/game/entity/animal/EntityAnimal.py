from mc.net.minecraft.game.entity.EntityCreature import EntityCreature
from mc.net.minecraft.game.level.block.Blocks import blocks

class EntityAnimal(EntityCreature):

    def __init__(self, world):
        super().__init__(world)

    def _getBlockPathWeight(self, x, y, z):
        if self._worldObj.getBlockId(x, y - 1, z) == blocks.grass.blockID:
            return 10.0
        else:
            return self._worldObj.getBrightness(x, y, z) - 0.5

    def _writeEntityToNBT(self, compound):
        super()._writeEntityToNBT(compound)

    def _readEntityFromNBT(self, compound):
        super()._readEntityFromNBT(compound)

    def getCanSpawnHere(self, x, y, z):
        return self._worldObj.getBlockLightValue(int(x), int(y), int(z)) > 8 and \
               super().getCanSpawnHere(x, y, z)
