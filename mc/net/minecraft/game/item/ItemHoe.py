from mc.net.minecraft.game.level.block.Blocks import blocks
from mc.net.minecraft.game.level.material.Material import Material
from mc.net.minecraft.game.item.Item import Item

class ItemHoe(Item):

    def __init__(self, items, itemId, strength):
        super().__init__(items, itemId)
        self._maxStackSize = 1
        self._maxDamage = 32 << strength

    def onItemUse(self, stack, world, x, y, z, sideHit):
        from mc.net.minecraft.game.entity.misc.EntityItem import EntityItem
        from mc.net.minecraft.game.item.ItemStack import ItemStack
        if x <= 0 or y <= 0 or z <= 0 or x >= world.width - 1 or \
           y >= world.height - 1 or z >= world.length - 1:
            return False

        blockId = world.getBlockId(x, y, z)
        material = world.getBlockMaterial(x, y + 1, z)
        if (material.isSolid() or blockId != blocks.grass.blockID) and \
           blockId != blocks.dirt.blockID:
            return False

        step = blocks.tilledField.stepSound
        world.playSoundAtPlayer(
            x + 0.5, y + 0.5, z + 0.5, step.stepSoundDirStep(),
            (step.soundVolume + 1.0) / 2.0, step.soundPitch * 0.8
        )
        world.setBlockWithNotify(x, y, z, blocks.tilledField.blockID)
        stack.damageItem(1)
        if world.rand.nextInt(8) == 0 and blockId == blocks.grass.blockID:
            for i in range(1):
                xMove = world.rand.nextFloat() * 0.7 + 0.15
                zMove = world.rand.nextFloat() * 0.7 + 0.15
                entity = EntityItem(world, x + xMove, y + 1.2, z + zMove,
                                    ItemStack(self.items.seeds))
                entity.delayBeforeCanPickup = 10
                world.spawnEntityInWorld(entity)

        return True
