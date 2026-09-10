"""Asset validation utilities for textures, atlases, and audio files."""

from __future__ import annotations

import os
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass
class ValidationResult:
    """Represents the outcome of an asset validation check."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)


def is_power_of_two(n: int) -> bool:
    """Return True if n is a positive power of two."""
    return n > 0 and (n & (n - 1)) == 0


def inspect_png_header(file_path: Union[str, Path]) -> Tuple[Optional[int], Optional[int], bool]:
    """Inspect PNG file header directly without requiring PIL.
    
    Returns (width, height, has_alpha).
    """
    path = Path(file_path)
    if not path.is_file():
        return None, None, False

    try:
        with open(path, "rb") as f:
            header = f.read(29)
            if len(header) < 29 or header[:8] != b"\x89PNG\r\n\x1a\n":
                return None, None, False

            # IHDR starts at offset 8, length 4 bytes, chunk type 4 bytes (IHDR)
            if header[12:16] != b"IHDR":
                return None, None, False

            width, height, bit_depth, color_type = struct.unpack(">IIBB", header[16:26])
            # Color type: 4 (grayscale+alpha), 6 (RGBA)
            has_alpha = color_type in (4, 6)
            return width, height, has_alpha
    except Exception:
        return None, None, False


def validate_texture_file(
    file_path: Union[str, Path],
    expected_width: Optional[int] = None,
    expected_height: Optional[int] = None,
    require_power_of_two: bool = True,
    require_alpha: bool = False,
    require_grid_16: bool = False,
) -> ValidationResult:
    """Validate a texture file on disk."""
    res = ValidationResult(is_valid=True)
    path = Path(file_path)

    if not path.exists():
        res.add_error(f"Asset file does not exist: {path}")
        return res

    if not path.is_file():
        res.add_error(f"Asset path is not a file: {path}")
        return res

    ext = path.suffix.lower()
    if ext != ".png":
        res.add_error(f"Unsupported texture format '{ext}'; expected '.png'")
        return res

    width, height, has_alpha = inspect_png_header(path)
    if width is None or height is None:
        res.add_error(f"Failed to read valid PNG header from {path}")
        return res

    res.details = {
        "path": str(path),
        "width": width,
        "height": height,
        "has_alpha": has_alpha,
    }

    if require_power_of_two:
        if not is_power_of_two(width) or not is_power_of_two(height):
            res.add_error(f"Dimensions {width}x{height} are not powers of two")

    if expected_width is not None and width != expected_width:
        res.add_error(f"Width {width} does not match expected {expected_width}")

    if expected_height is not None and height != expected_height:
        res.add_error(f"Height {height} does not match expected {expected_height}")

    if require_grid_16:
        if width % 16 != 0 or height % 16 != 0:
            res.add_error(f"Dimensions {width}x{height} cannot be evenly partitioned into 16x16 tiles")

    if require_alpha and not has_alpha:
        res.add_warning("Texture does not contain an explicit alpha channel")

    return res


def validate_atlas(
    file_path: Union[str, Path],
    expected_tiles_per_axis: int = 16,
    recommended_dimension: int = 256,
) -> ValidationResult:
    """Validate a block or item texture atlas.
    
    Verifies that the atlas is a power-of-two square grid compatible with 16x16 legacy tiles.
    """
    res = validate_texture_file(
        file_path,
        expected_width=recommended_dimension,
        expected_height=recommended_dimension,
        require_power_of_two=True,
        require_alpha=False,
        require_grid_16=True,
    )
    if res.is_valid:
        res.details["tiles_per_axis"] = expected_tiles_per_axis
        res.details["tile_size"] = recommended_dimension // expected_tiles_per_axis
    return res


def validate_audio_file(file_path: Union[str, Path]) -> ValidationResult:
    """Validate an audio file on disk (.ogg format)."""
    res = ValidationResult(is_valid=True)
    path = Path(file_path)

    if not path.exists():
        res.add_error(f"Audio file does not exist: {path}")
        return res

    if not path.is_file():
        res.add_error(f"Audio path is not a file: {path}")
        return res

    ext = path.suffix.lower()
    if ext != ".ogg":
        res.add_error(f"Unsupported audio format '{ext}'; expected '.ogg'")
        return res

    try:
        with open(path, "rb") as f:
            header = f.read(4)
            if header != b"OggS":
                res.add_error(f"File {path} does not contain valid OggS container magic bytes")
                return res
    except Exception as e:
        res.add_error(f"Could not read audio file {path}: {e}")
        return res

    res.details = {
        "path": str(path),
        "format": "ogg",
        "size_bytes": path.stat().st_size,
    }
    return res
