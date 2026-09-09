from mc.net.minecraft.game.entity.EntityLiving import EntityLiving
from mc.net.minecraft.game.entity.animal.EntityAnimal import EntityAnimal
from mc.net.minecraft.game.entity.animal.EntityPig import EntityPig
from mc.net.minecraft.game.entity.animal.EntitySheep import EntitySheep
from mc.net.minecraft.game.entity.monster.EntityCreeper import EntityCreeper
from mc.net.minecraft.game.entity.monster.EntitySkeleton import EntitySkeleton
from mc.net.minecraft.game.entity.monster.EntitySpider import EntitySpider
from mc.net.minecraft.game.entity.monster.EntityZombie import EntityZombie
from mc.net.minecraft.game.entity.monster.EntityMob import EntityMob
from mc.JavaUtils import random

class MobSpawner:

    def __init__(self, world):
        self.__worldObj = world

    def performSpawning(self):
        mobSize = self.__worldObj.width * self.__worldObj.length * \
               self.__worldObj.height * 20 // 64 // 64 // 64
        mobSize //= 2
        if self.__worldObj.difficultySetting == 0:
            mobSize = 0 // 4
        elif self.__worldObj.difficultySetting == 1:
            mobSize = mobSize * 3 // 4
        elif self.__worldObj.difficultySetting == 2:
            mobSize = (mobSize << 2) // 4
        elif self.__worldObj.difficultySetting == 3:
            mobSize = mobSize * 6 // 4

        animalSize = self.__worldObj.width * self.__worldObj.length // 4000
        totalMobs = self.__worldObj.entitiesInLevelList(EntityMob)
        for i in range(4):
            if totalMobs >= mobSize:
                break

            mobs = 0
            choice = self.__worldObj.rand.nextInt(5)
            blockX = self.__worldObj.rand.nextInt(self.__worldObj.width)
            blockY = int(min(self.__worldObj.rand.nextFloat(),
                             self.__worldObj.rand.nextFloat()) * self.__worldObj.height)
            blockZ = self.__worldObj.rand.nextInt(self.__worldObj.length)
            for j in range(2):
                xx = blockX
                yy = blockY
                zz = blockZ
                for k in range(3):
                    xx += self.__worldObj.rand.nextInt(6) - self.__worldObj.rand.nextInt(6)
                    yy += self.__worldObj.rand.nextInt(1) - self.__worldObj.rand.nextInt(1)
                    zz += self.__worldObj.rand.nextInt(6) - self.__worldObj.rand.nextInt(6)
                    if xx >= 0 and zz > 0 and yy >= 0 and \
                       yy < self.__worldObj.height - 2 and \
                       xx < self.__worldObj.width and zz < self.__worldObj.length:
                        x = xx + 0.5
                        y = yy + 0.5
                        z = zz + 0.5
                        if self.__worldObj.playerEntity:
                            xd = x - self.__worldObj.playerEntity.posX
                            yd = y - self.__worldObj.playerEntity.posY
                            zd = z - self.__worldObj.playerEntity.posZ
                        else:
                            xd = x - self.__worldObj.xSpawn
                            yd = y - self.__worldObj.ySpawn
                            zd = z - self.__worldObj.zSpawn

                        if xd * xd + yd * yd + zd * zd < 1024.0:
                            continue

                        mob = None
                        if choice == 0:
                            mob = EntitySkeleton(self.__worldObj)
                        elif choice == 1:
                            mob = EntityCreeper(self.__worldObj)
                        elif choice == 2:
                            mob = EntitySpider(self.__worldObj)
                        elif choice == 3:
                            mob = EntityZombie(self.__worldObj)

                        if isinstance(mob, EntityMob) and self.__worldObj.difficultySetting == 0:
                            mob = None

                        if not mob or self.__worldObj.isBlockNormalCube(xx, yy, zz) or \
                           not self.__worldObj.isBlockNormalCube(xx, yy - 1, zz) or \
                           not mob.getCanSpawnHere(x, y, z):
                            continue

                        yaw = self.__worldObj.rand.nextFloat() * 360.0
                        mob.setPositionAndRotation(x, y, z, yaw, 0.0)
                        mobs += 1
                        self.__worldObj.spawnEntityInWorld(mob)

            totalMobs += mobs

        totalAnimals = self.__worldObj.entitiesInLevelList(EntityAnimal)
        for i in range(4):
            if totalAnimals >= animalSize:
                break

            animals = 0
            choice = self.__worldObj.rand.nextInt(2)
            blockX = self.__worldObj.rand.nextInt(self.__worldObj.width)
            blockY = self.__worldObj.rand.nextInt(self.__worldObj.height)
            blockZ = self.__worldObj.rand.nextInt(self.__worldObj.length)
            for j in range(4):
                xx = blockX
                yy = blockY
                zz = blockZ
                for k in range(3):
                    xx += self.__worldObj.rand.nextInt(6) - self.__worldObj.rand.nextInt(6)
                    yy += self.__worldObj.rand.nextInt(1) - self.__worldObj.rand.nextInt(1)
                    zz += self.__worldObj.rand.nextInt(6) - self.__worldObj.rand.nextInt(6)
                    if xx >= 0 and zz > 0 and yy >= 0 and \
                       yy < self.__worldObj.height - 2 and \
                       xx < self.__worldObj.width and zz < self.__worldObj.length:
                        x = xx + 0.5
                        y = yy + 0.5
                        z = zz + 0.5
                        if self.__worldObj.playerEntity:
                            xd = x - self.__worldObj.playerEntity.posX
                            yd = y - self.__worldObj.playerEntity.posY
                            zd = z - self.__worldObj.playerEntity.posZ
                        else:
                            xd = x - self.__worldObj.xSpawn
                            yd = y - self.__worldObj.ySpawn
                            zd = z - self.__worldObj.zSpawn

                        if xd * xd + yd * yd + zd * zd < 1024.0:
                            continue

                        animal = None
                        if choice == 0:
                            animal = EntityPig(self.__worldObj)
                        elif choice == 1:
                            animal = EntitySheep(self.__worldObj)

                        if not animal or self.__worldObj.isBlockNormalCube(xx, yy, zz) or \
                           not self.__worldObj.isBlockNormalCube(xx, yy - 1, zz) or \
                           not animal.getCanSpawnHere(x, y, z):
                            continue

                        yaw = self.__worldObj.rand.nextFloat() * 360.0
                        animal.setPositionAndRotation(x, y, z, yaw, 0.0)
                        animals += 1
                        self.__worldObj.spawnEntityInWorld(animal)

            totalAnimals += animals
