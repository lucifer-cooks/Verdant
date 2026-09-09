# cython: language_level=3

cimport cython

from mc.JavaUtils cimport ByteBuffer, IntBuffer

@cython.final
cdef class Tessellator:

    cdef:
        int max_ints

        ByteBuffer __byteBuffer
        int[:] __rawBuffer

        int __vertexCount

        float __textureU
        float __textureV

        int __color

        bint __hasColor
        bint __hasTexture

        int __rawBufferIndex
        int __addedVertices

        bint __isColorDisabled
        int __drawMode

        bint __isDrawing
        bint __useVBO

        IntBuffer __vertexBuffers

        int __vboIndex
        int __vboCount

    cpdef void draw(self)
    cdef void __reset(self)
    cpdef void startDrawingQuads(self)
    cdef void startDrawing(self, int drawMode)
    cpdef inline void setColorOpaque_F(self, float r, float g, float b)
    cdef inline void __setColorOpaque(self, int r, int g, int b)
    cdef inline void __setColorRGBA(self, int r, int g, int b, int a)
    cpdef void addVertexWithUV(self, float x, float y, float z, float u, float v)
    cpdef void addVertex(self, float x, float y, float z)
    cpdef inline void setColorOpaque_I(self, int c)
    cpdef inline void disableColor(self)
