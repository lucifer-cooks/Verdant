from mc.net.minecraft.game.level.block.BlockLeavesBase import BlockLeavesBase
from mc.net.minecraft.game.level.material.Material import Material

class BlockLeaves(BlockLeavesBase):

    def __init__(self, blocks, blockId, tex):
        super().__init__(blocks, 18, 52, Material.leaves, True)
        self._setTickOnLoad(True)

    def updateTick(self, world, x, y, z, random):
        if world.getBlockMaterial(x, y - 1, z).isSolid():
            return

        for xx in range(x - 2, x + 3):
            for yy in range(y - 1, y + 1):
                for zz in range(z - 2, z + 3):
                    if world.getBlockId(xx, yy, zz) == self.blocks.wood.blockID:
                        return

        self.dropBlockAsItem(world, x, y, z, world.getBlockMetadata(x, y, z))
        world.setBlockWithNotify(x, y, z, 0)

    def quantityDropped(self, random):
        if random.nextInt(10) == 0:
            return 1
        else:
            return 0

    def idDropped(self, metadata, random):
        return self.blocks.sapling.blockID
