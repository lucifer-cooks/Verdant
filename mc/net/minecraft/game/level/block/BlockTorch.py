from mc.net.minecraft.game.level.block.Block import Block
from mc.net.minecraft.game.level.material.Material import Material

class BlockTorch(Block):

    def __init__(self, blocks, blockId, tex):
        super().__init__(blocks, 50, 80, Material.circuits)
        self._setTickOnLoad(True)

    def getCollisionBoundingBoxFromPool(self, x, y, z):
        return None

    def isOpaqueCube(self):
        return False

    def renderAsNormalBlock(self):
        return False

    def getRenderType(self):
        return 2

    def canPlaceBlockAt(self, world, x, y, z):
        if world.isBlockNormalCube(x - 1, y, z):
            return True
        elif world.isBlockNormalCube(x + 1, y, z):
            return True
        elif world.isBlockNormalCube(x, y, z - 1):
            return True
        elif world.isBlockNormalCube(x, y, z + 1):
            return True
        else:
            return world.isBlockNormalCube(x, y - 1, z)

    def onBlockPlaced(self, world, x, y, z, metadata):
        blockMeta = world.getBlockMetadata(x, y, z)
        if metadata == 1 and world.isBlockNormalCube(x, y - 1, z):
            blockMeta = 5
        elif metadata == 2 and world.isBlockNormalCube(x, y, z + 1):
            blockMeta = 4
        elif metadata == 3 and world.isBlockNormalCube(x, y, z - 1):
            blockMeta = 3
        elif metadata == 4 and world.isBlockNormalCube(x + 1, y, z):
            blockMeta = 2
        elif metadata == 5 and world.isBlockNormalCube(x - 1, y, z):
            blockMeta = 1

        world.setBlockMetadata(x, y, z, blockMeta)

    def updateTick(self, world, x, y, z, random):
        super().updateTick(world, x, y, z, random)
        if world.getBlockMetadata(x, y, z) == 0:
            self.onBlockAdded(world, x, y, z)

    def onBlockAdded(self, world, x, y, z):
        if world.isBlockNormalCube(x - 1, y, z):
            world.setBlockMetadata(x, y, z, 1)
        elif world.isBlockNormalCube(x + 1, y, z):
            world.setBlockMetadata(x, y, z, 2)
        elif world.isBlockNormalCube(x, y, z - 1):
            world.setBlockMetadata(x, y, z, 3)
        elif world.isBlockNormalCube(x, y, z + 1):
            world.setBlockMetadata(x, y, z, 4)
        elif world.isBlockNormalCube(x, y - 1, z):
            world.setBlockMetadata(x, y, z, 5)

        self.__dropTorchIfCantStay(world, x, y, z)

    def onNeighborBlockChange(self, world, x, y, z, blockType):
        if not self.__dropTorchIfCantStay(world, x, y, z):
            return

        metadata = world.getBlockMetadata(x, y, z)
        drop = False
        if not world.isBlockNormalCube(x - 1, y, z) and metadata == 1:
            drop = True
        elif not world.isBlockNormalCube(x + 1, y, z) and metadata == 2:
            drop = True
        elif not world.isBlockNormalCube(x, y, z - 1) and metadata == 3:
            drop = True
        elif not world.isBlockNormalCube(x, y, z + 1) and metadata == 4:
            drop = True
        elif not world.isBlockNormalCube(x, y - 1, z) and metadata == 5:
            drop = True

        if drop:
            self.dropBlockAsItem(world, x, y, z, world.getBlockMetadata(x, y, z))
            world.setBlockWithNotify(x, y, z, 0)

    def __dropTorchIfCantStay(self, world, x, y, z):
        if not self.canPlaceBlockAt(world, x, y, z):
            self.dropBlockAsItem(world, x, y, z, world.getBlockMetadata(x, y, z))
            world.setBlockWithNotify(x, y, z, 0)
            return False
        else:
            return True

    def collisionRayTrace(self, world, x, y, z, v0, v1):
        metadata = world.getBlockMetadata(x, y, z)
        if metadata == 1:
            self._setBlockBounds(0.0, 0.2, 0.35, 0.3, 0.8, 0.65)
        elif metadata == 2:
            self._setBlockBounds(0.7, 0.2, 0.35, 1.0, 0.8, 0.65)
        elif metadata == 3:
            self._setBlockBounds(0.35, 0.2, 0.0, 0.65, 0.8, 0.3)
        elif metadata == 4:
            self._setBlockBounds(0.35, 0.2, 0.7, 0.65, 0.8, 1.0)
        else:
            self._setBlockBounds(0.4, 0.0, 0.4, 0.6, 0.6, 0.6)

        return super().collisionRayTrace(world, x, y, z, v0, v1)

    def randomDisplayTick(self, world, x, y, z, random):
        metadata = world.getBlockMetadata(x, y, z)
        posX = x + 0.5
        posY = y + 0.7
        posZ = z + 0.5
        if metadata == 1:
            world.spawnParticle('smoke', posX - 0.27, posY + 0.22, posZ, 0.0, 0.0, 0.0)
            world.spawnParticle('flame', posX - 0.27, posY + 0.22, posZ, 0.0, 0.0, 0.0)
        elif metadata == 2:
            world.spawnParticle('smoke', posX + 0.27, posY + 0.22, posZ, 0.0, 0.0, 0.0)
            world.spawnParticle('flame', posX + 0.27, posY + 0.22, posZ, 0.0, 0.0, 0.0)
        elif metadata == 3:
            world.spawnParticle('smoke', posX, posY + 0.22, posZ - 0.27, 0.0, 0.0, 0.0)
            world.spawnParticle('flame', posX, posY + 0.22, posZ - 0.27, 0.0, 0.0, 0.0)
        elif metadata == 4:
            world.spawnParticle('smoke', posX, posY + 0.22, posZ + 0.27, 0.0, 0.0, 0.0)
            world.spawnParticle('flame', posX, posY + 0.22, posZ + 0.27, 0.0, 0.0, 0.0)
        else:
            world.spawnParticle('smoke', posX, posY, posZ, 0.0, 0.0, 0.0)
            world.spawnParticle('flame', posX, posY, posZ, 0.0, 0.0, 0.0)
