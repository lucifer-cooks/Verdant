from mc.net.minecraft.game.item.ItemStack import ItemStack

class CraftingRecipe:

    def __init__(self, width, height, items, output):
        self.__width = width
        self.__height = height
        self.__ingredientMap = items
        self.__recipeOutput = output

    def matchRecipe(self, items):
        for x in range(3 - self.__width + 1):
            for y in range(3 - self.__height + 1):
                if self.__matches(items, x, y, True):
                    return True
                if self.__matches(items, x, y, False):
                    return True

        return False

    def __matches(self, items, x, y, small):
        for xSlot in range(3):
            for ySlot in range(3):
                row = xSlot - x
                col = ySlot - y
                idx = -1
                if row >= 0 and col >= 0 and \
                   row < self.__width and col < self.__height:
                    if small:
                        idx = self.__ingredientMap[self.__width - row - 1 + col * self.__width]
                    else:
                        idx = self.__ingredientMap[row + col * self.__width]

                if items[xSlot + ySlot * 3] != idx:
                    return False

        return True

    def createResult(self):
        return ItemStack(self.__recipeOutput.itemID, self.__recipeOutput.stackSize)

    def getSize(self):
        return self.__width * self.__height
