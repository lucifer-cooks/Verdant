# cython: language_level=3

from libc.math cimport sqrt, atan2, pi

from mc.net.minecraft.game.entity.Entity cimport Entity
from mc.net.minecraft.game.entity.EntityLiving cimport EntityLiving
from mc.net.minecraft.game.level.World cimport World
from mc.net.minecraft.game.physics.Vec3D import Vec3D

cdef class EntityCreature(EntityLiving):

    cdef:
        object __pathToEntity
        public Entity _playerToAttack
        public bint _hasAttacked

    def __init__(self, World world):
        super().__init__(world)
        self.__pathToEntity = None
        self._playerToAttack = None
        self._hasAttacked = False

    def _updatePlayerActionState(self):
        cdef int toX, toY, toZ, i, posX, posY, posZ
        cdef float xd, yd, zd, d, lastWeight, weight, w, x, y, z
        cdef bint isInWater, isInLava

        self._hasAttacked = False
        if not self._playerToAttack:
            self._playerToAttack = self._findPlayerToAttack()
            if self._playerToAttack:
                self.__pathToEntity = self._worldObj.pathFinder.createEntityPathTo(
                    self, self._playerToAttack, 16.0
                )
        elif not self._playerToAttack.isEntityAlive():
            self._playerToAttack = None
        else:
            xd = self._playerToAttack.posX - self.posX
            yd = self._playerToAttack.posY - self.posY
            zd = self._playerToAttack.posZ - self.posZ
            d = sqrt(xd * xd + yd * yd + zd * zd)
            if not self._worldObj.rayTraceBlocks(Vec3D(self.posX,
                                                       self.posY + self._getEyeHeight(),
                                                       self.posZ),
                                                 Vec3D(self._playerToAttack.posX,
                                                       self._playerToAttack.posY + self._playerToAttack._getEyeHeight(),
                                                       self._playerToAttack.posZ)):
                self._attackEntity(self._playerToAttack, d)

        if self._hasAttacked:
            self._moveStrafing = 0.0
            self._moveForward = 0.0
            self._isJumping = False
            return

        if not self._playerToAttack or self.__pathToEntity and \
             self._rand.nextInt(20) != 0:
            if not self.__pathToEntity or self._rand.nextInt(100) == 0:
                toX = -1
                toY = -1
                toZ = -1
                lastWeight = -99999.0
                for i in range(200):
                    posX = <int>(self.posX + self._rand.nextInt(21) - 10.0)
                    posY = <int>(self.posY + self._rand.nextInt(9) - 4.0)
                    posZ = <int>(self.posZ + self._rand.nextInt(21) - 10.0)
                    weight = self._getBlockPathWeight(posX, posY, posZ)
                    if weight > lastWeight:
                        lastWeight = weight
                        toX = posX
                        toY = posY
                        toZ = posZ

                if toX > 0:
                    self.__pathToEntity = self._worldObj.pathFinder.createEntityPath(
                        self, toX, toY, toZ, 16.0
                    )
        else:
            self.__pathToEntity = self._worldObj.pathFinder.createEntityPathTo(
                self, self._playerToAttack, 16.0
            )

        isInWater = self.handleWaterMovement()
        isInLava = self.handleLavaMovement()
        if self.__pathToEntity and self._rand.nextInt(100) != 0:
            posVec = self.__pathToEntity.getPosition(self)
            w = self.width * 2.0
            while posVec:
                z = self.posZ
                y = self.posY
                x = self.posX
                x -= posVec.xCoord
                y -= posVec.yCoord
                z -= posVec.zCoord
                if x * x + y * y + z * z >= w * w or posVec.yCoord > self.posY:
                    break

                self.__pathToEntity.incrementPathIndex()
                if self.__pathToEntity.isFinished():
                    posVec = None
                    self.__pathToEntity = None
                else:
                    posVec = self.__pathToEntity.getPosition(self)

            self._isJumping = False
            if posVec:
                xd = posVec.xCoord - self.posX
                yd = posVec.yCoord - self.posY
                zd = posVec.zCoord - self.posZ
                self.rotationYaw = (atan2(zd, xd) * 180.0 / pi) - 90.0
                self._moveForward = self._moveSpeed
                if yd > 0.0:
                    self._isJumping = True

            if self._rand.nextFloat() < 0.8 and (isInWater or isInLava):
                self._isJumping = True
        else:
            super()._updatePlayerActionState()
            self.__pathToEntity = None

    def _attackEntity(self, Entity entity, float distance):
        pass

    def _getBlockPathWeight(self, int x, int y, int z):
        return 0.0

    def _findPlayerToAttack(self):
        return None

    def getCanSpawnHere(self, float x, float y, float z):
        return super().getCanSpawnHere(x, y, z) and \
               self._getBlockPathWeight(<int>x, <int>y, <int>z) >= 0.0
