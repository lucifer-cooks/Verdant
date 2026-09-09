from mc.net.minecraft.game.level.block.Block import Block
from mc.net.minecraft.game.level.material.Material import Material
from mc.net.minecraft.game.physics.AxisAlignedBB import AxisAlignedBB

class BlockFarmland(Block):

    def __init__(self, blocks, blockId):
        super().__init__(blocks, 60, Material.ground)
        self.blockIndexInTexture = 87
        self._setTickOnLoad(True)
        self._setBlockBounds(0.0, 0.0, 0.0, 1.0, 15.0 / 16.0, 1.0)
        self.setLightOpacity(255)

    def getCollisionBoundingBoxFromPool(self, x, y, z):
        return AxisAlignedBB(x, y, z, x + 1, y + 1, z + 1)

    def isOpaqueCube(self):
        return False

    def renderAsNormalBlock(self):
        return False

    def getBlockTextureFromSideAndMetadata(self, layer, metadata):
        if layer == 1 and metadata > 0:
            return self.blockIndexInTexture - 1
        elif layer == 1:
            return self.blockIndexInTexture
        else:
            return 2

    def updateTick(self, world, x, y, z, random):
        if random.nextInt(5) != 0:
            return

        xx = x - 4
        waterNear = False
        while True:
            if xx > x + 4:
                break

            for yy in range(y, y + 2):
                for zz in range(z - 4, z + 5):
                    if world.getBlockMaterial(xx, yy, zz) == Material.water:
                        waterNear = True
                        break

                if waterNear:
                    break

            if waterNear:
                break
            else:
                xx += 1

        if waterNear:
            world.setBlockMetadata(x, y, z, 7)
            return

        tickCounter = world.getBlockMetadata(x, y, z)
        if tickCounter > 0:
            world.setBlockMetadata(x, y, z, tickCounter - 1)
            return

        xx = x
        cropsPlanted = False
        while True:
            if xx > x:
                break

            for zz in range(z, z + 1):
                if world.getBlockId(xx, y + 1, zz) == self.blocks.crops.blockID:
                    cropsPlanted = True
                    break

            if cropsPlanted:
                break

            xx += 1

        if not cropsPlanted:
            world.setBlockWithNotify(x, y, z, self.blocks.dirt.blockID)

    def onEntityWalking(self, world, x, y, z):
        if world.rand.nextInt(4) == 0:
            world.setBlockWithNotify(x, y, z, self.blocks.dirt.blockID)

    def onNeighborBlockChange(self, world, x, y, z, blockType):
        super().onNeighborBlockChange(world, x, y, z, blockType)
        material = world.getBlockMaterial(x, y + 1, z)
        if material.isSolid():
            world.setBlockWithNotify(x, y, z, self.blocks.dirt.blockID)

    def idDropped(self, metadata, random):
        return self.blocks.dirt.idDropped(0, random)
