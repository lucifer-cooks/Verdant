from mc.net.minecraft.game.level.block.Block import Block
from mc.net.minecraft.game.level.material.Material import Material

class BlockOre(Block):

    def __init__(self, blocks, blockId, tex):
        super().__init__(blocks, blockId, tex, Material.wood)

    def idDropped(self, metadata, random):
        from mc.net.minecraft.game.item.Items import items
        if self.blockID == self.blocks.oreCoal.blockID:
            return items.coal.shiftedIndex
        elif self.blockID == self.blocks.oreDiamond.blockID:
            return items.diamond.shiftedIndex
        else:
            return self.blockID

    def quantityDropped(self, random):
        return 1
