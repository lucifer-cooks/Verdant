from mc.net.minecraft.game.level.block.Block import Block

class BlockBreakable(Block):

    def __init__(self, blocks, blockId, tex, material, localFlag):
        super().__init__(blocks, blockId, tex, material)
        self.__localFlag = localFlag

    def isOpaqueCube(self):
        return False

    def shouldSideBeRendered(self, world, x, y, z, layer):
        block = world.getBlockId(x, y, z)
        if not self.__localFlag and block == self.blockID:
            return False
        else:
            return super().shouldSideBeRendered(world, x, y, z, layer)
