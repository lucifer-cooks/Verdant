"""Verdant original creature and player visual identity subsystem (M11)."""

from verdant.assets.creatures.models import (
    ModelBriarReaver,
    ModelCloudRam,
    ModelHollowStalker,
    ModelMossbackBoar,
    ModelSkitterer,
    ModelSporeSpire,
    ModelVerdantWayfarer,
)
from verdant.assets.creatures.renderers import (
    RenderBriarReaver,
    RenderCloudRam,
    RenderHollowStalker,
    RenderMossbackBoar,
    RenderSkitterer,
    RenderSporeSpire,
    RenderVerdantWayfarer,
)
from verdant.assets.creatures.textures import ensure_all_creature_textures
from verdant.assets.creatures.mapping import (
    VERDANT_CREATURE_SPECS,
    CreatureRenderDispatcher,
    install_verdant_creature_renderers,
    register_verdant_creature_textures,
)

__all__ = [
    "ModelVerdantWayfarer",
    "ModelMossbackBoar",
    "ModelCloudRam",
    "ModelHollowStalker",
    "ModelBriarReaver",
    "ModelSporeSpire",
    "ModelSkitterer",
    "RenderVerdantWayfarer",
    "RenderMossbackBoar",
    "RenderCloudRam",
    "RenderHollowStalker",
    "RenderBriarReaver",
    "RenderSporeSpire",
    "RenderSkitterer",
    "ensure_all_creature_textures",
    "VERDANT_CREATURE_SPECS",
    "CreatureRenderDispatcher",
    "install_verdant_creature_renderers",
    "register_verdant_creature_textures",
]
