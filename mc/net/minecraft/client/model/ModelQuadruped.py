from mc.net.minecraft.client.model.ModelRenderer import ModelRenderer
from mc.net.minecraft.client.model.ModelBase import ModelBase

import math

class ModelQuadruped(ModelBase):

    def __init__(self, yRot, _):
        self.head = ModelRenderer(0, 0)
        self.head.addBox(-4.0, -4.0, -8.0, 8, 8, 8, 0.0)
        self.head.setRotationPoint(0.0, 18 - yRot, -6.0)
        self.body = ModelRenderer(28, 8)
        self.body.addBox(-5.0, -10.0, -7.0, 10, 16, 8, 0.0)
        self.body.setRotationPoint(0.0, 17 - yRot, 2.0)
        self.rightLegFront = ModelRenderer(0, 16)
        self.rightLegFront.addBox(-2.0, 0.0, -2.0, 4, yRot, 4, 0.0)
        self.rightLegFront.setRotationPoint(-3.0, 24 - yRot, 7.0)
        self.leftLegFront = ModelRenderer(0, 16)
        self.leftLegFront.addBox(-2.0, 0.0, -2.0, 4, yRot, 4, 0.0)
        self.leftLegFront.setRotationPoint(3.0, 24 - yRot, 7.0)
        self.rightLegBack = ModelRenderer(0, 16)
        self.rightLegBack.addBox(-2.0, 0.0, -2.0, 4, yRot, 4, 0.0)
        self.rightLegBack.setRotationPoint(-3.0, 24 - yRot, -5.0)
        self.leftLegBack = ModelRenderer(0, 16)
        self.leftLegBack.addBox(-2.0, 0.0, -2.0, 4, yRot, 4, 0.0)
        self.leftLegBack.setRotationPoint(3.0, 24 - yRot, -5.0)

    def render(self, x, y, z, xRot, yRot, zRot):
        self.setRotationAngles(x, y, z, xRot, yRot, 1.0)
        self.head.render(1.0)
        self.body.render(1.0)
        self.rightLegFront.render(1.0)
        self.leftLegFront.render(1.0)
        self.rightLegBack.render(1.0)
        self.leftLegBack.render(1.0)

    def setRotationAngles(self, x, y, z, xRot, yRot, zRot):
        self.head.rotateAngleY = xRot / (180.0 / math.pi)
        self.head.rotateAngleX = yRot / (180.0 / math.pi)
        self.body.rotateAngleX = math.pi * 0.5
        self.rightLegFront.rotateAngleX = math.cos(x * 0.6662) * 1.4 * y
        self.leftLegFront.rotateAngleX = math.cos(x * 0.6662 + math.pi) * 1.4 * y
        self.rightLegBack.rotateAngleX = math.cos(x * 0.6662 + math.pi) * 1.4 * y
        self.leftLegBack.rotateAngleX = math.cos(x * 0.6662) * 1.4 * y
