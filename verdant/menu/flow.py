"""VERDANT Progression Flow and World Launch Orchestrator.

Manages the transition from world creation to gameplay.
Structured so that in future milestones:
    CREATE WORLD -> INTRO CINEMATIC -> OUTWORLD
can be inserted seamlessly without redesigning world creation.
"""

from __future__ import annotations

import random
from typing import Any, Optional


def start_verdant_world(
    mc: Any,
    world_name: str = "My World",
    game_mode: str = "SURVIVAL",
    player_mode: str = "SINGLEPLAYER",
    seed: Optional[int] = None,
) -> None:
    """Launch a newly created VERDANT survival world.
    
    Parameters:
        mc: The authoritative Minecraft client instance.
        world_name: User-specified name for the world.
        game_mode: Gameplay mode (defaults to SURVIVAL).
        player_mode: SINGLEPLAYER or MULTIPLAYER.
        seed: Unique persistent world seed (generated randomly if None).
    """
    clean_name = world_name.strip() if world_name and world_name.strip() else "My World"
    if seed is None:
        seed = random.randint(10000000, 999999999)

    # Future milestone hook point:
    # 1. Trigger Helicopter Crash Cinematic
    # 2. Spawn player on OUTWORLD island
    #
    # Current authoritative implementation:
    # Generate huge OUTWORLD island survival world
    if hasattr(mc, "generateLevel"):
        # Set next world seed on mc for compatibility
        try:
            setattr(mc, "_next_world_seed", seed)
        except Exception:
            pass

        try:
            mc.generateLevel(1, 0, 1, 0, seed=seed)
        except TypeError:
            mc.generateLevel(1, 0, 1, 0)

        # Store world name, seed, and configuration
        if getattr(mc, "theWorld", None) is not None:
            mc.theWorld.name = clean_name
            try:
                from verdant.world.outworld import set_world_seed
                set_world_seed(mc.theWorld, seed)
            except Exception:
                pass

            # Store in Verdant world state if present
            if hasattr(mc, "verdant_world_state") and mc.verdant_world_state is not None:
                mc.verdant_world_state.world_name = clean_name
                mc.verdant_world_state.metadata["seed"] = seed

        # Close the creation screen and enter world
        if hasattr(mc, "displayGuiScreen"):
            mc.displayGuiScreen(None)
        if hasattr(mc, "setIngameFocus"):
            mc.setIngameFocus()
