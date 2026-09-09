from mc.net.minecraft.game.entity.misc.EntityItem import EntityItem
from mc.net.minecraft.game.entity.EnumArt import EnumArt
from mc.net.minecraft.game.entity.Entity import Entity
from mc.net.minecraft.game.item.ItemStack import ItemStack
from mc.net.minecraft.game.item.Items import items
from mc.net.minecraft.game.physics.AxisAlignedBB import AxisAlignedBB

from nbtlib.tag import String, Byte, Int

class EntityPainting(Entity):

    def __init__(self, world, xPosition=0, yPosition=0, zPosition=0, direction=0):
        super().__init__(world)
        self.__tickCounter1 = 0
        self.__xPosition = xPosition
        self.__yPosition = yPosition
        self.__zPosition = zPosition
        self.direction = direction
        self.art = None
        self.yOffset = 0.0
        self.setSize(0.5, 0.5)
        if xPosition or yPosition or xPosition or direction:
            paintings = []
            for art in EnumArt:
                self.art = art
                self.__setDirection(direction)
                if self.onValidSurface():
                    paintings.append(art)

            if paintings:
                self.art = paintings[self._rand.nextInt(len(paintings))]

            self.__setDirection(direction)

    def __setDirection(self, direction):
        self.direction = direction
        self.prevRotationYaw = self.rotationYaw = direction * 90
        sizeX = self.art.sizeX
        sizeY = self.art.sizeY
        sizeZ = self.art.sizeX
        if direction != 0 and direction != 2:
            sizeX = 0.5
        else:
            sizeZ = 0.5

        sizeX /= 32.0
        sizeY /= 32.0
        sizeZ /= 32.0
        x = self.__xPosition + 0.5
        y = self.__yPosition + 0.5
        z = self.__zPosition + 0.5
        if direction == 0:
            z -= 9.0 / 16.0
            x -= EntityPainting.__getArtSize(self.art.sizeX)
        elif direction == 1:
            x -= 9.0 / 16.0
            z += EntityPainting.__getArtSize(self.art.sizeX)
        elif direction == 2:
            z += 9.0 / 16.0
            x += EntityPainting.__getArtSize(self.art.sizeX)
        elif direction == 3:
            x += 9.0 / 16.0
            z -= EntityPainting.__getArtSize(self.art.sizeX)

        y += EntityPainting.__getArtSize(self.art.sizeY)
        self.setPosition(x, y, z)
        self.boundingBox = AxisAlignedBB(x - sizeX, y - sizeY, z - sizeZ,
                                         x + sizeX, y + sizeY, z + sizeZ)
        self.boundingBox = AxisAlignedBB(
            self.boundingBox.minX, self.boundingBox.minY, self.boundingBox.minZ,
            self.boundingBox.maxX - (0.1 / 16.0),
            self.boundingBox.maxY - (0.1 / 16.0),
            self.boundingBox.maxZ - (0.1 / 16.0)
        )

    @staticmethod
    def __getArtSize(size):
        return 0.5 if size == 32 else (0.5 if size == 64 else 0.0)

    def onEntityUpdate(self):
        self.__tickCounter1 += 1
        if self.__tickCounter1 - 1 == 100 and not self.onValidSurface():
            self.__tickCounter1 = 0
            self.setEntityDead()
            self._worldObj.spawnEntityInWorld(EntityItem(self._worldObj, self.posX,
                                                         self.posY, self.posZ,
                                                         ItemStack(items.painting)))
    def onValidSurface(self):
        if self._worldObj.getCollidingBoundingBoxes(self.boundingBox):
            return False

        sizeX = self.art.sizeX // 16
        sizeY = self.art.sizeY // 16
        xPos = self.__xPosition
        zPos = self.__zPosition
        if self.direction == 0:
            xPos = int(self.posX - self.art.sizeX / 32.0)
        if self.direction == 1:
            zPos = int(self.posZ - self.art.sizeX / 32.0)
        if self.direction == 2:
            xPos = int(self.posX - self.art.sizeX / 32.0)
        if self.direction == 3:
            zPos = int(self.posZ - self.art.sizeX / 32.0)

        yPos = int(self.posY - self.art.sizeY / 32.0)
        for x in range(sizeX):
            for y in range(sizeY):
                if self.direction != 0 and self.direction != 2:
                    material = self._worldObj.getBlockMaterial(
                        self.__xPosition, yPos + y, zPos + x
                    )
                else:
                    material = self._worldObj.getBlockMaterial(
                        xPos + x, yPos + y, self.__zPosition
                    )

                if not material.isSolid():
                    return False

        entities = self._worldObj.entityMap.getEntitiesWithinAABB(self, self.boundingBox)
        for entity in entities:
            if isinstance(entity, EntityPainting):
                return False

        return True

    def canBeCollidedWith(self):
        return True

    def attackEntityFrom(self, entity, damage):
        self.setEntityDead()
        self._worldObj.spawnEntityInWorld(EntityItem(self._worldObj, self.posX,
                                                     self.posY, self.posZ,
                                                     ItemStack(items.painting)))
        return True

    def _writeEntityToNBT(self, compound):
        compound['Dir'] = Byte(self.direction)
        compound['Motive'] = String(self.art.title)
        compound['TileX'] = Int(self.__xPosition)
        compound['TileY'] = Int(self.__yPosition)
        compound['TileZ'] = Int(self.__zPosition)

    def _getEntityString(self):
        return 'Painting'

    def _readEntityFromNBT(self, compound):
        self.direction = compound.get('Dir', Byte(0)).real
        self.__xPosition = compound.get('TileX', Int(0)).real
        self.__yPosition = compound.get('TileY', Int(0)).real
        self.__zPosition = compound.get('TileZ', Int(0)).real
        motive = str(compound.get('Motive', ''))
        for art in EnumArt:
            if art.title == motive:
                self.art = art

        if not self.art:
            self.art = EnumArt.Kebab

        self.setDirection(self.direction)
