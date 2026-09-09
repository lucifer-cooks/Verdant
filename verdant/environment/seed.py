"""Deterministic seed utilities for VERDANT environmental calculations."""

from __future__ import annotations

import hashlib


class VerdantWorldSeed:
    """Small deterministic hash-based noise source for VERDANT.

    This is intentionally simple and does not touch the legacy terrain generator.
    It provides stable environmental sampling keyed by world seed and coordinates.
    """

    def __init__(self, seed: int = 0):
        self.seed = int(seed)

    def _hash_component(self, *parts):
        digest = hashlib.sha256()
        digest.update(str(self.seed).encode('utf-8'))
        for part in parts:
            digest.update(b'|')
            digest.update(str(part).encode('utf-8'))
        return digest.hexdigest()

    def noise(self, x: int, y: int, z: int):
        digest = self._hash_component(x, y, z)
        value = int(digest[:16], 16)
        return (value / 0xFFFFFFFFFFFFFFFF) * 2.0 - 1.0

    def value(self, x: int, y: int, z: int):
        return (self.noise(x, y, z) + 1.0) / 2.0
