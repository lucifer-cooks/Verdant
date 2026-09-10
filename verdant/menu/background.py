"""Atmospheric background renderer for the VERDANT main menu."""

from __future__ import annotations

import math
import random
from typing import List, Tuple
from pyglet import gl

from mc.net.minecraft.client.gui.Gui import Gui
from mc.net.minecraft.client.render.Tessellator import tessellator


class SporeParticle:
    """Lightweight 2D bioluminescent spore particle."""

    def __init__(self, x: float, y: float, width: int, height: int, rng: random.Random) -> None:
        self.x = x
        self.y = y
        self.size = rng.uniform(1.2, 2.5)
        self.speed_y = rng.uniform(0.18, 0.45)
        self.amplitude = rng.uniform(0.3, 0.8)
        self.frequency = rng.uniform(0.02, 0.05)
        self.phase = rng.uniform(0, math.pi * 2)
        self.alpha = rng.uniform(0.2, 0.7)
        self.color_tint = rng.choice([
            (74, 222, 128),   # Vibrant emerald
            (110, 231, 183),  # Mint bio-glow
            (251, 191, 36),   # Amber spore
            (52, 211, 153),   # Seafoam green
        ])
        self.age = rng.uniform(0, 100)

    def update(self, width: int, height: int) -> None:
        self.age += 1.0
        self.y -= self.speed_y
        self.x += math.sin(self.age * self.frequency + self.phase) * self.amplitude

        # Wrap around screen edges
        if self.y < -10:
            self.y = height + 10
            self.x = random.uniform(0, max(width, 100))
        if self.x < 0:
            self.x = width
        elif self.x > width:
            self.x = 0

    def get_render_color(self) -> int:
        # Subtle alpha breathing pulse
        pulse = 0.8 + math.sin(self.age * 0.08) * 0.2
        a = int(min(max(self.alpha * pulse * 255.0, 10.0), 255.0))
        r, g, b = self.color_tint
        return (a << 24) | (r << 16) | (g << 8) | b


class VerdantAtmosphericBackground:
    """Renders a cinematic dark forest/island atmosphere behind VERDANT screens."""

    def __init__(self, particle_count: int = 35, seed: int = 42) -> None:
        self._rng = random.Random(seed)
        self._particles: List[SporeParticle] = []
        self._particle_count = particle_count
        self._initialized = False

    def _ensure_particles(self, width: int, height: int) -> None:
        if not self._initialized and width > 0 and height > 0:
            for _ in range(self._particle_count):
                px = self._rng.uniform(0, width)
                py = self._rng.uniform(0, height)
                self._particles.append(SporeParticle(px, py, width, height, self._rng))
            self._initialized = True

    def update(self, width: int, height: int) -> None:
        """Update particle physics."""
        self._ensure_particles(width, height)
        for p in self._particles:
            p.update(width, height)

    def draw(self, width: int, height: int) -> None:
        """Render the multi-layered atmospheric background."""
        self._ensure_particles(width, height)

        # 1. Base dark oceanic-forest vertical gradient covering 100% of the screen
        half_h = height // 2
        Gui._drawGradientRect(0, 0, width, half_h, 0xFF040A07, 0xFF0A1810)
        Gui._drawGradientRect(0, half_h, width, height, 0xFF0A1810, 0xFF050B08)

        # 2. Subtle horizontal mist line across horizon
        horizon_y = int(height * 0.48)
        Gui._drawGradientRect(0, horizon_y - 20, width, horizon_y, 0x000F261A, 0x33143322)
        Gui._drawGradientRect(0, horizon_y, width, horizon_y + 30, 0x33143322, 0x00050D08)

        # 3. Floating bioluminescent spore particles
        for p in self._particles:
            col = p.get_render_color()
            s = p.size
            Gui._drawRect(int(p.x), int(p.y), int(p.x + s), int(p.y + s), col)
