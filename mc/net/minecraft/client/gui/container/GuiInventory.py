from mc.net.minecraft.client.render.entity.RenderManager import RenderManager
from mc.net.minecraft.client.render.RenderEngine import RenderEngine
from mc.net.minecraft.client.RenderHelper import RenderHelper
from mc.net.minecraft.client.gui.container.InventoryCraftResult import InventoryCraftResult
from mc.net.minecraft.client.gui.container.InventoryCrafting import InventoryCrafting
from mc.net.minecraft.client.gui.container.GuiContainer import GuiContainer
from mc.net.minecraft.client.gui.container.Slot import Slot
from mc.net.minecraft.client.gui.container.SlotArmor import SlotArmor
from mc.net.minecraft.client.gui.container.SlotCrafting import SlotCrafting
from mc.net.minecraft.game.item.recipe.CraftingManager import CraftingManager
from pyglet import gl

import math

class GuiInventory(GuiContainer):

    def __init__(self, inventory):
        super().__init__()
        self.__inventoryCrafting = InventoryCrafting(self, 2, 2)
        self.__craftResult = InventoryCraftResult()
        self.__xSize_lo = 0.0
        self.__ySize_lo = 0.0

        self.allowUserInput = True

        self._inventorySlots.append(SlotCrafting(
                self, self.__inventoryCrafting, self.__craftResult, 0, 144, 36
            ))
        for row in range(2):
            for col in range(2):
                self._inventorySlots.append(Slot(
                        self, self.__inventoryCrafting, col + (row << 1),
                        88 + col * 18, 26 + row * 18
                    ))

        for armorSlot in range(4):
            self._inventorySlots.append(SlotArmor(
                    self, self, inventory, inventory.getSizeInventory() - 1 - armorSlot,
                    8, 8 + armorSlot * 18, armorSlot
                ))

        for row in range(3):
            for col in range(9):
                self._inventorySlots.append(Slot(
                        self, inventory, col + (row + 1) * 9,
                        8 + col * 18, 84 + row * 18
                    ))

        for barSlots in range(9):
            self._inventorySlots.append(Slot(self, inventory, barSlots,
                                             8 + barSlots * 18, 142))

    def onGuiClosed(self):
        super().onGuiClosed()
        for i in range(self.__inventoryCrafting.getSizeInventory()):
            stack = self.__inventoryCrafting.getStackInSlot(i)
            if stack:
                self.mc.thePlayer.dropPlayerItem(stack)

    def guiCraftingItemsCheck(self):
        items = [0] * 9
        for row in range(3):
            for col in range(3):
                slot = -1
                if row < 2 and col < 2:
                    stack = self.__inventoryCrafting.getStackInSlot(row + (col << 1))
                    if stack:
                        slot = stack.itemID

                items[row + col * 3] = slot

        self.__craftResult.setInventorySlotContents(
            0, CraftingManager.getInstance().findMatchingRecipe(items)
        )

    def _drawGuiContainerForegroundLayer(self):
        self._fontRenderer.drawString('Crafting', 86, 16, 4210752)

    def drawScreen(self, xm, ym, renderPartialTicks):
        super().drawScreen(xm, ym, renderPartialTicks)
        self.__xSize_lo = xm
        self.__ySize_lo = ym

    def _drawGuiContainerBackgroundLayer(self):
        tex = self.mc.renderEngine.getTexture('gui/inventory.png')
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)
        RenderEngine.bindTexture(tex)
        w = (self.width - self.xSize) // 2
        h = (self.height - self.ySize) // 2
        self.drawTexturedModalRect(w, h, 0, 0, self.xSize, self.ySize)
        gl.glEnable(gl.GL_NORMALIZE)
        gl.glEnable(gl.GL_COLOR_MATERIAL)
        gl.glPushMatrix()
        gl.glTranslatef(w + 51, h + 75, 50.0)
        gl.glScalef(-30.0, 30.0, 30.0)
        gl.glRotatef(180.0, 0.0, 0.0, 1.0)
        prevRenderYawOffset = self.mc.thePlayer.renderYawOffset
        prevRotationYaw = self.mc.thePlayer.rotationYaw
        prevRotationPitch = self.mc.thePlayer.rotationPitch
        x = (w + 51) - self.__xSize_lo
        y = (h + 75 - 50) - self.__ySize_lo
        gl.glRotatef(135.0, 0.0, 1.0, 0.0)
        RenderHelper.enableStandardItemLighting()
        gl.glRotatef(-135.0, 0.0, 1.0, 0.0)
        gl.glRotatef(-(math.atan(y / 40.0)) * 20.0, 1.0, 0.0, 0.0)
        self.mc.thePlayer.renderYawOffset = (math.atan(x / 40.0)) * 20.0
        self.mc.thePlayer.rotationYaw = (math.atan(x / 40.0)) * 40.0
        self.mc.thePlayer.rotationPitch = -(math.atan(y / 40.0)) * 20.0
        gl.glTranslatef(0.0, self.mc.thePlayer.yOffset, 0.0)
        RenderManager.instance.renderEntityWithPosYaw(
            self.mc.thePlayer, 0.0, 0.0, 0.0, 0.0, 1.0
        )
        self.mc.thePlayer.renderYawOffset = prevRenderYawOffset
        self.mc.thePlayer.rotationYaw = prevRotationYaw
        self.mc.thePlayer.rotationPitch = prevRotationPitch
        gl.glPopMatrix()
        RenderHelper.disableStandardItemLighting()
        gl.glDisable(gl.GL_NORMALIZE)
