from mc.net.minecraft.game.level.block.tileentity.TileEntity import TileEntity
from mc.net.minecraft.game.level.material.Material import Material
from mc.net.minecraft.game.level.block.Blocks import blocks
from mc.net.minecraft.game.item.ItemStack import ItemStack
from mc.net.minecraft.game.item.Items import items
from mc.net.minecraft.game.Inventory import Inventory

from nbtlib.tag import Compound, String, Short, Byte, List

class TileEntityFurnace(TileEntity, Inventory):

    def __init__(self):
        super().__init__()
        self.__furnaceItemStacks = [None] * 3
        self.__furnaceBurnTime = 0
        self.__currentItemBurnTime = 0
        self.__furnaceCookTime = 0

    def getSizeInventory(self):
        return len(self.__furnaceItemStacks)

    def getStackInSlot(self, slot):
        return self.__furnaceItemStacks[slot]

    def decrStackSize(self, slot, size):
        if not self.__furnaceItemStacks[slot]:
            return None

        if self.__furnaceItemStacks[slot].stackSize <= size:
            stack = self.__furnaceItemStacks[slot]
            self.__furnaceItemStacks[slot] = None
            return stack
        else:
            stack = self.__furnaceItemStacks[slot].splitStack(size)
            if self.__furnaceItemStacks[slot].stackSize == 0:
                self.__furnaceItemStacks[slot] = None

            return stack

    def setInventorySlotContents(self, slot, stack):
        self.__furnaceItemStacks[slot] = stack
        if stack:
            stack.stackSize = min(stack.stackSize, Inventory.STACK_LIMIT)

    def getInvName(self):
        return 'Chest'

    def readFromNBT(self, compound):
        super().readFromNBT(compound)
        tagList = compound.get('Items', List[Compound]())
        self.__furnaceItemStacks = [None] * len(self.__furnaceItemStacks)
        for tag in tagList:
            slot = tag.get('Slot', Byte(0)).real
            if slot >= 0 and slot < len(self.__furnaceItemStacks):
                self.__furnaceItemStacks[slot] = ItemStack(tag)

        self.__furnaceBurnTime = compound.get('BurnTime', Short(0)).real
        self.__furnaceCookTime = compound.get('CookTime', Short(0)).real
        self.__currentItemBurnTime = TileEntityFurnace.__getItemBurnTime(
            self.__furnaceItemStacks[1]
        ) or self.__furnaceBurnTime
        print(f'Lit: {self.__furnaceBurnTime}/{self.__currentItemBurnTime}')

    def writeToNBT(self, compound):
        super().writeToNBT(compound)
        compound['BurnTime'] = Short(self.__furnaceBurnTime)
        compound['CookTime'] = Short(self.__furnaceCookTime)
        compound['id'] = String('Furnace')
        tagList = List[Compound]()
        for i in range(len(self.__furnaceItemStacks)):
            if self.__furnaceItemStacks[i]:
                comp = Compound({'Slot': Byte(i)})
                self.__furnaceItemStacks[i].writeToNBT(comp)
                tagList.append(comp)

        compound['Items'] = tagList

    def getInventoryStackLimit(self):
        return Inventory.STACK_LIMIT

    def getCookProgressScaled(self, scale):
        return self.__furnaceCookTime * 24 // 200

    def getBurnTimeRemainingScaled(self, scale):
        return self.__furnaceBurnTime * 12 // self.__currentItemBurnTime

    def isBurning(self):
        return self.__furnaceBurnTime > 0

    def updateEntity(self):
        isBurning = self.isBurning()
        if self.isBurning():
            self.__furnaceBurnTime -= 1

        if self.__furnaceBurnTime == 0 and self.__canSmelt():
            self.__furnaceBurnTime = TileEntityFurnace.__getItemBurnTime(
                self.__furnaceItemStacks[1]
            )
            self.__currentItemBurnTime = self.__furnaceBurnTime
            if self.isBurning() and self.__furnaceItemStacks[1]:
                self.__furnaceItemStacks[1].stackSize -= 1
                if self.__furnaceItemStacks[1].stackSize == 0:
                    self.__furnaceItemStacks[1] = None

        if self.isBurning() and self.__canSmelt():
            self.__furnaceCookTime += 1
            if self.__furnaceCookTime == 200:
                self.__furnaceCookTime = 0
                if self.__canSmelt():
                    itemId = TileEntityFurnace.__smeltItem(
                        self.__furnaceItemStacks[0].getItem().shiftedIndex
                    )
                    if not self.__furnaceItemStacks[2]:
                        self.__furnaceItemStacks[2] = ItemStack(itemId, 1)
                    elif self.__furnaceItemStacks[2].itemID == itemId:
                        self.__furnaceItemStacks[2].stackSize += 1

                    self.__furnaceItemStacks[0].stackSize -= 1
                    if self.__furnaceItemStacks[0].stackSize <= 0:
                        self.__furnaceItemStacks[0] = None
        else:
            self.__furnaceCookTime = 0

        if isBurning != self.isBurning():
            isBurning = self.isBurning()
            face = self.worldObj.getBlockMetadata(self.xCoord, self.yCoord,
                                                  self.zCoord)
            entity = self.worldObj.getBlockTileEntity(self.xCoord, self.yCoord,
                                                      self.zCoord)
            if isBurning:
                self.worldObj.setBlockWithNotify(
                    self.xCoord, self.yCoord, self.zCoord,
                    blocks.stoneOvenActive.blockID
                )
            else:
                self.worldObj.setBlockWithNotify(
                    self.xCoord, self.yCoord, self.zCoord,
                    blocks.stoneOvenIdle.blockID
                )

            self.worldObj.setBlockMetadata(self.xCoord, self.yCoord,
                                           self.zCoord, face)
            self.worldObj.setBlockTileEntity(self.xCoord, self.yCoord,
                                             self.zCoord, entity)

    def __canSmelt(self):
        if not self.__furnaceItemStacks[0]:
            return False

        itemId = TileEntityFurnace.__smeltItem(
            self.__furnaceItemStacks[0].getItem().shiftedIndex
        )
        if itemId < 0:
            return False
        elif not self.__furnaceItemStacks[2]:
            return True
        elif self.__furnaceItemStacks[2].itemID != itemId:
            return False
        elif self.__furnaceItemStacks[2].stackSize < 64:
            return True
        else:
            return self.__furnaceItemStacks[2].stackSize < \
                   items.itemsList[itemId].getItemStackLimit()

    @staticmethod
    def __smeltItem(itemId):
        if itemId == blocks.oreIron.blockID:
            return items.ingotIron.shiftedIndex
        elif itemId == blocks.oreGold.blockID:
            return items.ingotGold.shiftedIndex
        elif itemId == blocks.oreDiamond.blockID:
            return items.diamond.shiftedIndex
        elif itemId == blocks.sand.blockID:
            return blocks.glass.blockID
        elif itemId == items.porkRaw.shiftedIndex:
            return items.porkCooked.shiftedIndex
        elif itemId == blocks.cobblestone.blockID:
            return blocks.stone.blockID
        else:
            return -1

    @staticmethod
    def __getItemBurnTime(stack):
        if not stack:
            return 0

        itemId = stack.getItem().shiftedIndex
        if itemId < 256 and blocks.blocksList[itemId].material == Material.wood:
            return 300
        elif itemId == items.stick.shiftedIndex:
            return 100
        elif itemId == items.coal.shiftedIndex:
            return 1600
        else:
            return 0
