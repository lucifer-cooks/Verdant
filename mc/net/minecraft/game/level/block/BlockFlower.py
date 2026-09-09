from mc.net.minecraft.game.level.block.Block import Block
from mc.net.minecraft.game.level.material.Material import Material

class BlockFlower(Block):

    def __init__(self, blocks, blockId, tex):
        super().__init__(blocks, blockId, tex, Material.plants)
        self.blockIndexInTexture = tex
        self._setTickOnLoad(True)
        self._setBlockBounds(0.3, 0.0, 0.3, 0.7, 0.6, 0.7)

    def canPlaceBlockAt(self, world, x, y, z):
        return self._canThisPlantGrowOnThisBlockID(world.getBlockId(x, y - 1, z))

    def _canThisPlantGrowOnThisBlockID(self, blockId):
        return blockId == self.blocks.grass.blockID or \
               blockId == self.blocks.dirt.blockID or \
               blockId == self.blocks.tilledField.blockID

    def onNeighborBlockChange(self, world, x, y, z, blockType):
        super().onNeighborBlockChange(world, x, y, z, blockType)
        self.__checkFlowerChange(world, x, y, z)

    def updateTick(self, world, x, y, z, random):
        self.__checkFlowerChange(world, x, y, z)

    def __checkFlowerChange(self, world, x, y, z):
        if not self.canBlockStay(world, x, y, z):
            self.dropBlockAsItem(world, x, y, z, world.getBlockMetadata(x, y, z))
            world.setBlockWithNotify(x, y, z, 0)

    def canBlockStay(self, world, x, y, z):
        return (world.getBlockLightValue(x, y, z) >= 8 or \
                world.getBlockLightValue(x, y, z) >= 4 and \
                world.canBlockSeeTheSky(x, y, z)) and \
               self._canThisPlantGrowOnThisBlockID(world.getBlockId(x, y - 1, z))

    def getCollisionBoundingBoxFromPool(self, x, y, z):
        return None

    def isOpaqueCube(self):
        return False

    def renderAsNormalBlock(self):
        return False

    def getRenderType(self):
        return 1
