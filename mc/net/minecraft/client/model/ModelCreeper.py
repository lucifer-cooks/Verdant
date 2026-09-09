from mc.net.minecraft.client.model.ModelRenderer import ModelRenderer
from mc.net.minecraft.client.model.ModelBase import ModelBase

import math

class ModelCreeper(ModelBase):

    def __init__(self):
        self.__head = ModelRenderer(0, 0)
        self.__head.addBox(-4.0, -8.0, -4.0, 8, 8, 8, 0.0)
        self.__head.setRotationPoint(0.0, 4.0, 0.0)
        self.__headwear = ModelRenderer(32, 0)
        self.__headwear.addBox(-4.0, -8.0, -4.0, 8, 8, 8, 0.5)
        self.__headwear.setRotationPoint(0.0, 4.0, 0.0)
        self.__body = ModelRenderer(16, 16)
        self.__body.addBox(-4.0, 0.0, -2.0, 8, 12, 4, 0.0)
        self.__body.setRotationPoint(0.0, 4.0, 0.0)
        self.__leg1 = ModelRenderer(0, 16)
        self.__leg1.addBox(-2.0, 0.0, -2.0, 4, 6, 4, 0.0)
        self.__leg1.setRotationPoint(-2.0, 16.0, 4.0)
        self.__leg2 = ModelRenderer(0, 16)
        self.__leg2.addBox(-2.0, 0.0, -2.0, 4, 6, 4, 0.0)
        self.__leg2.setRotationPoint(2.0, 16.0, 4.0)
        self.__leg3 = ModelRenderer(0, 16)
        self.__leg3.addBox(-2.0, 0.0, -2.0, 4, 6, 4, 0.0)
        self.__leg3.setRotationPoint(-2.0, 16.0, -4.0)
        self.__leg4 = ModelRenderer(0, 16)
        self.__leg4.addBox(-2.0, 0.0, -2.0, 4, 6, 4, 0.0)
        self.__leg4.setRotationPoint(2.0, 16.0, -4.0)

    def render(self, x, y, z, xRot, yRot, zRot):
        self.setRotationAngles(x, y, z, xRot, yRot, 1.0)
        self.__head.render(1.0)
        self.__body.render(1.0)
        self.__leg1.render(1.0)
        self.__leg2.render(1.0)
        self.__leg3.render(1.0)
        self.__leg4.render(1.0)

    def setRotationAngles(self, x, y, z, xRot, yRot, zRot):
        self.__head.rotateAngleY = yRot / (180.0 / math.pi)
        self.__head.rotateAngleX = xRot / (180.0 / math.pi)
        self.__leg1.rotateAngleX = math.cos(x * 0.6662) * 1.4 * y
        self.__leg2.rotateAngleX = math.cos(x * 0.6662 + math.pi) * 1.4 * y
        self.__leg3.rotateAngleX = math.cos(x * 0.6662 + math.pi) * 1.4 * y
        self.__leg4.rotateAngleX = math.cos(x * 0.6662) * 1.4 * y
