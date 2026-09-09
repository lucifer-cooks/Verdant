from mc.net.minecraft.game.level.material.Material import Material
from mc.net.minecraft.game.level.block.BlockContainer import BlockContainer

class BlockFurnace(BlockContainer):

    def __init__(self, blocks, blockId, isActive):
        super().__init__(blocks, blockId, Material.rock)
        self.__isActive = isActive
        self.blockIndexInTexture = 45

    def onBlockAdded(self, world, x, y, z):
        super().onBlockAdded(world, x, y, z)
        self.__setDefaultDirection(world, x, y, z)

    def __setDefaultDirection(self, world, x, y, z):
        north = world.getBlockId(x, y, z - 1)
        south = world.getBlockId(x, y, z + 1)
        west = world.getBlockId(x - 1, y, z)
        east = world.getBlockId(x + 1, y, z)
        face = 3
        if self.blocks.opaqueCubeLookup[north] and not \
           self.blocks.opaqueCubeLookup[south]:
            face = 3
        if self.blocks.opaqueCubeLookup[south] and not \
           self.blocks.opaqueCubeLookup[north]:
            face = 2
        if self.blocks.opaqueCubeLookup[west] and not \
           self.blocks.opaqueCubeLookup[east]:
            face = 5
        if self.blocks.opaqueCubeLookup[east] and not \
           self.blocks.opaqueCubeLookup[west]:
            face = 4

        world.setBlockMetadata(x, y, z, face)

    def getBlockTexture(self, world, x, y, z, layer):
        if layer == 1:
            return self.blocks.stone.blockIndexInTexture
        elif layer == 0:
            return self.blocks.stone.blockIndexInTexture

        face = world.getBlockMetadata(x, y, z)
        if face == 0:
            self.__setDefaultDirection(world, x, y, z)
            face = world.getBlockMetadata(x, y, z)

        if layer != face:
            return self.blockIndexInTexture
        elif self.__isActive:
            return self.blockIndexInTexture + 16
        else:
            return self.blockIndexInTexture - 1

    def randomDisplayTick(self, world, x, y, z, random):
        if not self.__isActive:
            return

        face = world.getBlockMetadata(x, y, z)
        x += 0.5
        y += random.nextFloat() * 6.0 / 16.0
        z += 0.5
        ofs = random.nextFloat() * 0.6 - 0.3
        if face == 4:
            world.spawnParticle('smoke', x - 0.52, y, z + ofs, 0.0, 0.0, 0.0)
            world.spawnParticle('flame', x - 0.52, y, z + ofs, 0.0, 0.0, 0.0)
        elif face == 5:
            world.spawnParticle('smoke', x + 0.52, y, z + ofs, 0.0, 0.0, 0.0)
            world.spawnParticle('flame', x + 0.52, y, z + ofs, 0.0, 0.0, 0.0)
        elif face == 2:
            world.spawnParticle('smoke', x + ofs, y, z - 0.52, 0.0, 0.0, 0.0)
            world.spawnParticle('flame', x + ofs, y, z - 0.52, 0.0, 0.0, 0.0)
        elif face == 3:
            world.spawnParticle('smoke', x + ofs, y, z + 0.52, 0.0, 0.0, 0.0)
            world.spawnParticle('flame', x + ofs, y, z + 0.52, 0.0, 0.0, 0.0)

    def getBlockTextureFromSide(self, face):
        if face == 1:
            return self.blocks.stone.blockIndexInTexture
        elif face == 0:
            return self.blocks.stone.blockIndexInTexture
        elif face == 3:
            return self.blockIndexInTexture - 1
        else:
            return self.blockIndexInTexture

    def blockActivated(self, world, x, y, z, player):
        entity = world.getBlockTileEntity(x, y, z)
        player.displayGUIFurnace(entity)
        return True

    def _getBlockEntity(self):
        from mc.net.minecraft.game.level.block.tileentity.TileEntityFurnace import TileEntityFurnace
        return TileEntityFurnace()
