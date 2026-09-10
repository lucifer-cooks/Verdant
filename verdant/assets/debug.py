"""Debug and diagnostic utilities for the Verdant asset redirection system."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from verdant.assets.registry import AssetRegistry, AssetResolutionResult
from verdant.assets.theme import ThemeManager


def get_asset_resolution(logical_key: str, category: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve detailed resolution information for a logical asset key.
    
    Returns a dictionary formatted for debugging and status inspection.
    """
    registry = AssetRegistry.get_instance()
    cat = (category or "").lower().strip()

    if cat == "audio" or logical_key.startswith("audio.") or logical_key.startswith("step.") or logical_key.startswith("mob."):
        res = registry.resolve_audio(logical_key)
    elif cat == "entity" or cat == "entities":
        res = registry.resolve_entity_visual(logical_key)
    elif cat == "block" or cat == "blocks":
        res = registry.resolve_block_visual(logical_key)
    else:
        # Default to texture resolution
        res = registry.resolve_texture(logical_key)

    source_repr = str(res.resolved_source) if res.resolved_source is not None else "None"
    
    return {
        "logical_key": res.logical_key,
        "category": res.category,
        "theme": res.theme.value,
        "source": "legacy fallback" if res.is_fallback else ("verdant asset" if res.resolved_source is not None else "unresolved"),
        "resolved_target": source_repr,
        "fallback": res.is_fallback,
        "valid": res.is_valid,
        "details": res.details,
    }


def format_asset_resolution(logical_key: str, category: Optional[str] = None) -> str:
    """Format get_asset_resolution() into human-readable text."""
    info = get_asset_resolution(logical_key, category)
    lines = [
        f"asset = {info['logical_key']} ({info['category']})",
        f"theme = {info['theme']}",
        f"source = {info['source']}",
        f"resolved_target = {info['resolved_target']}",
        f"fallback = {str(info['fallback']).lower()}",
        f"valid = {str(info['valid']).lower()}",
    ]
    return "\n".join(lines)


def dump_asset_report() -> List[Dict[str, Any]]:
    """Generate a summary list of all default registered assets and their resolution states."""
    registry = AssetRegistry.get_instance()
    report: List[Dict[str, Any]] = []

    # Textures
    for key in registry.DEFAULT_TEXTURE_MAPPINGS:
        report.append(get_asset_resolution(key, "textures"))

    # Entities
    for key in registry.ENTITY_MAPPINGS:
        report.append(get_asset_resolution(key, "entities"))

    # Audio cues
    for key in ("step.grass", "step.stone", "water.splash", "random.click", "mob.pig"):
        report.append(get_asset_resolution(key, "audio"))

    return report
