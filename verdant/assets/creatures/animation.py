"""Lightweight visual animation functions for Verdant original models."""

from __future__ import annotations

import math


def calculate_limb_swing(distance_walked: float, limb_yaw: float, speed_multiplier: float = 0.6662) -> float:
    """Calculate natural sinusoidal leg swing angle."""
    return math.cos(distance_walked * speed_multiplier) * 1.4 * limb_yaw


def calculate_breathing_offset(ticks_existed: float, frequency: float = 0.08, amplitude: float = 0.05) -> float:
    """Calculate subtle resting breathing motion."""
    return math.cos(ticks_existed * frequency) * amplitude


def calculate_fungal_pulse(fuse_progress: float) -> tuple[float, float]:
    """Calculate non-linear swelling expansion for Spore Spire volatile buildup."""
    clamped = min(max(fuse_progress, 0.0), 1.0)
    curved = clamped * clamped * clamped
    scale_xz = 1.0 + curved * 0.40
    scale_y = 1.0 + curved * 0.20
    return scale_xz, scale_y
