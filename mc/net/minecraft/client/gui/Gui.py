from mc.net.minecraft.client.render.Tessellator import tessellator
from pyglet import gl

class Gui:
    _zLevel = 0.0

    @staticmethod
    def _drawRect(x0, y0, x1, y1, col):
        a = ((col % 0x100000000) >> 24) / 255.0
        r = (col >> 16 & 255) / 255.0
        g = (col >> 8 & 255) / 255.0
        b = (col & 255) / 255.0
        t = tessellator
        gl.glEnable(gl.GL_BLEND)
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glColor4f(r, g, b, a)
        t.startDrawingQuads()
        t.addVertex(x0, y1, 0.0)
        t.addVertex(x1, y1, 0.0)
        t.addVertex(x1, y0, 0.0)
        t.addVertex(x0, y0, 0.0)
        t.draw()
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glDisable(gl.GL_BLEND)

    @staticmethod
    def _drawGradientRect(x0, y0, x1, y1, col1, col2):
        a1 = ((col1 % 0x100000000) >> 24) / 255.0
        r1 = (col1 >> 16 & 255) / 255.0
        g1 = (col1 >> 8 & 255) / 255.0
        b1 = (col1 & 255) / 255.0
        a2 = ((col2 % 0x100000000) >> 24) / 255.0
        r2 = (col2 >> 16 & 255) / 255.0
        g2 = (col2 >> 8 & 255) / 255.0
        b2 = (col2 & 255) / 255.0
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glEnable(gl.GL_BLEND)
        gl.glDisable(gl.GL_ALPHA_TEST)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        t = tessellator
        t.startDrawingQuads()
        t.setColorRGBA_F(r1, g1, b1, a1)
        t.addVertex(x1, y0, 0.0)
        t.addVertex(x0, y0, 0.0)
        t.setColorRGBA_F(r2, g2, b2, a2)
        t.addVertex(x0, y1, 0.0)
        t.addVertex(x1, y1, 0.0)
        t.draw()
        gl.glDisable(gl.GL_BLEND)
        gl.glEnable(gl.GL_ALPHA_TEST)
        gl.glEnable(gl.GL_TEXTURE_2D)

    @staticmethod
    def drawCenteredString(font, string, x, y, color):
        font.drawStringWithShadow(string, int(x - font.getStringWidth(string) / 2),
                                  y, color)

    @staticmethod
    def drawString(font, string, x, y, color):
        font.drawStringWithShadow(string, x, y, color)

    def drawTexturedModalRect(self, x, y, xOffset, yOffset, w, h):
        f = 0.00390625
        t = tessellator
        t.startDrawingQuads()
        t.addVertexWithUV(x, y + h, self._zLevel, xOffset * f, (yOffset + h) * f)
        t.addVertexWithUV(x + w, y + h, self._zLevel, (xOffset + w) * f, (yOffset + h) * f)
        t.addVertexWithUV(x + w, y, self._zLevel, (xOffset + w) * f, yOffset * f)
        t.addVertexWithUV(x, y, self._zLevel, xOffset * f, yOffset * f)
        t.draw()
