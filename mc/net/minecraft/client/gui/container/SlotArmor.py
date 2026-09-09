from mc.net.minecraft.client.gui.container.Slot import Slot
from mc.net.minecraft.game.item.ItemArmor import ItemArmor

class SlotArmor(Slot):

    def __init__(self, inventory, guiHandler, guiInventory, slotIndex, xPos, yPos, armorType):
        super().__init__(guiHandler, guiInventory, slotIndex, 8, yPos)
        self.__armorType = armorType

    def isItemValid(self, stack):
        if isinstance(stack.getItem(), ItemArmor):
            return stack.getItem().armorType == self.__armorType
        else:
            return False

    def getBackgroundIconIndex(self):
        return 15 + (self.__armorType << 4)
