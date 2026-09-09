from mc.JavaUtils import Random

class Item:
    TOTAL_STACK_SIZE = 64
    MAX_DAMAGE = 32
    _rand = Random()

    def __init__(self, items, itemId):
        self.items = items
        self.shiftedIndex = itemId + 256
        if items.itemsList[itemId + 256]:
            print('CONFLICT @', itemId)

        items.itemsList[itemId + 256] = self
        self._maxStackSize = Item.TOTAL_STACK_SIZE
        self._maxDamage = Item.MAX_DAMAGE

    def setIconIndex(self, iconIndex):
        self._iconIndex = iconIndex
        return self

    def getIconIndex(self):
        return self._iconIndex

    def onItemUse(self, stack, world, x, y, z, sideHit):
        return False

    def getStrVsBlock(self, block):
        return 1.0

    def onItemRightClick(self, stack, world, player):
        return stack

    def getItemStackLimit(self):
        return self._maxStackSize

    def getMaxDamage(self):
        return self._maxDamage

    def hitEntity(self, stack):
        pass

    def onBlockDestroyed(self, stack):
        pass

    def getDamageVsEntity(self):
        return 1

    def canHarvestBlock(self, block):
        return False
