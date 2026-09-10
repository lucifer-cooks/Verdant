from mc.net.minecraft.game.level.block.Block import Block
from mc.net.minecraft.game.level.material.Material import Material
from mc.JavaUtils import Random

class BlockSand(Block):

    def __init__(self, blocks, blockId, tex):
        super().__init__(blocks, blockId, tex, Material.sand)
        Random()
        self._falling_blocks = set()

    def onBlockAdded(self, world, x, y, z):
        self.__tryToFall(world, x, y, z)

    def onNeighborBlockChange(self, world, x, y, z, blockType):
        # Prevent recursion by checking if this block is already being processed
        block_key = (x, y, z)
        if block_key not in self._falling_blocks:
            self.__tryToFall(world, x, y, z)

    def __tryToFall(self, world, x, y, z):
        block_key = (x, y, z)
        if block_key in self._falling_blocks:
            return
        
        self._falling_blocks.add(block_key)
        
        try:
            newY = y
            while True:
                blockId = world.getBlockId(x, newY - 1, z)
                if blockId == 0:
                    stop = True
                elif blockId == self.blocks.fire.blockID:
                    stop = True
                else:
                    material = self.blocks.blocksList[blockId].material
                    stop = True if material == Material.water else material == Material.lava

                if not stop or newY < 0:
                    if newY < 0:
                        world.setTileNoUpdate(x, y, z, 0)

                    if newY != y:
                        blockId = world.getBlockId(x, newY, z)
                        if blockId > 0 and self.blocks.blocksList[blockId].material != Material.air:
                            world.setTileNoUpdate(x, newY, z, 0)

                        # Use setTileNoUpdate instead of swap to prevent neighbor notification cascade
                        world.setTileNoUpdate(x, newY, z, self.blockID)
                        world.setTileNoUpdate(x, y, z, 0)

                    return

                newY -= 1
                if world.getBlockId(x, newY, z) == self.blocks.fire.blockID:
                    world.setBlock(x, newY, z, 0)
        finally:
            self._falling_blocks.discard(block_key)
