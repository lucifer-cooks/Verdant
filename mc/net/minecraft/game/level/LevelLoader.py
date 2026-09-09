from mc.net.minecraft.client.LoadingScreenRenderer import LoadingScreenRenderer
from mc.net.minecraft.game.entity.EntityPainting import EntityPainting
from mc.net.minecraft.game.entity.animal.EntityPig import EntityPig
from mc.net.minecraft.game.entity.animal.EntitySheep import EntitySheep
from mc.net.minecraft.game.entity.misc.EntityItem import EntityItem
from mc.net.minecraft.game.entity.monster.EntityCreeper import EntityCreeper
from mc.net.minecraft.game.entity.monster.EntityGiantZombie import EntityGiantZombie
from mc.net.minecraft.game.entity.monster.EntitySkeleton import EntitySkeleton
from mc.net.minecraft.game.entity.monster.EntitySpider import EntitySpider
from mc.net.minecraft.game.entity.monster.EntityZombie import EntityZombie
from mc.net.minecraft.game.level.block.tileentity.TileEntityChest import TileEntityChest
from mc.net.minecraft.game.level.block.tileentity.TileEntityFurnace import TileEntityFurnace
from mc.net.minecraft.game.level.block.Blocks import blocks
from mc.net.minecraft.game.level.World import World

from nbtlib import File
from nbtlib.tag import Compound, ByteArray, List, String, Byte, Short, Long, Int

import traceback

