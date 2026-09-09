from mc.net.minecraft.game.item.Item import Item
from mc.net.minecraft.game.item.Items import items
from mc.net.minecraft.game.item.ItemStack import ItemStack
from mc.net.minecraft.game.item.recipe.CraftingRecipe import CraftingRecipe
from mc.net.minecraft.game.item.recipe.RecipesArmor import RecipesArmor
from mc.net.minecraft.game.item.recipe.RecipesTools import RecipesTools
from mc.net.minecraft.game.item.recipe.RecipesWeapons import RecipesWeapons
from mc.net.minecraft.game.item.recipe.RecipesIngots import RecipesIngots
from mc.net.minecraft.game.item.recipe.RecipesFood import RecipesFood
from mc.net.minecraft.game.item.recipe.RecipesCrafting import RecipesCrafting
from mc.net.minecraft.game.item.recipe.RecipeSorter import RecipeSorter
from mc.net.minecraft.game.level.block.Block import Block
from mc.net.minecraft.game.level.block.Blocks import blocks
from functools import cmp_to_key

class CraftingManager:
    instance = None

    @classmethod
    def getInstance(cls):
        if cls.instance:
            return cls.instance

        cls.instance = cls()
        return cls.instance

    def __init__(self):
        self.__recipes = []

        RecipesTools().addRecipes(self)
        RecipesWeapons().addRecipes(self)
        RecipesIngots().addRecipes(self)
        RecipesFood()
        self.addRecipe(ItemStack(items.bowlSoup),
                       ('Y', 'X', '#', ord('X'), blocks.mushroomBrown, ord('Y'),
                        blocks.mushroomRed, ord('#'), items.bowlEmpty))
        self.addRecipe(ItemStack(items.bowlSoup),
                       ('Y', 'X', '#', ord('X'), blocks.mushroomRed, ord('Y'),
                        blocks.mushroomBrown, ord('#'), items.bowlEmpty))
        RecipesCrafting()
        self.addRecipe(ItemStack(blocks.chest),
                       ('###', '# #', '###', ord('#'), blocks.planks))
        self.addRecipe(ItemStack(blocks.stoneOvenIdle),
                       ('###', '# #', '###', ord('#'), blocks.cobblestone))
        self.addRecipe(ItemStack(blocks.planks, 4),
                       ('#', ord('#'), blocks.wood))
        self.addRecipe(ItemStack(blocks.workbench),
                       ('##', '##', ord('#'), blocks.planks))
        RecipesArmor().addRecipes(self)
        self.addRecipe(ItemStack(blocks.clothGray, 1),
                       ('###', '###', '###', ord('#'), items.silk))
        self.addRecipe(ItemStack(blocks.tnt, 1),
                       ('X#X', '#X#', 'X#X', ord('X'),
                       items.gunpowder, ord('#'), blocks.sand))
        self.addRecipe(ItemStack(items.bow, 1),
                       (' #X', '# X', ' #X', ord('X'),
                       items.silk, ord('#'), items.stick))
        self.addRecipe(ItemStack(blocks.stairSingle, 3),
                       ('###', ord('#'), blocks.cobblestone))
        self.addRecipe(ItemStack(items.stick, 4),
                       ('#', '#', ord('#'), blocks.planks))
        self.addRecipe(ItemStack(blocks.torch, 4),
                       ('X', '#', ord('X'), items.coal, ord('#'), items.stick))
        self.addRecipe(ItemStack(items.bowlEmpty, 4),
                       ('# #', ' # ', ord('#'), blocks.planks))
        self.addRecipe(ItemStack(items.striker, 1),
                       ('A ', ' B', ord('A'), items.ingotIron, ord('B'), items.flint))
        self.addRecipe(ItemStack(items.bread, 1),
                       ('###', ord('#'), items.wheat))
        self.addRecipe(ItemStack(items.painting, 1),
                       ('###', '#X#', '###', ord('#'), blocks.planks,
                        ord('X'), blocks.clothGray))
        self.__recipes = sorted(
            self.__recipes,
            key=cmp_to_key(RecipeSorter(self).compare)
        )
        print(len(self.__recipes), 'recipes')

    def addRecipe(self, stack, solution):
        slotLocations = ''
        slot = 0
        recipeWidth = 0
        recipeHeight = 0
        if isinstance(solution[0], tuple):
            slot += 1
            pattern = solution[0]
            for slots in pattern:
                recipeHeight += 1
                recipeWidth = len(slots)
                slotLocations += slots
        else:
            while isinstance(solution[slot], str):
                slots = solution[slot]
                slot += 1
                recipeHeight += 1
                recipeWidth = len(slots)
                slotLocations += slots

        slot2item = {}
        while slot < len(solution):
            slots = solution[slot]
            idx = 0
            if isinstance(solution[slot + 1], Item):
                idx = solution[slot + 1].shiftedIndex
            elif isinstance(solution[slot + 1], Block):
                idx = solution[slot + 1].blockID

            slot2item[slots] = idx
            slot += 2

        recipeItems = [0] * recipeWidth * recipeHeight
        for i in range(recipeWidth * recipeHeight):
            slot = slotLocations[i]
            if slot2item.get(ord(slot)):
                recipeItems[i] = slot2item.get(ord(slot))
            else:
                recipeItems[i] = -1

        self.__recipes.append(
            CraftingRecipe(recipeWidth, recipeHeight, recipeItems, stack)
        )

    def findMatchingRecipe(self, craftItems):
        for recipe in self.__recipes:
            if recipe.matchRecipe(craftItems):
                return recipe.createResult()

        return None
