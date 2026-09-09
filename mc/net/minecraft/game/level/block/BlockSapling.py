from mc.net.minecraft.game.level.block.BlockFlower import BlockFlower

class BlockSapling(BlockFlower):

    def __init__(self, blocks, blockId, tex):
        super().__init__(blocks, 6, 15)
        self._setBlockBounds(10.0 * 0.01, 0.0, 10.0 * 0.01, 0.9, 0.8, 0.9)

    def updateTick(self, world, x, y, z, random):
        super().updateTick(world, x, y, z, random)
        if world.getBlockLightValue(x, y + 1, z) >= 9 and random.nextInt(5) == 0:
            metadata = world.getBlockMetadata(x, y, z)
            if metadata < 15:
                world.setBlockMetadata(x, y, z, metadata + 1)
                return

            world.setTileNoUpdate(x, y, z, 0)
            if not world.growTrees(x, y, z):
                world.setTileNoUpdate(x, y, z, self.blockID)
