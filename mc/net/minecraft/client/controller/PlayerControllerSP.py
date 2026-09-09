from mc.net.minecraft.client.controller.PlayerController import PlayerController
from mc.net.minecraft.game.level.MobSpawner import MobSpawner
from mc.net.minecraft.game.level.block.Blocks import blocks
from mc.net.minecraft.game.entity.EntityLiving import EntityLiving
from mc.net.minecraft.game.item.ItemStack import ItemStack
from mc.net.minecraft.game.item.Items import items

class PlayerControllerSP(PlayerController):

    def __init__(self, mc):
        super().__init__(mc)
        self.__curBlockX = -1
        self.__curBlockY = -1
        self.__curBlockZ = -1
        self.__curBlockDamage = 0.0
        self.__prevBlockDamage = 0.0
        self.__blockDestroySoundCounter = 0.0
        self.__blockHitWait = 0
        self.__mobSpawner = None

    def sendBlockRemoved(self, x, y, z):
        block = self._mc.theWorld.getBlockId(x, y, z)
        metadata = self._mc.theWorld.getBlockMetadata(x, y, z)
        change = super().sendBlockRemoved(x, y, z)
        stack = self._mc.thePlayer.inventory.getCurrentItem()
        if stack:
            items.itemsList[stack.itemID].onBlockDestroyed(stack)
            if stack.stackSize == 0:
                self._mc.thePlayer.destroyCurrentEquippedItem()
        if change and self._mc.thePlayer.canHarvestBlock(blocks.blocksList[block]):
            blocks.blocksList[block].dropBlockAsItem(self._mc.theWorld, x, y, z, metadata)

        return change

    def clickBlock(self, x, y, z):
        block = self._mc.theWorld.getBlockId(x, y, z)
        if block > 0 and blocks.blocksList[block].blockStrength(self._mc.thePlayer) >= 1.0:
            self.sendBlockRemoved(x, y, z)

    def resetBlockRemoving(self):
        self.__curBlockDamage = 0.0
        self.__blockHitWait = 0

    def sendBlockRemoving(self, x, y, z, sideHit):
        if self.__blockHitWait > 0:
            self.__blockHitWait -= 1
            return

        super().sendBlockRemoving(x, y, z, sideHit)
        if x == self.__curBlockX and y == self.__curBlockY and z == self.__curBlockZ:
            block = self._mc.theWorld.getBlockId(x, y, z)
            if block == 0:
                return

            block = blocks.blocksList[block]
            self.__curBlockDamage += block.blockStrength(self._mc.thePlayer)
            if self.__blockDestroySoundCounter % 4.0 == 0.0 and block:
                speed = (block.stepSound.soundVolume + 1.0) / 8.0
                self._mc.sndManager.playSound(
                    block.stepSound.stepSoundDirStep(), x + 0.5, y + 0.5, z + 0.5,
                    speed, block.stepSound.soundPitch * 0.5
                )

            self.__blockDestroySoundCounter += 1
            if self.__curBlockDamage >= 1.0:
                self.sendBlockRemoved(x, y, z)
                self.__curBlockDamage = 0.0
                self.__prevBlockDamage = 0.0
                self.__blockDestroySoundCounter = 0.0
                self.__blockHitWait = 5
        else:
            self.__curBlockDamage = 0.0
            self.__prevBlockDamage = 0.0
            self.__blockDestroySoundCounter = 0.0
            self.__curBlockX = x
            self.__curBlockY = y
            self.__curBlockZ = z

    def setPartialTime(self, damageTime):
        if self.__curBlockDamage <= 0.0:
            self._mc.renderGlobal.damagePartialTime = 0.0
        else:
            self._mc.renderGlobal.damagePartialTime = self.__prevBlockDamage + \
                (self.__curBlockDamage - self.__prevBlockDamage) * damageTime

    def getBlockReachDistance(self):
        return 4.0

    def onWorldChange(self, world):
        super().onWorldChange(world)
        self.__mobSpawner = MobSpawner(world)

    def onUpdate(self):
        self.__prevBlockDamage = self.__curBlockDamage
        self.__mobSpawner.performSpawning()
