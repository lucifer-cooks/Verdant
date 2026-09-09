from mc.net.minecraft.client.model.ModelRenderer import ModelRenderer
from mc.net.minecraft.client.model.ModelQuadruped import ModelQuadruped

class ModelSheepFur(ModelQuadruped):

    def __init__(self):
        super().__init__(12, 0.0)
        self.head = ModelRenderer(0, 0)
        self.head.addBox(-3.0, -4.0, -4.0, 6, 6, 6, 0.6)
        self.head.setRotationPoint(0.0, 6.0, -8.0)
        self.body = ModelRenderer(28, 8)
        self.body.addBox(-4.0, -10.0, -7.0, 8, 16, 6, 1.75)
        self.body.setRotationPoint(0.0, 5.0, 2.0)
        self.rightLegFront = ModelRenderer(0, 16)
        self.rightLegFront.addBox(-2.0, 0.0, -2.0, 4, 6, 4, 0.5)
        self.rightLegFront.setRotationPoint(-3.0, 12.0, 7.0)
        self.leftLegFront = ModelRenderer(0, 16)
        self.leftLegFront.addBox(-2.0, 0.0, -2.0, 4, 6, 4, 0.5)
        self.leftLegFront.setRotationPoint(3.0, 12.0, 7.0)
        self.rightLegBack = ModelRenderer(0, 16)
        self.rightLegBack.addBox(-2.0, 0.0, -2.0, 4, 6, 4, 0.5)
        self.rightLegBack.setRotationPoint(-3.0, 12.0, -5.0)
        self.leftLegBack = ModelRenderer(0, 16)
        self.leftLegBack.addBox(-2.0, 0.0, -2.0, 4, 6, 4, 0.5)
        self.leftLegBack.setRotationPoint(3.0, 12.0, -5.0)
