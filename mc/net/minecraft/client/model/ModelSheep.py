from mc.net.minecraft.client.model.ModelQuadruped import ModelQuadruped
from mc.net.minecraft.client.model.ModelRenderer import ModelRenderer

class ModelSheep(ModelQuadruped):

    def __init__(self):
        super().__init__(12, 0.0)
        self.head = ModelRenderer(0, 0)
        self.head.addBox(-3.0, -4.0, -6.0, 6, 6, 8, 0.0)
        self.head.setRotationPoint(0.0, 6.0, -8.0)
        self.body = ModelRenderer(28, 8)
        self.body.addBox(-4.0, -10.0, -7.0, 8, 16, 6, 0.0)
        self.body.setRotationPoint(0.0, 5.0, 2.0)
