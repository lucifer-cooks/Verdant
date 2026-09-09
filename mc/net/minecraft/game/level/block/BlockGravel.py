from mc.net.minecraft.game.level.block.BlockSand import BlockSand

class BlockGravel(BlockSand):

    def __init__(self, blocks, blockId, tex):
        super().__init__(blocks, 13, 19)

    def idDropped(self, metadata, random):
        from mc.net.minecraft.game.item.Items import items
        return items.flint.shiftedIndex if random.nextInt(10) == 0 else self.blockID
