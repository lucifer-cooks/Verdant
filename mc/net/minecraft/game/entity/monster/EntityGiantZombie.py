from mc.net.minecraft.game.entity.monster.EntityMob import EntityMob

class EntityGiantZombie(EntityMob):

    def __init__(self, world):
        super().__init__(world)
        self._texture = 'mob/zombie.png'
        self._moveSpeed = 0.5
        self._attackStrength = 50
        self.health *= 10
        self.yOffset *= 6.0
        self.setSize(self.width * 6.0, self.height * 6.0)

    def _getBlockPathWeight(self, x, y, z):
        return self._worldObj.getBrightness(x, y, z) - 0.5

    def _getEntityString(self):
        return 'Giant'
