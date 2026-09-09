# cython: language_level=3

import numpy as np
cimport numpy as np

from mc.JavaUtils cimport FloatBuffer, IntBuffer, floatToRawIntBits
from mc.JavaUtils import BufferUtils
from pyglet import gl

cdef class Tessellator:
    MAX_INTS = 2097152

    def __cinit__(self):
        self.max_ints = self.MAX_INTS
        self.__byteBuffer = BufferUtils.createByteBuffer(self.max_ints << 2)
        self.__rawBuffer = np.zeros(self.max_ints, dtype=np.int32)
        self.__rawBufferIndex = 0
        self.__addedVertices = 0
        self.__vboIndex = 0
        self.__vboCount = 10
        self.__isDrawing = False

    def __init__(self):
        self.__useVBO = False
        if self.__useVBO:
            self.__vertexBuffers = BufferUtils.createIntBuffer(self.__vboCount)
            self.__vertexBuffers.glGenBuffersARB()

    cpdef void draw(self):
        cdef IntBuffer ib
        cdef FloatBuffer fb

        if not self.__isDrawing:
            raise RuntimeError('Not tesselating!')

        self.__isDrawing = False
        if self.__vertexCount > 0:
            ib = self.__byteBuffer.asIntBuffer()
            fb = self.__byteBuffer.asFloatBuffer()
            ib.clear()
            ib.putInts(self.__rawBuffer, 0, self.__rawBufferIndex)
            fb.position(0)
            self.__byteBuffer.position(0)
            self.__byteBuffer.limit(self.__rawBufferIndex << 2)
            if self.__useVBO:
                self.__vboIndex = (self.__vboIndex + 1) % self.__vboCount
                gl.glBindBufferARB(gl.GL_ARRAY_BUFFER, self.__vertexBuffers.getAt(self.__vboIndex))
                self.__byteBuffer.glBufferDataARB(gl.GL_ARRAY_BUFFER, gl.GL_STREAM_DRAW)

            if self.__hasTexture:
                if self.__useVBO:
                    gl.glTexCoordPointer(2, gl.GL_FLOAT, 32, 12)
                else:
                    fb.position(3)
                    fb.glTexCoordPointer(2, 32)

                gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
            if self.__hasColor:
                if self.__useVBO:
                    gl.glColorPointer(4, gl.GL_UNSIGNED_BYTE, 32, 20)
                else:
                    self.__byteBuffer.position(20)
                    self.__byteBuffer.glColorPointer(4, 32)

                gl.glEnableClientState(gl.GL_COLOR_ARRAY)

            if self.__useVBO:
                gl.glVertexPointer(3, gl.GL_FLOAT, 32, 0)
            else:
                fb.position(0)
                fb.glVertexPointer(3, 32)

            gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
            gl.glDrawArrays(self.__drawMode, gl.GL_POINTS, self.__vertexCount)
            gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
            if self.__hasTexture:
                gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
            if self.__hasColor:
                gl.glDisableClientState(gl.GL_COLOR_ARRAY)

        self.__reset()

    cdef void __reset(self):
        self.__vertexCount = 0
        self.__byteBuffer.clear()
        self.__rawBufferIndex = 0
        self.__addedVertices = 0

    cpdef void startDrawingQuads(self):
        self.startDrawing(gl.GL_QUADS)

    cdef void startDrawing(self, int drawMode):
        if self.__isDrawing:
            raise RuntimeError('Already tesselating!')

        self.__isDrawing = True
        self.__reset()
        self.__drawMode = drawMode
        self.__hasColor = False
        self.__hasTexture = False
        self.__isColorDisabled = False

    cpdef inline void setColorOpaque_F(self, float r, float g, float b):
        self.__setColorOpaque(<int>(r * 255.0), <int>(g * 255.0), <int>(b * 255.0))

    def setColorRGBA_F(self, float r, float g, float b, float a):
        self.__setColorRGBA(<int>(r * 255.0), <int>(g * 255.0),
                            <int>(b * 255.0), <int>(a * 255.0))

    cdef inline void __setColorOpaque(self, int r, int g, int b):
        self.__setColorRGBA(r, g, b, 255)

    cdef inline void __setColorRGBA(self, int r, int g, int b, int a):
        if self.__isColorDisabled:
            return

        r = max(min(r, 255), 0)
        g = max(min(g, 255), 0)
        b = max(min(b, 255), 0)
        a = max(min(a, 255), 0)

        self.__hasColor = True
        self.__color = a << 24 | b << 16 | g << 8 | r

    cpdef void addVertexWithUV(self, float x, float y, float z, float u, float v):
        self.__hasTexture = True
        self.__textureU = u
        self.__textureV = v
        self.addVertex(x, y, z)

    cpdef void addVertex(self, float x, float y, float z):
        self.__addedVertices += 1
        if self.__hasTexture:
            self.__rawBuffer[self.__rawBufferIndex + 3] = floatToRawIntBits(self.__textureU)
            self.__rawBuffer[self.__rawBufferIndex + 4] = floatToRawIntBits(self.__textureV)

        if self.__hasColor:
            self.__rawBuffer[self.__rawBufferIndex + 5] = self.__color

        self.__rawBuffer[self.__rawBufferIndex    ] = floatToRawIntBits(x)
        self.__rawBuffer[self.__rawBufferIndex + 1] = floatToRawIntBits(y)
        self.__rawBuffer[self.__rawBufferIndex + 2] = floatToRawIntBits(z)
        self.__rawBufferIndex += 8

        self.__vertexCount += 1
        if self.__vertexCount % 4 == 0 and self.__rawBufferIndex >= self.max_ints - 32:
            self.draw()

    cpdef inline void setColorOpaque_I(self, int c):
        cdef int r = c >> 16 & 0xFF
        cdef int g = c >> 8 & 0xFF
        cdef int b = c & 0xFF
        self.__setColorOpaque(r, g, b)

    cpdef inline void disableColor(self):
        self.__isColorDisabled = True

    @staticmethod
    def setNormal(float x, float y, float z):
        gl.glNormal3f(x, y, z)

tessellator = Tessellator()