class LevelLoader:

    def __init__(self, loadingScreen):
        self.__guiLoading = loadingScreen

    def load(self, file):
        if self.__guiLoading:
            self.__guiLoading.displayProgressMessage('Loading level')
            self.__guiLoading.displayLoadingString('Reading..')

        levelTag = LoadingScreenRenderer.writeLevelTags(file)
        aboutTag = levelTag.get('About', Compound({}))
        mapTag = levelTag.get('Map', Compound({}))
        environmentTag = levelTag.get('Environment', Compound({}))
        entityTag = levelTag.get('Entities', List[Compound]())
        width = mapTag.get('Width', Short(0)).real
        length = mapTag.get('Length', Short(0)).real
        height = mapTag.get('Height', Short(0)).real
        world = World()
        if self.__guiLoading:
            self.__guiLoading.displayLoadingString('Preparing level..')

        spawnTag = mapTag.get('Spawn', List[Short]([Short(0), Short(0), Short(0)]))
        world.xSpawn = spawnTag[0].real
        world.ySpawn = spawnTag[1].real
        world.zSpawn = spawnTag[2].real
        world.authorName = str(aboutTag.get('Author', ''))
        world.name = str(aboutTag.get('Name', ''))
        world.createTime = aboutTag.get('CreatedOn', Long(0)).real
        world.cloudColor = environmentTag.get('CloudColor', Int(0)).real
        world.skyColor = environmentTag.get('SkyColor', Int(0)).real
        world.fogColor = environmentTag.get('FogColor', Int(0)).real
        world.skyBrightness = max(environmentTag.get('SkyBrightness', Byte(0)).real, 0)
        if world.skyBrightness > 16:
            world.skyBrightness = world.skyBrightness * 15 // 100

        world.cloudHeight = environmentTag.get('CloudHeight', Short(0)).real
        world.groundLevel = environmentTag.get('SurroundingGroundHeight', Short(0)).real
        world.waterLevel = environmentTag.get('SurroundingWaterHeight', Short(0)).real
        world.defaultFluid = environmentTag.get('SurroundingWaterType', Byte(0)).real
        world.worldTime = environmentTag.get('TimeOfDay', Short(0)).real
        world.skylightSubtracted = world.getSkyBrightness()
        world.generate(width, height, length, bytearray(mapTag['Blocks']),
                       bytearray(mapTag['Data']))
        if self.__guiLoading:
            self.__guiLoading.displayLoadingString('Preparing entities..')

        for compound in entityTag:
            try:
                entityType = str(compound.get('id', ''))
                entity = self._loadEntity(world, entityType)
                if entity:
                    entity.readFromNBT(compound)
                    world.spawnEntityInWorld(entity)
                else:
                    print(f'Skipping unknown entity id "{entityType}"')
            except Exception as e:
                print('Error reading entity')
                print(traceback.format_exc())

        tileTag = levelTag.get('TileEntities', List[Compound]())
        for compound in tileTag:
            try:
                pos = compound.get('Pos', Int(0)).real
                entityType = str(compound.get('id', ''))
                entity = None
                if entityType == 'Chest':
                    entity = TileEntityChest()
                elif entityType == 'Furnace':
                    entity = TileEntityFurnace()

                if entity:
                    x = pos % 1024
                    y = (pos >> 10) % 1024
                    z = (pos >> 20) % 1024
                    entity.readFromNBT(compound)
                    world.setBlockTileEntity(x, y, z, entity)
                else:
                    print(f'Skipping unknown tile entity id "{entityType}"')
            except Exception as e:
                print('Error reading tileentity')
                print(traceback.format_exc())

        return world

    def _loadEntity(self, world, entityId):
        if entityId == 'Pig':
            return EntityPig(world)
        elif entityId == 'Sheep':
            return EntitySheep(world)
        elif entityId == 'Creeper':
            return EntityCreeper(world)
        elif entityId == 'Skeleton':
            return EntitySkeleton(world)
        elif entityId == 'Spider':
            return EntitySpider(world)
        elif entityId == 'Zombie':
            return EntityZombie(world)
        elif entityId == 'Giant':
            return EntityGiantZombie(world)
        elif entityId == 'Item':
            return EntityItem(world)
        elif entityId == 'Painting':
            return EntityPainting(world)

    def save(self, world, file):
        if self.__guiLoading:
            self.__guiLoading.displayProgressMessage('Saving level')
            self.__guiLoading.displayLoadingString('Preparing level..')

        environmentTag = Compound({'CloudColor': Int(world.cloudColor),
                                   'SkyColor': Int(world.skyColor),
                                   'FogColor': Int(world.fogColor),
                                   'SkyBrightness': Byte(world.skyBrightness),
                                   'CloudHeight': Short(world.cloudHeight),
                                   'SurroundingGroundHeight': Short(world.groundLevel),
                                   'SurroundingWaterHeight': Short(world.waterLevel),
                                   'SurroundingGroundType': Byte(blocks.grass.blockID),
                                   'SurroundingWaterType': Byte(world.defaultFluid),
                                   'TimeOfDay': Short(world.worldTime)})
        mapTag = Compound({'Width': Short(world.width), 'Length': Short(world.length),
                           'Height': Short(world.height),
                           'Blocks': ByteArray(world.getBlocks()),
                           'Data': ByteArray(world.getData())})
        posTag = List[Short]([Short(world.xSpawn), Short(world.ySpawn),
                              Short(world.zSpawn)])
        mapTag['Spawn'] = posTag
        aboutTag = Compound({'Author': String(world.authorName),
                             'Name': String(world.name),
                             'CreatedOn': Long(world.createTime)})

        if self.__guiLoading:
            self.__guiLoading.displayLoadingString('Preparing entities..')

        entityTag = List[Compound]()
        for entity in world.entityMap.all:
            compound = Compound()
            entity.writeToNBT(compound)
            if compound:
                entityTag.append(compound)

        tileTag = List[Compound]()
        for pos, entity in world.map.items():
            compound = Compound({'Pos': Int(pos)})
            entity.writeToNBT(compound)
            tileTag.append(compound)

        levelTag = Compound({'About': aboutTag, 'Map': mapTag,
                             'Environment': environmentTag, 'Entities': entityTag,
                             'TileEntities': tileTag})

        if self.__guiLoading:
            self.__guiLoading.displayLoadingString('Writing..')

        f = File(levelTag, gzipped=True)
        f.save(file)
