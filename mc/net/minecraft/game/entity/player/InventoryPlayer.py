from mc.net.minecraft.game.level.block.Blocks import blocks
from mc.net.minecraft.game.item.ItemArmor import ItemArmor
from mc.net.minecraft.game.item.ItemStack import ItemStack
from mc.net.minecraft.game.Inventory import Inventory

class InventoryPlayer(Inventory):

    def __init__(self, player):
        self.__player = player
        self.currentItem = 0
        self.mainInventory = [None] * 36
        self.armorInventory = [None] * 4

    def getCurrentItem(self):
        return self.mainInventory[self.currentItem]

    def __getInventorySlotContainItem(self, slot):
        for i in range(len(self.mainInventory)):
            if self.mainInventory[i] and self.mainInventory[i].itemID == slot:
                return i

        return -1

    def __storeItemStack(self):
        for i in range(len(self.mainInventory)):
            if not self.mainInventory[i]:
                return i

        return -1

    def getFirstEmptyStack(self, index):
        index = self.__getInventorySlotContainItem(index)
        if index >= 0 and index < 9:
            self.currentItem = index

    def swapPaint(self, dy):
        if dy > 0:
            dy = 1
        elif dy < 0:
            dy = -1

        self.currentItem -= dy
        while self.currentItem < 0:
            self.currentItem += 9

        while self.currentItem >= 9:
            self.currentItem -= 9

    def tick(self):
        for i in range(len(self.mainInventory)):
            if self.mainInventory[i] and self.mainInventory[i].animationsToGo > 0:
                self.mainInventory[i].animationsToGo -= 1

    def consumeInventoryItem(self, item):
        slot = self.__getInventorySlotContainItem(item)
        if slot < 0:
            return False

        self.mainInventory[slot].stackSize -= 1
        if self.mainInventory[slot].stackSize <= 0:
            self.mainInventory[slot] = None

        return True

    def addItemStackToInventory(self, stack):
        if not stack.itemDamage:
            stackSize = stack.stackSize
            itemId = stack.itemID
            maybeSlot = 0
            slot = 0
            while True:
                if maybeSlot >= len(self.mainInventory):
                    slot = -1
                    break

                if self.mainInventory[maybeSlot] and self.mainInventory[maybeSlot].itemID == itemId:
                    item = self.mainInventory[maybeSlot]
                    if self.mainInventory[maybeSlot].stackSize < item.getItem().getItemStackLimit() and \
                       self.mainInventory[maybeSlot].stackSize < Inventory.STACK_LIMIT:
                        slot = maybeSlot
                        break

                maybeSlot += 1

            if slot < 0:
                slot = self.__storeItemStack()

            if slot >= 0:
                if not self.mainInventory[slot]:
                    self.mainInventory[slot] = ItemStack(itemId, 0)

                stackExcess = stackSize
                item = self.mainInventory[slot]
                if stackSize > item.getItem().getItemStackLimit() - self.mainInventory[slot].stackSize:
                    item = self.mainInventory[slot]
                    stackExcess = item.getItem().getItemStackLimit() - self.mainInventory[slot].stackSize

                stackExcess = min(
                    stackExcess,
                    Inventory.STACK_LIMIT - self.mainInventory[slot].stackSize
                )
                if stackExcess == 0:
                    stackSize = stackSize
                else:
                    stackSize -= stackExcess
                    self.mainInventory[slot].stackSize += stackExcess
                    self.mainInventory[slot].animationsToGo = 5

            stack.stackSize = stackSize
            if stack.stackSize == 0:
                return True

        slot = self.__storeItemStack()
        if slot >= 0:
            self.mainInventory[slot] = stack
            self.mainInventory[slot].animationsToGo = 5
            return True
        else:
            return False

    def decrStackSize(self, slot, size):
        inv = self.mainInventory
        if slot >= len(self.mainInventory):
            inv = self.armorInventory
            slot -= len(self.mainInventory)

        if not inv[slot]:
            return None

        if inv[slot].stackSize <= size:
            stack = inv[slot]
            inv[slot] = None
            return stack
        else:
            stack = inv[slot].splitStack(size)
            if inv[slot].stackSize == 0:
                inv[slot] = None

            return stack

    def setInventorySlotContents(self, slot, stack):
        inv = self.mainInventory
        if slot >= len(self.mainInventory):
            inv = self.armorInventory
            slot -= len(self.mainInventory)

        inv[slot] = stack

    def getSizeInventory(self):
        return len(self.mainInventory) + 4

    def getStackInSlot(self, slot):
        inv = self.mainInventory
        if slot >= len(self.mainInventory):
            inv = self.armorInventory
            slot -= len(self.mainInventory)

        return inv[slot]

    def getInvName(self):
        return 'Inventory'

    def getInventoryStackLimit(self):
        return Inventory.STACK_LIMIT

    def getPlayerArmorValue(self):
        damageReduceCount = 0
        damageCount = 0
        maxDamageCount = 0
        for slot in self.armorInventory:
            if slot and isinstance(slot.getItem(), ItemArmor):
                maxDamage = slot.isItemStackDamageable()
                damage = maxDamage - slot.itemDamage
                damageCount += damage
                maxDamageCount += maxDamage
                damageReduceCount += slot.getItem().damageReduceAmount

        if maxDamageCount == 0:
            return 0
        else:
            return (damageReduceCount - 1) * damageCount // maxDamageCount + 1
