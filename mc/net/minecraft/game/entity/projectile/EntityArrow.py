from mc.net.minecraft.game.entity.Entity import Entity
from mc.net.minecraft.game.physics.Vec3D import Vec3D
from mc.net.minecraft.game.physics.MovingObjectPosition import MovingObjectPosition

from nbtlib.tag import Short, Byte

import math

class EntityArrow(Entity):

    def __init__(self, world, entity):
        super().__init__(world)
        self.__owner = entity
        self.__xTile = -1
        self.__yTile = -1
        self.__zTile = -1
        self.__inTile = 0
        self.__inGround = False
        self.arrowShake = 0
        self.__ticksInAir = 0
        self.setSize(0.5, 0.5)
        self.setPositionAndRotation(entity.posX, entity.posY, entity.posZ,
                                    entity.rotationYaw, entity.rotationPitch)
        self.posX -= math.cos(self.rotationYaw / 180.0 * math.pi) * 0.16
        self.posY -= 0.1
        self.posZ -= math.sin(self.rotationYaw / 180.0 * math.pi) * 0.16
        self.setPosition(self.posX, self.posY, self.posZ)
        self.yOffset = 0.0
        self.motionX = -math.sin(self.rotationYaw / 180.0 * math.pi) * \
                       math.cos(self.rotationPitch / 180.0 * math.pi)
        self.motionZ = math.cos(self.rotationYaw / 180.0 * math.pi) * \
                       math.cos(self.rotationPitch / 180.0 * math.pi)
        self.motionY = -math.sin(self.rotationPitch / 180.0 * math.pi)
        self.setArrowHeading(self.motionX, self.motionY, self.motionZ, 1.5, 1.0)

    def setArrowHeading(self, x, y, z, yaw, pitch):
        d = math.sqrt(x * x + y * y + z * z)
        x /= d
        y /= d
        z /= d
        x += self._rand.nextGaussian() * 0.0075 * pitch
        y += self._rand.nextGaussian() * 0.0075 * pitch
        z += self._rand.nextGaussian() * 0.0075 * pitch
        x *= yaw
        y *= yaw
        z *= yaw
        self.motionX = x
        self.motionY = y
        self.motionZ = z
        d = math.sqrt(x * x + z * z)
        self.prevRotationYaw = self.rotationYaw = math.atan2(x, z) * 180.0 / math.pi
        self.prevRotationPitch = self.rotationPitch = math.atan2(y, d) * 180.0 / math.pi
        self.__ticksInGround = 0

    def onEntityUpdate(self):
        super().onEntityUpdate()
        if self.arrowShake > 0:
            self.arrowShake -= 1

        if self.__inGround:
            blockId = self._worldObj.getBlockId(self.__xTile, self.__yTile, self.__zTile)
            if blockId == self.__inTile:
                self.__ticksInGround += 1
                if self.__ticksInGround == 1200:
                    self.setEntityDead()

                return

            self.__inGround = False
            self.motionX *= self._rand.nextFloat() * 0.2
            self.motionY *= self._rand.nextFloat() * 0.2
            self.motionZ *= self._rand.nextFloat() * 0.2
            self.__ticksInGround = 0
            self.__ticksInAir = 0
        else:
            self.__ticksInAir += 1

        posVec = Vec3D(self.posX, self.posY, self.posZ)
        motionVec = Vec3D(self.posX + self.motionX, self.posY + self.motionY,
                          self.posZ + self.motionZ)
        hit = self._worldObj.rayTraceBlocks(posVec, motionVec)
        posVec = Vec3D(self.posX, self.posY, self.posZ);
        motionVec = Vec3D(self.posX + self.motionX, self.posY + self.motionY,
                          self.posZ + self.motionZ)
        if hit:
            motionVec = Vec3D(hit.hitVec.xCoord, hit.hitVec.yCoord, hit.hitVec.zCoord)

        target = None
        entities = self._worldObj.entityMap.getEntitiesWithinAABB(
            self, self.boundingBox.addCoord(self.motionX, self.motionY,
                                            self.motionZ).expand(1.0, 1.0, 1.0)
        )
        distance = 0.0
        for entity in entities:
            if entity.canBeCollidedWith() and (entity != self.__owner or \
                                               self.__ticksInAir >= 5):
                box = entity.boundingBox.expand(0.3, 0.3, 0.3);
                eHit = box.calculateIntercept(posVec, motionVec);
                if eHit:
                    d = posVec.distanceTo(eHit.hitVec)
                    if d < distance or distance == 0.0:
                        target = entity
                        distance = d

        if target:
            hit = MovingObjectPosition(target)

        if hit:
            if hit.entityHit:
                if hit.entityHit.attackEntityFrom(self, 4):
                    self._worldObj.playSoundAtEntity(
                        self, 'random.drr', 1.0,
                        1.2 / (self._rand.nextFloat() * 0.2 + 0.9)
                    )
                    self.setEntityDead()
                else:
                    self.motionX *= -0.1
                    self.motionY *= -0.1
                    self.motionZ *= -0.1
                    self.rotationYaw += 180.0
                    self.prevRotationYaw += 180.0
                    self.__ticksInAir = 0
            else:
                self.__xTile = hit.blockX
                self.__yTile = hit.blockY
                self.__zTile = hit.blockZ
                self.__inTile = self._worldObj.getBlockId(self.__xTile, self.__yTile,
                                                          self.__zTile)
                self.motionX = hit.hitVec.xCoord - self.posX
                self.motionY = hit.hitVec.yCoord - self.posY
                self.motionZ = hit.hitVec.zCoord - self.posZ
                d = math.sqrt(self.motionX * self.motionX + \
                              self.motionY * self.motionY + \
                              self.motionZ * self.motionZ)
                self.posX -= self.motionX / d * 0.05
                self.posY -= self.motionY / d * 0.05
                self.posZ -= self.motionZ / d * 0.05
                self._worldObj.playSoundAtEntity(
                    self, 'random.drr', 1.0,
                    1.2 / (self._rand.nextFloat() * 0.2 + 0.9)
                )
                self.__inGround = True
                self.arrowShake = 7

        self.posX += self.motionX
        self.posY += self.motionY
        self.posZ += self.motionZ
        d = math.sqrt(self.motionX * self.motionX + self.motionZ * self.motionZ)
        self.rotationYaw = math.atan2(self.motionX, self.motionZ) * 180.0 / math.pi
        self.rotationPitch = math.atan2(self.motionY, d) * 180.0 / (math.pi)
        while self.rotationPitch < -180.0:
            self.rotationPitch -= -360.0

        while self.rotationPitch - self.prevRotationPitch >= 180.0:
            self.prevRotationPitch += 360.0

        while self.rotationYaw - self.prevRotationYaw < -180.0:
            self.prevRotationYaw -= 360.0

        while self.rotationYaw - self.prevRotationYaw >= 180.0:
            self.prevRotationYaw += 360.0

        self.rotationPitch = self.prevRotationPitch + (self.rotationPitch - self.prevRotationPitch) * 0.2
        self.rotationYaw = self.prevRotationYaw + (self.rotationYaw - self.prevRotationYaw) * 0.2
        motion = 0.99
        if self.handleWaterMovement():
            for i in range(4):
                self._worldObj.spawnParticle(
                    'bubble', self.posX - self.motionX * 0.25,
                    self.posY - self.motionY * 0.25,
                    self.posZ - self.motionZ * 0.25,
                    self.motionX, self.motionY, self.motionZ
                )

            motion = 0.8

        self.motionX *= motion
        self.motionY *= motion
        self.motionZ *= motion
        self.motionY -= 0.03
        self.setPosition(self.posX, self.posY, self.posZ)

    def _writeEntityToNBT(self, compound):
        compound['xTile'] = Short(self.__xTile)
        compound['yTile'] = Short(self.__yTile)
        compound['zTile'] = Short(self.__zTile)
        compound['inTile'] = Byte(self.__inTile)
        compound['shake'] = Byte(self.arrowShake)
        compound['inGround'] = Byte(1 if self.__inGround else 0)

    def _readEntityFromNBT(self, compound):
        self.__xTile = compound.get('xTile', Short(-1)).real
        self.__yTile = compound.get('yTile', Short(-1)).real
        self.__zTile = compound.get('zTile', Short(-1)).real
        self.__inTile = compound.get('inTile', Byte(0)).real & 255
        self.arrowShake = compound.get('shake', Byte(0)).real & 255
        self.__inGround = compound.get('inGround', Byte(False)).real == 1

    def _getEntityString(self):
        return 'Arrow'

    def onCollideWithPlayer(self, player):
        from mc.net.minecraft.game.item.Items import items
        from mc.net.minecraft.game.item.ItemStack import ItemStack
        if self.__inGround and self.__owner == player and self.arrowShake <= 0 and \
           player.inventory.addItemStackToInventory(ItemStack(items.arrow.shiftedIndex, 1)):
            self._worldObj.playSoundAtEntity(
                self, 'random.pop', 0.2,
                ((self._rand.nextFloat() - self._rand.nextFloat()) * 0.7 + 1.0) * 2.0
            )
            player.onItemPickup(self)
            self.setEntityDead()

    def getShadowSize(self):
        return 0.0
