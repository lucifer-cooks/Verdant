from mc.net.minecraft.game.level.block.BlockFlower import BlockFlower

class BlockCrops(BlockFlower):

    def __init__(self, blocks, blockId, tex):
        super().__init__(blocks, 59, 88)
        self.blockIndexInTexture = 88
        self._setTickOnLoad(True)
        self._setBlockBounds(0.0, 0.0, 0.0, 1.0, 0.25, 1.0)

    def _canThisPlantGrowOnThisBlockID(self, blockId):
        return blockId == self.blocks.tilledField.blockID

    def updateTick(self, world, x, y, z, random):
        super().updateTick(world, x, y, z, random)
        if world.getBlockLightValue(x, y + 1, z) < 9:
            return

        ticks = world.getBlockMetadata(x, y, z)
        if ticks < 7:
            changeRate = 1.0
            north = world.getBlockId(x, y, z - 1)
            south = world.getBlockId(x, y, z + 1)
            west = world.getBlockId(x - 1, y, z)
            east = world.getBlockId(x + 1, y, z)
            northWest = world.getBlockId(x - 1, y, z - 1)
            northEast = world.getBlockId(x + 1, y, z - 1)
            southEast = world.getBlockId(x + 1, y, z + 1)
            southWest = world.getBlockId(x - 1, y, z + 1)
            adjacentCrops = west == self.blockID or east == self.blockID
            verticalCrops = north == self.blockID or south == self.blockID
            diagonalCrops = northWest == self.blockID or northEast == self.blockID or \
                            southEast == self.blockID or southWest == self.blockID
            for xx in range(x - 1, x + 2):
                for zz in range(z - 1, z + 2):
                    dirt = world.getBlockId(xx, y - 1, zz)
                    grow = 0.0
                    if dirt == self.blocks.tilledField.blockID:
                        grow = 1.0
                        if world.getBlockMetadata(xx, y - 1, zz) > 0:
                            grow = 3.0

                    if xx != x or zz != z:
                        grow /= 4.0

                    changeRate += grow

            if diagonalCrops or adjacentCrops and verticalCrops:
                changeRate /= 2.0

            if random.nextInt(int(100.0 / changeRate)) == 0:
                world.setBlockMetadata(x, y, z, ticks + 1)

    def getBlockTextureFromSideAndMetadata(self, layer, metadata):
        if metadata < 0:
            metadata = 7

        return self.blockIndexInTexture + metadata

    def getRenderType(self):
        return 6

    def onBlockDestroyedByPlayer(self, world, x, y, z, metadata):
        from mc.net.minecraft.game.entity.misc.EntityItem import EntityItem
        from mc.net.minecraft.game.item.ItemStack import ItemStack
        from mc.net.minecraft.game.item.Items import items
        super().onBlockDestroyedByPlayer(world, x, y, z, metadata)
        for i in range(3):
            if world.rand.nextInt(15) <= metadata:
                dropX = world.rand.nextFloat() * 0.7 + 0.15
                dropY = world.rand.nextFloat() * 0.7 + 0.15
                dropZ = world.rand.nextFloat() * 0.7 + 0.15
                entity = EntityItem(world, x + dropX, y + dropY, z + dropZ,
                                    ItemStack(items.seeds))
                entity.delayBeforeCanPickup = 10
                world.spawnEntityInWorld(entity)

    def idDropped(self, metadata, random):
        from mc.net.minecraft.game.item.Items import items
        print('Get resource:', metadata)
        return items.wheat.shiftedIndex if metadata == 7 else -1

    def quantityDropped(self, random):
        return 1
