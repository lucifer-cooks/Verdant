from mc.net.minecraft.game.level.block.tileentity.TileEntity import TileEntity
from mc.net.minecraft.game.item.ItemStack import ItemStack
from mc.net.minecraft.game.Inventory import Inventory

from nbtlib.tag import Compound, String, Byte, List

class TileEntityChest(TileEntity, Inventory):

    def __init__(self):
        self.__chestContents = [None] * 36

    def getSizeInventory(self):
        return 27

    def getStackInSlot(self, slot):
        return self.__chestContents[slot]

    def decrStackSize(self, slot, size):
        if not self.__chestContents[slot]:
            return None

        if self.__chestContents[slot].stackSize <= size:
            stack = self.__chestContents[slot]
            self.__chestContents[slot] = None
            return stack
        else:
            stack = self.__chestContents[slot].splitStack(size)
            if self.__chestContents[slot].stackSize == 0:
                self.__chestContents[slot] = None

            return stack

    def setInventorySlotContents(self, slot, stack):
        self.__chestContents[slot] = stack
        if stack:
            stack.stackSize = min(stack.stackSize, Inventory.STACK_LIMIT)

    def getInvName(self):
        return 'Chest'

    def readFromNBT(self, compound):
        tagList = compound.get('Items', List[Compound]())
        self.__chestContents = [None] * 27
        for tag in tagList:
            slot = tag.get('Slot', Byte(0)).real & 255
            if slot >= 0 and slot < len(self.__chestContents):
                self.__chestContents[slot] = ItemStack(tag)

    def writeToNBT(self, compound):
        compound['id'] = String('Chest')
        tagList = List[Compound]()
        for i in range(len(self.__chestContents)):
            if self.__chestContents[i]:
                comp = Compound({'Slot': Byte(i)})
                self.__chestContents[i].writeToNBT(comp)
                tagList.append(comp)

        compound['Items'] = tagList

    def getInventoryStackLimit(self):
        return Inventory.STACK_LIMIT
