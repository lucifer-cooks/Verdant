# VERDANT environmental layer

This package contains the M3 environmental foundation. It is intentionally separate
from the legacy world generator and does not rewrite terrain generation.

The model is intentionally lightweight and deterministic:

- world seed determines local environmental variation
- elevation is read from the existing legacy world when available
- season modifies climate values in a deterministic way
- biome classification is based on environmental ranges rather than block ids
- future systems can query the environment without touching engine internals

## Core ideas

- `VerdantWorldSeed` provides a deterministic, hash-based pseudo-noise source.
- `VerdantClimateSystem` produces local temperature/humidity/rainfall values.
- `VerdantBiomeDefinition` stores the data-driven biome envelope.
- `VerdantBiomeResolver` picks the most appropriate biome for an environment.
