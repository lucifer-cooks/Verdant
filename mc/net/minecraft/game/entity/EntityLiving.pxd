# cython: language_level=3

from mc.net.minecraft.game.entity.Entity cimport Entity

cdef class EntityLiving(Entity):

    cdef:
        public int heartsHalvesLife
        public float renderYawOffset
        public float prevRenderYawOffset
        float __prevRotationYawHead
        float __rotationYawHead
        public str _texture
        public int health
        public int prevHealth
        int __livingSoundTime
        public int hurtTime
        public int maxHurtTime
        public float attackedAtYaw
        public int deathTime
        public int attackTime
        public float prevCameraPitch
        public float cameraPitch
        public float prevLimbYaw
        public float limbYaw
        public float limbSwing
        public int _entityAge
        public float _moveStrafing
        public float _moveForward
        float __randomYawVelocity
        public bint _isJumping
        float __defaultPitch
        public float _moveSpeed

    cpdef float _getEyeHeight(self)
    cdef _fall(self, float d)
    cdef travel(self, float x, float z)
