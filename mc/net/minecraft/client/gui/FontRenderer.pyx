# cython: language_level=3

cimport cython

from mc.net.minecraft.client.render.Tessellator import tessellator
from mc.JavaUtils import BufferUtils
from mc import Resources
from pyglet import gl

@cython.final
cdef class FontRenderer:

    def __init__(self, settings, name, textures):
        cdef int w, h, i, xt, yt, xPixel, yPixel, pixel, x, y, col, r, g, b, ar
        cdef bint emptyColumn

        self.__buffer = BufferUtils.createIntBuffer(1024)
        texture = Resources.textures[name + '1']
        w = texture[0]
        h = texture[1]
        rawPixels = texture[2]

        for i in range(128):
            xt = i % 16
            yt = i // 16

            emptyColumn = False
            for x in range(8):
                if emptyColumn:
                    break

                xPixel = (xt << 3) + x
                emptyColumn = True
                for y in range(8):
                    if not emptyColumn:
                        break

                    yPixel = ((yt << 3) + y) * w
                    pixel = rawPixels[xPixel + yPixel] & 255
                    if pixel > 128:
                        emptyColumn = False

            if i == 32:
                x = 4

            self.__charWidth[i] = x

        self.__fontTextureName = textures.getTexture(name + '2')
        self.__fontDisplayLists = gl.glGenLists(288)
        t = tessellator
        for i in range(256):
            gl.glNewList(self.__fontDisplayLists + i, gl.GL_COMPILE)
            t.startDrawingQuads()
            x = i % 16 << 3
            y = i // 16 << 3
            t.addVertexWithUV(0.0, 7.99, 0.0, x / 128.0, (y + 7.99) / 128.0)
            t.addVertexWithUV(7.99, 7.99, 0.0, (x + 7.99) / 128.0, (y + 7.99) / 128.0)
            t.addVertexWithUV(7.99, 0.0, 0.0, (x + 7.99) / 128.0, y / 128.0)
            t.addVertexWithUV(0.0, 0.0, 0.0, x / 128.0, y / 128.0)
            t.draw()
            gl.glTranslatef(self.__charWidth[i], 0.0, 0.0)
            gl.glEndList()

        i = 0
        while i < 32:
            col = (i & 8) << 3
            b = (i & 1) * 191 + col
            g = ((i & 2) >> 1) * 191 + col
            r = ((i & 4) >> 2) * 191 + col
            if settings.anaglyph:
                ar = (r * 30 + g * 59 + b * 11) // 100
                g = (r * 30 + g * 70) // 100
                b = (r * 30 + b * 70) // 100
                r = ar

            if i >= 16:
                r //= 4
                g //= 4
                b //= 4

            gl.glColor4f(r / 255.0, g / 255.0, b / 255.0, 1.0)
            i += 3

    def drawStringWithShadow(self, str string, int x, int y, int color):
        self.__renderString(string, x + 1, y + 1, color, True)
        self.drawString(string, x, y, color)

    def drawString(self, str string, int x, int y, int color):
        self.__renderString(string, x, y, color, False)

    cdef __renderString(self, str string, int x, int y, int color, bint darken=False):
        cdef float r, g, b
        cdef int i, cc

        if string is None:
            return

        if darken:
            color = (color & 0xFCFCFC) >> 2

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.__fontTextureName)
        r = (color >> 16 & 255) / 255.0
        g = (color >> 8 & 255) / 255.0
        b = (color & 255) / 255.0
        gl.glColor4f(r, g, b, 1.0)
        self.__buffer.clear()
        gl.glPushMatrix()
        gl.glTranslatef(x, y, 0.0)
        i = 0
        while i < len(string):
            while string[i] == '&' and len(string) > i + 1:
                cc = '0123456789abcdef'.index(string[i + 1])
                if cc < 0 or cc > 15:
                    cc = 15

                self.__buffer.put(
                    self.__fontDisplayLists + 256 + cc + (16 if darken else 0)
                )
                if self.__buffer.remaining() == 0:
                    self.__buffer.flip()
                    self.__buffer.glCallLists()
                    self.__buffer.clear()

                i += 2

            self.__buffer.put(self.__fontDisplayLists + ord(string[i]))
            if self.__buffer.remaining() == 0:
                self.__buffer.flip()
                self.__buffer.glCallLists()
                self.__buffer.clear()

            i += 1

        self.__buffer.flip()
        self.__buffer.glCallLists()
        gl.glPopMatrix()

    def getStringWidth(self, str string):
        cdef int length, i

        if string is None:
            return 0
        else:
            length = 0
            for i, char in enumerate(string):
                if char != '&':
                    length += self.__charWidth[ord(char)]

            return length
