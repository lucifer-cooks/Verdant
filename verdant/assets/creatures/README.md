# VERDANT Original Creature Visuals (M11)

This module implements the original visual identity, geometry, and textures for player and creature entities in VERDANT.

## Creature Visual Mappings

| Gameplay Entity | Behavioral Role | VERDANT Visual Identity | Model Class | Texture File |
|---|---|---|---|---|
| `EntityPlayer` | Protagonist / Explorer | **Verdant Wayfarer** | `ModelVerdantWayfarer` | `player/wayfarer.png` |
| `EntityPig` | Forest Grazer | **Mossback Boar** | `ModelMossbackBoar` | `passive/mossback_boar.png` |
| `EntitySheep` | Meadow Grazer | **Cloud-Ram** | `ModelCloudRam` | `passive/cloud_ram.png` |
| `EntityZombie` | Forest Ghoul | **Hollow Stalker** | `ModelHollowStalker` | `hostile/hollow_stalker.png` |
| `EntitySkeleton` | Thorned Archer | **Briar Reaver** | `ModelBriarReaver` | `hostile/briar_reaver.png` |
| `EntityCreeper` | Volatile Blight | **Spore Spire** | `ModelSporeSpire` | `hostile/spore_spire.png` |
| `EntitySpider` | Cave Predator | **Chittering Skitterer** | `ModelSkitterer` | `hostile/skitterer.png` |

## Key Architectural Invariants

1. **Authoritative Gameplay Simulation**:
   Entity classes, movement physics, AABB collisions, health/damage formulas, AI pathfinding, drops, day/night mob spawning, and M7–M9 ecological feedback remain completely untouched and authoritative.
2. **Visual Distinctiveness**:
   Every creature features an original silhouette, original geometry proportions, and authentic pixel art derived from the user's approved reference sheets. No silhouette or texture copies Minecraft IP.
3. **Pure Python Presentation**:
   Renderers integrate directly with `RenderManager.py` at the Python level. Zero compiled Cython files are modified.
4. **Theme Support**:
   - In `ThemeMode.VERDANT_ORIGINAL`, original Verdant models and textures are dispatched.
   - In `ThemeMode.CLASSIC`, legacy renderers and models are safely restored as a fallback.
