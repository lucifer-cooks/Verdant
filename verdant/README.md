# VERDANT extension layer

This package is intentionally separate from the original Minecraft Indev codebase.
The original engine remains the foundation, and VERDANT is a future extension layer.

## Foundation boundary

The following belong to the original Indev foundation and must remain unchanged unless a dedicated milestone explicitly targets them:

- rendering pipeline
- world generation
- physics and movement
- inventory handling
- crafting logic
- entity systems
- legacy save/load format

## VERDANT responsibility

Future VERDANT modules should live under this package and focus on:

- modern biome systems
- climate and weather
- vegetation and ecosystem layers
- resource simulation
- settlement and civilization systems
- NPC and population management
- player progression and extended systems

## Legacy communication model

VERDANT talks to the legacy game through small, explicit no-op hooks defined in `verdant/hooks.py`.
The current implementation does not change gameplay at all. It only provides a safe extension edge.

Legacy systems that are currently bridged for M1:

- world generation
- world tick
- render frame
- entity updates
- persistence save/load
- world change events

## Where future code goes

Future modules should be added under `verdant/` instead of sprinkling logic across the legacy package tree.
Examples:

- `verdant/world/` for biome, climate, terrain layers
- `verdant/living_world/` for wildlife and ecology systems
- `verdant/civilization/` for settlement and NPC logic
- `verdant/player/` for player progression and expanded systems
- `verdant/persistence/` for save extensions

## Hard changes that require explicit milestones

The following legacy systems must not be modified casually:

- `mc/net/minecraft/client/render/*`
- `mc/net/minecraft/game/level/generator/*`
- `mc/net/minecraft/game/level/World.pyx`
- `mc/net/minecraft/client/player/*`
- `mc/net/minecraft/game/item/*`
- `mc/net/minecraft/game/entity/*`

Any changes to these systems require a dedicated milestone and a separate risk review.
