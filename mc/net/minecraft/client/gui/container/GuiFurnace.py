from mc.net.minecraft.client.gui.container.GuiContainer import GuiContainer
from mc.net.minecraft.client.gui.container.Slot import Slot
from mc.net.minecraft.client.render.RenderEngine import RenderEngine
from pyglet import gl

class GuiFurnace(GuiContainer):

    def __init__(self, inventory, furnaceInventory):
        super().__init__()
        self.__furnaceInventory = furnaceInventory
        self._inventorySlots.append(Slot(self, furnaceInventory, 0, 56, 17))
        self._inventorySlots.append(Slot(self, furnaceInventory, 1, 56, 53))
        self._inventorySlots.append(Slot(self, furnaceInventory, 2, 116, 35))
        for row in range(3):
            for col in range(9):
                self._inventorySlots.append(Slot(self, inventory, col + (row + 1) * 9,
                                            8 + col * 18, 84 + row * 18))
        for row in range(9):
            self._inventorySlots.append(Slot(self, inventory, row,
                                        8 + row * 18, 142))

    def _drawGuiContainerForegroundLayer(self):
        self._fontRenderer.drawString('Furnace', 60, 6, 4210752)
        self._fontRenderer.drawString('Inventory', 8, self.ySize - 96 + 2, 4210752)

    def _drawGuiContainerBackgroundLayer(self):
        tex = self.mc.renderEngine.getTexture('gui/furnace.png')
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)
        RenderEngine.bindTexture(tex)
        x = (self.width - self.xSize) // 2
        y = (self.height - self.ySize) // 2
        self.drawTexturedModalRect(x, y, 0, 0, self.xSize, self.ySize)
        if self.__furnaceInventory.isBurning():
            burnTime = self.__furnaceInventory.getBurnTimeRemainingScaled(12)
            self.drawTexturedModalRect(x + 56, y + 36 + 12 - burnTime, 176,
                                       12 - burnTime, 14, burnTime + 2)

        cookProgress = self.__furnaceInventory.getCookProgressScaled(24)
        self.drawTexturedModalRect(x + 79, y + 34, 176, 14, cookProgress + 1, 16)
