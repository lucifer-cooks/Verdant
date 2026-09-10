# VERDANT Asset Redirection Subsystem (M10)

This directory houses the presentation and asset redirection architecture for VERDANT.

## Architectural Principles

1. **KEEP → STUDY → WRAP → EXTEND → REPLACE**:
   The authoritative legacy Indev engine remains untouched. Visual and auditory presentation is decoupled through Python-level redirection.
2. **Zero Proprietary Asset Copies**:
   Minecraft copyrighted assets must **never** be copied into `themes/classic/` or `themes/verdant/`.
   - In `CLASSIC` mode, resources are resolved directly from the legacy engine (`mc.Resources` and `mc/resources/`).
   - In `VERDANT_ORIGINAL` mode, the engine looks for original assets in `themes/verdant/` and falls back safely to the legacy engine when an asset has not yet been authored.
3. **Atlas Compatibility**:
   Replacement atlases (e.g. `terrain.png`, `gui/items.png`) must maintain a 256×256 power-of-two resolution divided into a 16×16 tile grid (16×16 pixels per block face) so compiled Cython vertex UV mappings remain mathematically correct without modifying Cython source.

## Directory Layout

```
verdant/assets/
├── __init__.py           # Public exports
├── paths.py              # Directory paths & helpers
├── theme.py              # ThemeMode (CLASSIC, VERDANT_ORIGINAL)
├── validation.py         # Dimension, power-of-two, and format validators
├── registry.py           # Logical key resolution (textures, audio, entities, blocks)
├── textures.py           # RenderEngine texture interception
├── audio.py              # SoundManager audio cue redirection
├── debug.py              # Asset resolution diagnostics
├── README.md             # This document
└── themes/
    ├── classic/          # Logical legacy fallback (empty, zero copies)
    └── verdant/          # Original Verdant assets
        ├── textures/     # Original terrain, items, gui sheets
        ├── audio/        # Original .ogg sound effects & music
        ├── entities/     # Original mob and player textures
        ├── gui/          # Original HUD and dialog windows
        └── font/         # Original typography sheets
```

## Adding Original Verdant Assets

To add an original Verdant asset:
1. Ensure the asset is an original creation (no derivative works of Minecraft art).
2. Place the file in the appropriate subfolder under `themes/verdant/` matching its logical name (e.g. `themes/verdant/textures/terrain.png` or `themes/verdant/audio/step.grass.ogg`).
3. The registry will validate dimensions and automatically prioritize it over legacy fallback.
