from mc.net.minecraft.game.item.Item import Item

class ItemArmor(Item):
    __damageReduceAmountArray = (3, 8, 6, 3)
    __maxDamageArray = (11, 16, 15, 13)

    def __init__(self, items, itemId, armorLevel, renderIndex, armorType):
        super().__init__(items, itemId)
        self.armorType = armorType
        self.renderIndex = renderIndex
        self.damageReduceAmount = ItemArmor.__damageReduceAmountArray[armorType]
        self._maxDamage = ItemArmor.__maxDamageArray[armorType] * 3 << armorLevel
        self._maxStackSize = 1
