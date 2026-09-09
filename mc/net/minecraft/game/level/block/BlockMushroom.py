from mc.net.minecraft.game.level.block.BlockFlower import BlockFlower

class BlockMushroom(BlockFlower):

    def __init__(self, blocks, blockId, tex):
        super().__init__(blocks, blockId, tex)
        self._setBlockBounds(0.3, 0.0, 0.3, 0.7, 0.4, 0.7)

    def _canThisPlantGrowOnThisBlockID(self, blockId):
        return self.blocks.opaqueCubeLookup[blockId]

    def canBlockStay(self, world, x, y, z):
        if world.getBlockLightValue(x, y, z) <= 13:
            below = world.getBlockId(x, y - 1, z)
            if self.blocks.opaqueCubeLookup[below]:
                return True

        return False
