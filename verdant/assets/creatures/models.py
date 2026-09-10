"""Original Verdant Creature and Player Models.

Reverted to wrap the authoritative original Indev models (ModelZombie, ModelCreeper,
ModelPig, ModelSheep, ModelSkeleton, ModelSpider, ModelBiped) while maintaining
full compatibility with the Verdant theme and asset architecture.
"""

from __future__ import annotations

import math
from typing import List, Optional

from pyglet import gl

from mc.net.minecraft.client.model.ModelBase import ModelBase
from mc.net.minecraft.client.model.ModelBiped import ModelBiped
from mc.net.minecraft.client.model.ModelCreeper import ModelCreeper
from mc.net.minecraft.client.model.ModelPig import ModelPig
from mc.net.minecraft.client.model.ModelRenderer import ModelRenderer
from mc.net.minecraft.client.model.ModelSheep import ModelSheep
from mc.net.minecraft.client.model.ModelSkeleton import ModelSkeleton
from mc.net.minecraft.client.model.ModelSpider import ModelSpider
from mc.net.minecraft.client.model.ModelZombie import ModelZombie
from mc.net.minecraft.client.model.PositionTextureVertex import PositionTextureVertex
from mc.net.minecraft.client.render.Tessellator import tessellator


class VerdantTexturedQuad:
    """Textured quad supporting arbitrary texture canvas dimensions."""

    def __init__(
        self,
        vertices: List[PositionTextureVertex],
        u0: float,
        v0: float,
        u1: float,
        v1: float,
        tex_w: float = 64.0,
        tex_h: float = 32.0,
    ) -> None:
        self.vertexPositions = vertices
        if isinstance(u0, (int, float)):
            vertices[0] = vertices[0].setTexturePosition(
                u1 / tex_w - 0.0015625, v0 / tex_h + 0.003125
            )
            vertices[1] = vertices[1].setTexturePosition(
                u0 / tex_w + 0.0015625, v0 / tex_h + 0.003125
            )
            vertices[2] = vertices[2].setTexturePosition(
                u0 / tex_w + 0.0015625, v1 / tex_h - 0.003125
            )
            vertices[3] = vertices[3].setTexturePosition(
                u1 / tex_w - 0.0015625, v1 / tex_h - 0.003125
            )


class VerdantModelRenderer:
    """Modular box renderer utility."""

    def __init__(
        self,
        xTexOffs: int,
        yTexOffs: int,
        texture_width: float = 64.0,
        texture_height: float = 32.0,
    ) -> None:
        self.__corners: List[Optional[PositionTextureVertex]] = []
        self.__faces: List[Optional[VerdantTexturedQuad]] = []
        self.__textureOffsetX = xTexOffs
        self.__textureOffsetY = yTexOffs
        self.__textureWidth = float(texture_width)
        self.__textureHeight = float(texture_height)
        self.__rotationPointX = 0.0
        self.__rotationPointY = 0.0
        self.__rotationPointZ = 0.0
        self.rotateAngleX = 0.0
        self.rotateAngleY = 0.0
        self.rotateAngleZ = 0.0
        self.__compiled = False
        self.__displayList = 0
        self.mirror = False
        self.showModel = True
        self.__isHidden = False


# ==============================================================================
# REVERTED MOB MODELS — USING AUTHORITATIVE INDEV GEOMETRY
# ==============================================================================

class ModelHollowStalker(ModelZombie):
    """Hollow Stalker uses the authoritative original Zombie model geometry."""

    def __init__(self) -> None:
        super().__init__()
        self.twigs = getattr(self, "bipedHeadwear", None)


class ModelSporeSpire(ModelCreeper):
    """Spore Spire uses the authoritative original Creeper model geometry."""

    def __init__(self) -> None:
        super().__init__()
        self.cap = getattr(self, "_ModelCreeper__head", None)
        self.sporePods = getattr(self, "_ModelCreeper__headwear", None)
        self.tendril1 = getattr(self, "_ModelCreeper__leg1", None)
        self.tendril2 = getattr(self, "_ModelCreeper__leg2", None)
        self.tendril3 = getattr(self, "_ModelCreeper__leg3", None)


class ModelMossbackBoar(ModelPig):
    """Mossback Boar uses the authoritative original Pig model geometry."""

    def __init__(self) -> None:
        super().__init__()
        self.tuskLeft = None
        self.tuskRight = None
        self.mossCrest = None


class ModelCloudRam(ModelSheep):
    """Cloud-Ram uses the authoritative original Sheep model geometry."""

    def __init__(self) -> None:
        super().__init__()
        self.hornLeft = None
        self.hornRight = None
        self.fleece = getattr(self, "fleece", None)


class ModelBriarReaver(ModelSkeleton):
    """Briar Reaver uses the authoritative original Skeleton model geometry."""

    def __init__(self) -> None:
        super().__init__()
        self.antlers = None


class ModelSkitterer(ModelSpider):
    """Chittering Skitterer uses the authoritative original Spider model geometry."""

    def __init__(self) -> None:
        super().__init__()
        self.carapace = getattr(self, "_ModelSpider__head", None)
        self.mandibleLeft = None
        self.legs = [
            getattr(self, f"_ModelSpider__leg{i}", None)
            for i in range(1, 9)
        ]


class ModelVerdantWayfarer(ModelBiped):
    """Verdant Wayfarer uses the authoritative original player Biped model geometry."""

    def __init__(self, translation: float = 0.0, _=0.0) -> None:
        super().__init__(translation, _)
        self.hood_cowl = getattr(self, "bipedHeadwear", None)
        self.mantle = getattr(self, "bipedBody", None)
        self.satchel = None
        self.rightArm = getattr(self, "bipedRightArm", None)
        self.leftArm = getattr(self, "bipedLeftArm", None)
