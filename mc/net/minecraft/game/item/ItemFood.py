from mc.net.minecraft.game.item.Item import Item

class ItemFood(Item):

    def __init__(self, items, itemId, healAmount):
        super().__init__(items, itemId)
        self.__healAmount = healAmount
        self._maxStackSize = 1

    def onItemRightClick(self, stack, world, player):
        stack.stackSize -= 1
        player.heal(self.__healAmount)
        return stack
