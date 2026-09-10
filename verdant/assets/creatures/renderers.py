"""Custom entity renderers for Verdant original creature and player models.

Reverted to wrap the authoritative original Indev entity renderers
(RenderLiving, RenderCreeper, RenderSpider, RenderSheep, RenderPlayer)
with custom skin support for Hollow Stalker (Zombie) and Spore Spire (Creeper).
"""

from __future__ import annotations

try:
    import mc.net.minecraft.client.render.RenderGlobal
except Exception:
    pass

import math
from pyglet import gl

from mc.net.minecraft.client.model.ModelPig import ModelPig
from mc.net.minecraft.client.model.ModelSheep import ModelSheep
from mc.net.minecraft.client.model.ModelSheepFur import ModelSheepFur
from mc.net.minecraft.client.model.ModelSkeleton import ModelSkeleton
from mc.net.minecraft.client.model.ModelZombie import ModelZombie
from mc.net.minecraft.client.render.entity.RenderCreeper import RenderCreeper
from mc.net.minecraft.client.render.entity.RenderGiantZombie import RenderGiantZombie
from mc.net.minecraft.client.render.entity.RenderLiving import RenderLiving
from mc.net.minecraft.client.render.entity.RenderPlayer import RenderPlayer
from mc.net.minecraft.client.render.entity.RenderSheep import RenderSheep
from mc.net.minecraft.client.render.entity.RenderSpider import RenderSpider
from verdant.assets.creatures.models import (
    ModelBriarReaver,
    ModelCloudRam,
    ModelHollowStalker,
    ModelMossbackBoar,
    ModelSkitterer,
    ModelSporeSpire,
    ModelVerdantWayfarer,
)


class RenderVerdantWayfarer(RenderPlayer):
    """Renderer for the Verdant Wayfarer (Player)."""

    def __init__(self) -> None:
        super().__init__()


class RenderMossbackBoar(RenderLiving):
    """Renderer for the Verdant Mossback Boar (Pig gameplay role)."""

    def __init__(self) -> None:
        super().__init__(ModelPig(), 0.7)


class RenderCloudRam(RenderSheep):
    """Renderer for the Verdant Cloud-Ram (Sheep gameplay role)."""

    def __init__(self) -> None:
        super().__init__(ModelSheep(), ModelSheepFur(), 0.7)


class RenderHollowStalker(RenderLiving):
    """Renderer for the Verdant Hollow Stalker (Zombie gameplay role).
    
    Uses original ModelZombie with the user's custom hollow_stalker.png skin.
    """

    def __init__(self) -> None:
        super().__init__(ModelZombie(), 0.5)


class RenderBriarReaver(RenderLiving):
    """Renderer for the Verdant Briar Reaver (Skeleton gameplay role)."""

    def __init__(self) -> None:
        super().__init__(ModelSkeleton(), 0.5)


class RenderSporeSpire(RenderCreeper):
    """Renderer for the Verdant Spore Spire (Creeper gameplay role).
    
    Uses original ModelCreeper with the user's custom spore_spire.png skin,
    retaining original swelling and flashing animation mechanics.
    """

    def __init__(self) -> None:
        super().__init__()


class RenderSkitterer(RenderSpider):
    """Renderer for the Verdant Chittering Skitterer (Spider gameplay role)."""

    def __init__(self) -> None:
        super().__init__()
