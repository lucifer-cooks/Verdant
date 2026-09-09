from mc.net.minecraft.game.level.block.Blocks import blocks
from mc.net.minecraft.game.item.Item import Item

class ItemSeeds(Item):

    def __init__(self, items, itemId, blockType):
        super().__init__(items, 39)
        self.__blockType = blockType

    def onItemUse(self, stack, world, x, y, z, sideHit):
        if sideHit != 1:
            return False
        elif x <= 0 or y <= 0 or z <= 0 or x >= world.width - 1 or \
           y >= world.height - 1 or z >= world.length - 1:
            return False

        blockId = world.getBlockId(x, y, z)
        if blockId == blocks.tilledField.blockID:
            world.setBlockWithNotify(x, y + 1, z, self.__blockType)
            stack.stackSize -= 1
            return True
        else:
            return False
