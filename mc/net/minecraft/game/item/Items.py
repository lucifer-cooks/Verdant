from mc.net.minecraft.game.item.ItemFlintAndSteel import ItemFlintAndSteel
from mc.net.minecraft.game.item.ItemPainting import ItemPainting
from mc.net.minecraft.game.item.ItemPickaxe import ItemPickaxe
from mc.net.minecraft.game.item.ItemArmor import ItemArmor
from mc.net.minecraft.game.item.ItemSword import ItemSword
from mc.net.minecraft.game.item.ItemSpade import ItemSpade
from mc.net.minecraft.game.item.ItemSeeds import ItemSeeds
from mc.net.minecraft.game.item.ItemSoup import ItemSoup
from mc.net.minecraft.game.item.ItemBlock import ItemBlock
from mc.net.minecraft.game.item.ItemFood import ItemFood
from mc.net.minecraft.game.item.ItemAxe import ItemAxe
from mc.net.minecraft.game.item.ItemBow import ItemBow
from mc.net.minecraft.game.item.ItemHoe import ItemHoe
from mc.net.minecraft.game.item.Item import Item
from mc.net.minecraft.game.level.block.Blocks import blocks

class Items:

    def __init__(self):
        self.itemsList = [None] * 1024

        self.shovel = ItemSpade(self, 0, 2).setIconIndex(82)
        self.pickaxeSteel = ItemPickaxe(self, 1, 2).setIconIndex(98)
        self.axeSteel = ItemAxe(self, 2, 2).setIconIndex(114)

        self.striker = ItemFlintAndSteel(self, 3).setIconIndex(5)

        apple = ItemFood(self, 4, 4).setIconIndex(4)

        self.bow = ItemBow(self, 5).setIconIndex(21)
        self.arrow = Item(self, 6).setIconIndex(37)

        self.coal = Item(self, 7).setIconIndex(7)
        self.diamond = Item(self, 8).setIconIndex(55)
        self.ingotIron = Item(self, 9).setIconIndex(23)
        self.ingotGold = Item(self, 10).setIconIndex(39)

        self.swordSteel = ItemSword(self, 11, 2).setIconIndex(66)
        self.swordWood = ItemSword(self, 12, 0).setIconIndex(64)
        self.shovelWood = ItemSpade(self, 13, 0).setIconIndex(80)
        self.pickaxeWood = ItemPickaxe(self, 14, 0).setIconIndex(96)
        self.axeWood = ItemAxe(self, 15, 0).setIconIndex(112)

        self.swordStone = ItemSword(self, 16, 1).setIconIndex(65)
        self.shovelStone = ItemSpade(self, 17, 1).setIconIndex(81)
        self.pickaxeStone = ItemPickaxe(self, 18, 1).setIconIndex(97)
        self.axeStone = ItemAxe(self, 19, 1).setIconIndex(113)

        self.swordDiamond = ItemSword(self, 20, 3).setIconIndex(67)
        self.shovelDiamond = ItemSpade(self, 21, 3).setIconIndex(83)
        self.pickaxeDiamond = ItemPickaxe(self, 22, 3).setIconIndex(99)
        self.axeDiamond = ItemAxe(self, 23, 3).setIconIndex(115)

        self.stick = Item(self, 24).setIconIndex(53)

        self.bowlEmpty = Item(self, 25).setIconIndex(71)
        self.bowlSoup = ItemSoup(self, 26, 10).setIconIndex(72)

        self.swordGold = ItemSword(self, 27, 0).setIconIndex(68)
        self.shovelGold = ItemSpade(self, 28, 0).setIconIndex(84)
        self.pickaxeGold = ItemPickaxe(self, 29, 0).setIconIndex(100)
        self.axeGold = ItemAxe(self, 30, 0).setIconIndex(116)

        self.silk = Item(self, 31).setIconIndex(8)
        self.feather = Item(self, 32).setIconIndex(24)

        self.gunpowder = Item(self, 33).setIconIndex(40)

        self.hoeWood = ItemHoe(self, 34, 0).setIconIndex(128)
        self.hoeStone = ItemHoe(self, 35, 1).setIconIndex(129)
        self.hoeSteel = ItemHoe(self, 36, 2).setIconIndex(130)
        self.hoeDiamond = ItemHoe(self, 37, 3).setIconIndex(131)
        self.hoeGold = ItemHoe(self, 38, 4).setIconIndex(132)

        self.seeds = ItemSeeds(self, 39, blocks.crops.blockID).setIconIndex(9)
        self.wheat = Item(self, 40).setIconIndex(25)
        self.bread = ItemFood(self, 41, 5).setIconIndex(41)

        self.helmetLeather = ItemArmor(self, 42, 0, 0, 0).setIconIndex(0)
        self.plateLeather = ItemArmor(self, 43, 0, 0, 1).setIconIndex(16)
        self.legsLeather = ItemArmor(self, 44, 0, 0, 2).setIconIndex(32)
        self.bootsLeather = ItemArmor(self, 45, 0, 0, 3).setIconIndex(48)
        self.helmetChain = ItemArmor(self, 46, 1, 1, 0).setIconIndex(1)
        self.plateChain = ItemArmor(self, 47, 1, 1, 1).setIconIndex(17)
        self.legsChain = ItemArmor(self, 48, 1, 1, 2).setIconIndex(33)
        self.bootsChain = ItemArmor(self, 49, 1, 1, 3).setIconIndex(49)
        self.helmetSteel = ItemArmor(self, 50, 2, 2, 0).setIconIndex(2)
        self.plateSteel = ItemArmor(self, 51, 2, 2, 1).setIconIndex(18)
        self.legsSteel = ItemArmor(self, 52, 2, 2, 2).setIconIndex(34)
        self.bootsSteel = ItemArmor(self, 53, 2, 2, 3).setIconIndex(50)
        self.helmetDiamond = ItemArmor(self, 54, 3, 3, 0).setIconIndex(3)
        self.plateDiamond = ItemArmor(self, 55, 3, 3, 1).setIconIndex(19)
        self.legsDiamond = ItemArmor(self, 56, 3, 3, 2).setIconIndex(35)
        self.bootsDiamond = ItemArmor(self, 57, 3, 3, 3).setIconIndex(51)
        self.helmetGold = ItemArmor(self, 58, 1, 4, 0).setIconIndex(4)
        self.plateGold = ItemArmor(self, 59, 1, 4, 1).setIconIndex(20)
        self.legsGold = ItemArmor(self, 60, 1, 4, 2).setIconIndex(36)
        self.bootsGold = ItemArmor(self, 61, 1, 4, 3).setIconIndex(52)

        self.flint = Item(self, 62).setIconIndex(6)

        self.porkRaw = ItemFood(self, 63, 3).setIconIndex(87)
        self.porkCooked = ItemFood(self, 64, 8).setIconIndex(88)

        self.painting = ItemPainting(self, 65).setIconIndex(26)

        for i in range(256):
            if blocks.blocksList[i]:
                self.itemsList[i] = ItemBlock(self, i - 256)

items = Items()
