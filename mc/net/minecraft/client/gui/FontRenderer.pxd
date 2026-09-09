# cython: language_level=3

cimport cython

from mc.JavaUtils cimport IntBuffer

@cython.final
cdef class FontRenderer:

    cdef:
        int[256] __charWidth
        int __fontTextureName
        int __fontDisplayLists
        IntBuffer __buffer

    cdef __renderString(self, str string, int x, int y, int color, bint darken=?)
