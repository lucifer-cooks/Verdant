# cython: language_level=3

cimport cython

cpdef unsigned long long getMillis()
cdef double signum(double val)
cdef unsigned int floatToRawIntBits(float x)

cdef class Random:

    cdef:
        long long __seed
        double __nextNextGaussian
        bint __haveNextNextGaussian

    cdef int _next(self, int bits)
    cpdef int nextInt(self, int limit=?)
    cpdef float nextFloat(self)
    cdef double nextDouble(self)
    cpdef double nextGaussian(self)

cpdef double random()

cdef class Bits:

    cdef long makeLong(self, unsigned char b7, unsigned char b6, unsigned char b5,
                       unsigned char b4, unsigned char b3, unsigned char b2,
                       unsigned char b1, unsigned char b0)
    cdef int makeInt(self, unsigned char b3, unsigned char b2,
                     unsigned char b1, unsigned char b0)
    cdef short makeShort(self, unsigned char b1, unsigned char b0)

cpdef enum ByteOrder:
    BIG_ENDIAN = 0
    LITTLE_ENDIAN = 1

cdef class Buffer(Bits):

    cdef:
        int _position
        int _limit
        int _capacity
        bint _order

    cpdef long getLong(self)
    cpdef int getInt(self)
    cpdef short getShort(self)
    cpdef double getDouble(self)
    cpdef float getFloat(self)

    cpdef order(self, bint order)
    cpdef flip(self)
    cpdef limit(self, int limit)
    cpdef position(self, int position=?)
    cpdef remaining(self)

    cpdef clear(self)
    cpdef capacity(self)
    cpdef compact(self)

    cdef int __nextIndex(self, int nb=?)
    cdef int nextGetIndex(self, int nb=?)
    cdef int nextPutIndex(self, int nb=?)

    cdef int checkIndex(self, int i)
    cdef bint checkBounds(self, int off, int length, int size)

@cython.final
cdef class ByteBuffer(Buffer):
    cdef:
        unsigned char[:] _array
        object __dataPtr
        int __lastPos

    cpdef inline put(self, unsigned char value)
    cdef inline putIntB(self, int bi, int x)
    cdef inline putFloatB(self, int bi, float x)
    cpdef inline unsigned char get(self)
    cpdef inline unsigned char getAt(self, int idx)
    cdef inline __getDataPtr(self)
    cdef IntBuffer asIntBuffer(self)
    cdef FloatBuffer asFloatBuffer(self)

cdef class IntBuffer(Buffer):
    cdef:
        int[:] __array
        object _dataPtr
        int _lastPos

    cpdef put(self, int value)
    cdef putInts(self, int[:] src, int offset, int length)
    cpdef int get(self)
    cpdef int getAt(self, int idx)
    cdef _getDataPtr(self)

cdef class FloatBuffer(Buffer):
    cdef:
        float[:] __array
        object _dataPtr
        int _lastPos

    cpdef put(self, float value)
    cdef putFloats(self, float* src, int offset, int length)
    cpdef float get(self)
    cpdef float getAt(self, int idx)
    cdef getFloats(self, float*, int size)
    cdef _getDataPtr(self)

cdef class ByteBufferAsIntBuffer(IntBuffer):
    cdef:
        ByteBuffer _bb
        int _offset

    cpdef put(self, int value)
    cdef _getDataPtr(self)

cdef class ByteBufferAsFloatBuffer(FloatBuffer):
    cdef:
        ByteBuffer _bb
        int _offset

    cpdef put(self, float value)
    cdef _getDataPtr(self)
