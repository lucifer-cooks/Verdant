from mc.net.minecraft.game.item.Item import Item

class ItemPainting(Item):

    def __init__(self, items, itemId):
        super().__init__(items, 65)
        self._maxDamage = 64

    def onItemUse(self, stack, world, x, y, z, sideHit):
        if sideHit == 0:
            return False
        elif sideHit == 1:
            return False
        elif x <= 0 or y <= 0 or z <= 0 or x >= world.width - 1 or \
           y >= world.height - 1 or z >= world.length - 2:
            return False

        direction = 0
        if sideHit == 4:
            direction = 1
        elif sideHit == 3:
            direction = 2
        elif sideHit == 5:
            direction = 3

        from mc.net.minecraft.game.entity.EntityPainting import EntityPainting
        painting = EntityPainting(world, x, y, z, direction)
        if painting.onValidSurface():
            world.spawnEntityInWorld(painting)
            stack.stackSize -= 1

        return True
