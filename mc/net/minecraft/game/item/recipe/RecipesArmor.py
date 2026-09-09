from mc.net.minecraft.game.item.Items import items
from mc.net.minecraft.game.item.ItemStack import ItemStack
from mc.net.minecraft.game.level.block.Blocks import blocks

class RecipesArmor:
    __recipePatterns = (('XXX', 'X X'), ('X X', 'XXX', 'XXX'), ('XXX', 'X X', 'X X'), ('X X', 'X X'))
    __recipeItems = (
        (blocks.clothGray, blocks.fire, items.ingotIron, items.diamond, items.ingotGold),
        (items.helmetLeather, items.helmetChain, items.helmetSteel, items.helmetDiamond, items.helmetGold),
        (items.plateLeather, items.plateChain, items.plateSteel, items.plateDiamond, items.plateGold),
        (items.legsLeather, items.legsChain, items.legsSteel, items.legsDiamond, items.legsGold),
        (items.bootsLeather, items.bootsChain, items.bootsSteel, items.bootsDiamond, items.bootsGold)
    )

    def addRecipes(self, craftingManager):
        for toolIdx, toolItem in enumerate(self.__recipeItems[0]):
            for toolType in range(len(self.__recipeItems) - 1):
                toolResult = self.__recipeItems[toolType + 1][toolIdx]
                craftingManager.addRecipe(
                    ItemStack(toolResult),
                    [self.__recipePatterns[toolType], ord('X'), toolItem]
                )
