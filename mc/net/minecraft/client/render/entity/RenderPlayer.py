from mc.net.minecraft.client.render.entity.RenderLiving import RenderLiving
from mc.net.minecraft.client.model.ModelBiped import ModelBiped
from mc.net.minecraft.game.item.ItemArmor import ItemArmor

class RenderPlayer(RenderLiving):
    __armorFilenamePrefix = ('cloth', 'chain', 'iron', 'diamond', 'gold')

    def __init__(self):
        super().__init__(ModelBiped(0.0), 0.5)
        self.__modelBipedMain = self._mainModel
        self.__modelArmorChestplate = ModelBiped(1.0)
        self.__modelArmor = ModelBiped(0.5)

    def __renderPlayer(self, entity, xd, yd, zd, yaw, a):
        super().renderLiving(entity, xd, yd - entity.yOffset, zd, yaw, a)

    def drawFirstPersonHand(self):
        self.__modelBipedMain.bipedRightArm.render(1.0)

    def _shouldRenderPass(self, entity, i):
        stack = entity.inventory.armorInventory[3 - i]
        if stack:
            item = stack.getItem()
            if isinstance(item, ItemArmor):
                self._loadTexture(
                    'armor/' + RenderPlayer.__armorFilenamePrefix[item.renderIndex] + \
                    '_' + str(2 if i == 2 else 1) + '.png'
                )
                model = self.__modelArmor if i == 2 else self.__modelArmorChestplate
                model.bipedHead.showModel = i == 0
                model.bipedHeadwear.showModel = i == 0
                model.bipedBody.showModel = i == 1 or i == 2
                model.bipedRightArm.showModel = i == 1
                model.bipedLeftArm.showModel = i == 1
                model.bipedRightLeg.showModel = i == 2 or i == 3
                model.bipedLeftLeg.showModel = i == 2 or i == 3
                self.setRenderPassModel(model)
                return True

        return False

    def renderLiving(self, entity, xd, yd, zd, yaw, a):
        self.__renderPlayer(entity, xd, yd, zd, yaw, a)

    def doRender(self, entity, xd, yd, zd, yaw, a):
        self.__renderPlayer(entity, xd, yd, zd, yaw, a)
