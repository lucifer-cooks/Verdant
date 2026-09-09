from mc.net.minecraft.client.gui.Gui import Gui
from mc.net.minecraft.client.render.Tessellator import tessellator
from pyglet import window, gl

class GuiScreen(Gui):
    allowUserInput = False

    def drawScreen(self, xMouse, yMouse, renderPartialTicks):
        for button in self._controlList:
            button.drawButton(self.mc, xMouse, yMouse)

    def _keyTyped(self, key, char, motion):
        if key == window.key.ESCAPE:
            self.mc.displayGuiScreen(None)
            self.mc.setIngameFocus()

    def _mouseClicked(self, xm, ym, button):
        if button == window.mouse.LEFT:
            for button in self._controlList:
                if button.mousePressed(xm, ym):
                    self.mc.sndManager.playSoundFX('random.click', 1.0, 1.0)
                    self._actionPerformed(button)

    def _actionPerformed(self, button):
        pass

    def setWorldAndResolution(self, minecraft, width, height):
        self.mc = minecraft
        self._fontRenderer = minecraft.fontRenderer
        self.width = width
        self.height = height
        self._controlList = []
        self.initGui()

    def initGui(self):
        pass

    def handleMouseInput(self, button):
        xm = self.mc.mouseX * self.width // self.mc.width
        ym = self.height - self.mc.mouseY * self.height // self.mc.height - 1
        self._mouseClicked(xm, ym, button)

    def handleKeyboardEvent(self, key=None, char=None, motion=None):
        if key == window.key.F11:
            self.mc.toggleFullscreen()
            return

        self._keyTyped(key, char, motion)

    def updateScreen(self):
        pass

    def onGuiClosed(self):
        pass

    def drawDefaultBackground(self):
        if self.mc.theWorld:
            self._drawGradientRect(0, 0, self.width, self.height,
                                   1610941696, -1607454624)
            return

        gl.glDisable(gl.GL_LIGHTING)
        gl.glDisable(gl.GL_FOG)
        t = tessellator
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.mc.renderEngine.getTexture('dirt.png'))
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)
        t.startDrawingQuads()
        t.setColorOpaque_I(4210752)
        t.addVertexWithUV(0.0, self.height, 0.0, 0.0, self.height / 32.0)
        t.addVertexWithUV(self.width, self.height, 0.0, self.width / 32.0,
                          self.height / 32.0)
        t.addVertexWithUV(self.width, 0.0, 0.0, self.width / 32.0, 0.0)
        t.addVertexWithUV(0.0, 0.0, 0.0, 0.0, 0.0)
        t.draw()

    def doesGuiPauseGame(self):
        return True
