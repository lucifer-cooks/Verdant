from mc.net.minecraft.game.level.block.BlockBreakable import BlockBreakable

class BlockGlass(BlockBreakable):

    def __init__(self, blocks, blockId, tex, material, localFlag):
        super().__init__(blocks, 20, 49, material, False)

    def quantityDropped(self, random):
        return 0
