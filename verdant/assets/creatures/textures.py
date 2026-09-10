"""Game-ready texture generation and extraction for Verdant creature identities."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    from PIL import Image, ImageDraw, ImageFilter
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

from verdant.assets.paths import ASSETS_DIR, PROJECT_ROOT, VERDANT_THEME_DIR

CREATURES_THEME_DIR = VERDANT_THEME_DIR / "creatures"
PLAYER_TEXTURE_DIR = CREATURES_THEME_DIR / "player"
PASSIVE_TEXTURE_DIR = CREATURES_THEME_DIR / "passive"
HOSTILE_TEXTURE_DIR = CREATURES_THEME_DIR / "hostile"

SOURCE_IMAGES_DIR = PROJECT_ROOT / "verdant"


def _extract_and_paste(
    src_im: Image.Image,
    crop_box: Tuple[int, int, int, int],
    dst_im: Image.Image,
    paste_pos: Tuple[int, int],
    target_size: Tuple[int, int],
) -> None:
    """Helper to crop a region from source reference sheet, resize, and paste onto game-ready canvas."""
    try:
        cropped = src_im.crop(crop_box)
        resized = cropped.resize(target_size, Image.Resampling.LANCZOS)
        dst_im.paste(resized, paste_pos, resized if resized.mode == "RGBA" else None)
    except Exception:
        pass


def build_wayfarer_texture() -> Image.Image:
    """Build the 64x64 game-ready Verdant Wayfarer texture from the user's reference sheet."""
    target_path = PLAYER_TEXTURE_DIR / "wayfarer.png"
    PLAYER_TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    
    tex = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    src_file = SOURCE_IMAGES_DIR / "wayfarer.png"

    if _HAS_PIL and src_file.is_file():
        src = Image.open(src_file).convert("RGBA")
        
        # 1. Head (0, 0, 32, 16)
        # Head Top at (8, 0, 8, 8)
        _extract_and_paste(src, (11, 10, 185, 180), tex, (8, 0), (8, 8))
        # Head Bottom at (16, 0, 8, 8)
        _extract_and_paste(src, (11, 10, 185, 180), tex, (16, 0), (8, 8))
        # Head Right at (0, 8, 8, 8)
        _extract_and_paste(src, (730, 115, 875, 335), tex, (0, 8), (8, 8))
        # Head Front at (8, 8, 8, 8)
        _extract_and_paste(src, (185, 10, 410, 335), tex, (8, 8), (8, 8))
        # Head Left at (16, 8, 8, 8)
        _extract_and_paste(src, (410, 80, 560, 335), tex, (16, 8), (8, 8))
        # Head Back at (24, 8, 8, 8)
        _extract_and_paste(src, (560, 115, 730, 335), tex, (24, 8), (8, 8))

        # 2. Torso (16, 16, 24, 16)
        # Torso Top at (20, 16, 8, 4)
        _extract_and_paste(src, (160, 405, 395, 520), tex, (20, 16), (8, 4))
        # Torso Bottom at (28, 16, 8, 4)
        _extract_and_paste(src, (160, 700, 395, 805), tex, (28, 16), (8, 4))
        # Torso Right at (16, 20, 4, 12)
        _extract_and_paste(src, (395, 405, 520, 805), tex, (16, 20), (4, 12))
        # Torso Front at (20, 20, 8, 12)
        _extract_and_paste(src, (160, 405, 395, 805), tex, (20, 20), (8, 12))
        # Torso Left at (28, 20, 4, 12)
        _extract_and_paste(src, (36, 405, 160, 805), tex, (28, 20), (4, 12))
        # Torso Back at (32, 20, 8, 12)
        _extract_and_paste(src, (520, 405, 755, 805), tex, (32, 20), (8, 12))

        # 3. Right Arm (40, 16, 16, 16)
        _extract_and_paste(src, (895, 60, 1040, 680), tex, (44, 20), (4, 12))
        _extract_and_paste(src, (895, 60, 1040, 680), tex, (40, 20), (4, 12))
        _extract_and_paste(src, (895, 60, 1040, 680), tex, (48, 20), (4, 12))
        _extract_and_paste(src, (895, 60, 1040, 680), tex, (52, 20), (4, 12))
        _extract_and_paste(src, (895, 60, 950, 120), tex, (44, 16), (4, 4))
        _extract_and_paste(src, (895, 620, 950, 680), tex, (48, 16), (4, 4))

        # 4. Left Arm (32, 48, 16, 16)
        _extract_and_paste(src, (1100, 60, 1235, 680), tex, (36, 52), (4, 12))
        _extract_and_paste(src, (1100, 60, 1235, 680), tex, (32, 52), (4, 12))
        _extract_and_paste(src, (1100, 60, 1235, 680), tex, (40, 52), (4, 12))
        _extract_and_paste(src, (1100, 60, 1235, 680), tex, (44, 52), (4, 12))
        _extract_and_paste(src, (1100, 60, 1150, 120), tex, (36, 48), (4, 4))
        _extract_and_paste(src, (1100, 620, 1150, 680), tex, (40, 48), (4, 4))

        # 5. Right Leg (0, 16, 16, 16)
        _extract_and_paste(src, (36, 860, 430, 1195), tex, (4, 20), (4, 12))
        _extract_and_paste(src, (36, 860, 430, 1195), tex, (0, 20), (4, 12))
        _extract_and_paste(src, (36, 860, 430, 1195), tex, (8, 20), (4, 12))
        _extract_and_paste(src, (36, 860, 430, 1195), tex, (12, 20), (4, 12))
        _extract_and_paste(src, (36, 860, 120, 920), tex, (4, 16), (4, 4))
        _extract_and_paste(src, (36, 1130, 120, 1195), tex, (8, 16), (4, 4))

        # 6. Left Leg (16, 48, 16, 16)
        _extract_and_paste(src, (470, 860, 850, 1195), tex, (20, 52), (4, 12))
        _extract_and_paste(src, (470, 860, 850, 1195), tex, (16, 52), (4, 12))
        _extract_and_paste(src, (470, 860, 850, 1195), tex, (24, 52), (4, 12))
        _extract_and_paste(src, (470, 860, 850, 1195), tex, (28, 52), (4, 12))
        _extract_and_paste(src, (470, 860, 550, 920), tex, (20, 48), (4, 4))
        _extract_and_paste(src, (470, 1130, 550, 1195), tex, (24, 48), (4, 4))

        # 7. Hood Cowl Overlay / 3D Headwear (32, 0, 32, 16)
        _extract_and_paste(src, (11, 10, 185, 180), tex, (40, 0), (8, 8))
        _extract_and_paste(src, (11, 10, 185, 180), tex, (48, 0), (8, 8))
        _extract_and_paste(src, (730, 115, 875, 335), tex, (32, 8), (8, 8))
        _extract_and_paste(src, (185, 10, 410, 335), tex, (40, 8), (8, 8))
        _extract_and_paste(src, (410, 80, 560, 335), tex, (48, 8), (8, 8))
        _extract_and_paste(src, (560, 115, 730, 335), tex, (56, 8), (8, 8))
    else:
        # Programmatic procedural synthesis from original palette
        draw = ImageDraw.Draw(tex)
        # Green hood
        draw.rectangle([0, 0, 63, 15], fill=(58, 86, 44, 255))
        # Mask and face
        draw.rectangle([8, 8, 15, 15], fill=(70, 98, 52, 255))
        draw.rectangle([10, 11, 11, 12], fill=(80, 160, 90, 255))
        draw.rectangle([13, 11, 14, 12], fill=(80, 160, 90, 255))
        draw.rectangle([8, 13, 15, 15], fill=(42, 40, 38, 255))
        # Explorer tunic
        draw.rectangle([16, 16, 39, 31], fill=(225, 220, 205, 255))
        draw.rectangle([20, 24, 27, 26], fill=(110, 75, 45, 255))
        # Boots and vambraces
        draw.rectangle([0, 16, 15, 31], fill=(85, 55, 35, 255))
        draw.rectangle([40, 16, 55, 31], fill=(95, 65, 40, 255))

    tex.save(target_path, "PNG")
    return tex


def build_mossback_boar_texture() -> Image.Image:
    """Build the 64x32 game-ready Verdant Mossback Boar texture from the user's reference sheet."""
    target_path = PASSIVE_TEXTURE_DIR / "mossback_boar.png"
    PASSIVE_TEXTURE_DIR.mkdir(parents=True, exist_ok=True)

    tex = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    src_file = SOURCE_IMAGES_DIR / "mossback_boar.png"

    if _HAS_PIL and src_file.is_file():
        src = Image.open(src_file).convert("RGBA")
        # 1. Boar Head (0, 0, 24, 16): Snout + tusks + eyes
        # Top/Bottom
        _extract_and_paste(src, (20, 100, 260, 200), tex, (6, 0), (8, 6))
        _extract_and_paste(src, (20, 300, 260, 430), tex, (14, 0), (8, 6))
        # Front face with tusks and eyes
        _extract_and_paste(src, (20, 100, 260, 430), tex, (6, 6), (8, 8))
        # Head sides
        _extract_and_paste(src, (20, 120, 140, 430), tex, (0, 6), (6, 8))
        _extract_and_paste(src, (140, 120, 260, 430), tex, (14, 6), (6, 8))
        _extract_and_paste(src, (20, 100, 260, 430), tex, (20, 6), (6, 8))

        # 2. Boar Body (28, 0, 36, 18): Hunched spine with moss ridge
        _extract_and_paste(src, (260, 120, 595, 220), tex, (36, 0), (10, 8))
        _extract_and_paste(src, (260, 300, 595, 430), tex, (46, 0), (10, 8))
        _extract_and_paste(src, (260, 120, 595, 430), tex, (28, 8), (8, 10))
        _extract_and_paste(src, (260, 120, 595, 430), tex, (36, 8), (10, 10))
        _extract_and_paste(src, (595, 140, 790, 430), tex, (46, 8), (8, 10))
        _extract_and_paste(src, (595, 140, 790, 430), tex, (54, 8), (10, 10))

        # 3. Four Legs (0, 16, 24, 16): Cloven hooves + moss knees
        _extract_and_paste(src, (895, 95, 980, 690), tex, (0, 16), (4, 12))
        _extract_and_paste(src, (980, 95, 1065, 690), tex, (4, 16), (4, 12))
        _extract_and_paste(src, (1065, 95, 1150, 690), tex, (8, 16), (4, 12))
        _extract_and_paste(src, (1150, 95, 1235, 690), tex, (12, 16), (4, 12))
    else:
        # Fallback synthesis with exact boar palette
        draw = ImageDraw.Draw(tex)
        draw.rectangle([0, 0, 63, 15], fill=(74, 51, 34, 255))
        draw.rectangle([6, 6, 13, 13], fill=(85, 60, 40, 255))
        # Tusks
        draw.rectangle([6, 11, 7, 13], fill=(232, 222, 192, 255))
        draw.rectangle([12, 11, 13, 13], fill=(232, 222, 192, 255))
        # Moss back
        draw.rectangle([28, 0, 63, 7], fill=(90, 125, 40, 255))
        # Legs
        draw.rectangle([0, 16, 23, 27], fill=(65, 45, 30, 255))
        draw.rectangle([0, 26, 23, 27], fill=(45, 40, 38, 255))

    tex.save(target_path, "PNG")
    return tex


def build_hollow_stalker_texture() -> Image.Image:
    """Build the 64x32 game-ready Verdant Hollow Stalker texture from the user's skin."""
    target_path = HOSTILE_TEXTURE_DIR / "hollow_stalker.png"
    HOSTILE_TEXTURE_DIR.mkdir(parents=True, exist_ok=True)

    src_file = SOURCE_IMAGES_DIR / "hollow_stalker.png"
    if _HAS_PIL and src_file.is_file():
        src = Image.open(src_file).convert("RGBA")
        if src.size == (64, 64):
            # Top half 64x32 contains the full biped skin; bottom half is empty padding
            tex = src.crop((0, 0, 64, 32))
        elif src.size == (64, 32):
            tex = src.copy()
        else:
            tex = src.resize((64, 32), Image.Resampling.NEAREST)
    else:
        tex = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(tex)
        draw.rectangle([0, 0, 31, 15], fill=(50, 65, 40, 255))
        draw.rectangle([8, 8, 15, 15], fill=(20, 18, 16, 255))
        draw.point([(10, 11), (13, 11)], fill=(245, 195, 50, 255))
        draw.rectangle([16, 16, 39, 31], fill=(46, 39, 34, 255))
        draw.rectangle([40, 16, 55, 31], fill=(60, 50, 40, 255))
        draw.rectangle([0, 16, 15, 31], fill=(46, 39, 34, 255))

    tex.save(target_path, "PNG")
    return tex


def build_spore_spire_texture() -> Image.Image:
    """Build the 64x32 game-ready Verdant Spore Spire texture from the user's skin."""
    target_path = HOSTILE_TEXTURE_DIR / "spore_spire.png"
    HOSTILE_TEXTURE_DIR.mkdir(parents=True, exist_ok=True)

    src_file = SOURCE_IMAGES_DIR / "spore_spire.png"
    if _HAS_PIL and src_file.is_file():
        src = Image.open(src_file).convert("RGBA")
        if src.size == (64, 32):
            tex = src.copy()
        else:
            tex = src.resize((64, 32), Image.Resampling.NEAREST)
    else:
        tex = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(tex)
        draw.rectangle([0, 0, 31, 15], fill=(96, 124, 60, 255))
        draw.rectangle([32, 0, 63, 15], fill=(176, 168, 148, 255))
        draw.rectangle([0, 16, 31, 31], fill=(138, 130, 112, 255))

    tex.save(target_path, "PNG")
    return tex


def build_cloud_ram_texture() -> Image.Image:
    """Build the 64x32 game-ready Verdant Cloud-Ram texture."""
    target_path = PASSIVE_TEXTURE_DIR / "cloud_ram.png"
    PASSIVE_TEXTURE_DIR.mkdir(parents=True, exist_ok=True)

    tex = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tex)
    
    # 1. Slender head with curved dark crest horns
    # Head base (warm alabaster / grey muzzle)
    draw.rectangle([0, 0, 23, 15], fill=(225, 218, 204, 255))
    draw.rectangle([6, 8, 13, 13], fill=(240, 234, 222, 255))
    # Soft muzzle
    draw.rectangle([8, 12, 11, 13], fill=(160, 150, 142, 255))
    # Eyes
    draw.point([(7, 9), (12, 9)], fill=(68, 56, 48, 255))
    # Dark curved horn spirals
    draw.rectangle([4, 2, 7, 5], fill=(68, 56, 48, 255))
    draw.rectangle([12, 2, 15, 5], fill=(68, 56, 48, 255))
    draw.point([(3, 4), (16, 4)], fill=(43, 34, 28, 255))

    # 2. Slender meadow-strider body
    draw.rectangle([24, 0, 63, 17], fill=(215, 208, 195, 255))
    
    # 3. Fluffy fleece mantle overlay
    draw.rectangle([26, 2, 60, 15], fill=(244, 239, 228, 255))
    # Subtle fleece texture shading
    for y in range(4, 15, 2):
        for x in range(28, 58, 4):
            draw.point([(x, y), (x + 1, y + 1)], fill=(226, 218, 200, 255))

    # 4. Slender high-stepping cloven legs
    draw.rectangle([0, 16, 23, 31], fill=(185, 175, 162, 255))
    # Dark cloven hooves
    draw.rectangle([0, 29, 23, 31], fill=(55, 45, 38, 255))

    tex.save(target_path, "PNG")
    return tex


def build_briar_reaver_texture() -> Image.Image:
    """Build the 64x32 game-ready Verdant Briar Reaver texture."""
    target_path = HOSTILE_TEXTURE_DIR / "briar_reaver.png"
    HOSTILE_TEXTURE_DIR.mkdir(parents=True, exist_ok=True)

    tex = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tex)

    # 1. Thorn skull with branch antlers
    draw.rectangle([0, 0, 31, 15], fill=(195, 185, 168, 255))
    # Dark hollow eye sockets
    draw.rectangle([8, 8, 15, 15], fill=(18, 14, 12, 255))
    draw.point([(9, 10), (10, 10), (13, 10), (14, 10)], fill=(32, 24, 18, 255))
    # Antler thorn branches
    draw.line([(8, 4), (4, 1)], fill=(65, 48, 34, 255))
    draw.line([(15, 4), (19, 1)], fill=(65, 48, 34, 255))

    # 2. Narrow ribcage interlaced with briar thorns
    draw.rectangle([16, 16, 39, 31], fill=(175, 165, 148, 255))
    # Thorny interlacing
    for y in [19, 22, 25, 28]:
        draw.line([(20, y), (27, y)], fill=(58, 44, 32, 255))

    # 3. Limbs with thorn spines
    draw.rectangle([40, 16, 55, 31], fill=(185, 175, 158, 255))
    draw.rectangle([0, 16, 15, 31], fill=(185, 175, 158, 255))
    # Dark thorn spikes
    draw.point([(42, 22), (53, 24), (2, 22), (13, 25)], fill=(40, 30, 22, 255))

    tex.save(target_path, "PNG")
    return tex


def build_skitterer_texture() -> Image.Image:
    """Build the 64x32 game-ready Verdant Chittering Skitterer texture."""
    target_path = HOSTILE_TEXTURE_DIR / "skitterer.png"
    HOSTILE_TEXTURE_DIR.mkdir(parents=True, exist_ok=True)

    tex = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tex)

    # 1. Flattened dark chitinous carapace
    draw.rectangle([0, 0, 23, 15], fill=(30, 26, 24, 255))
    # Cluster of glowing amber eyes
    draw.point([(8, 8), (9, 8), (14, 8), (15, 8)], fill=(255, 170, 34, 255))
    draw.point([(10, 9), (13, 9)], fill=(255, 119, 17, 255))
    draw.point([(9, 7), (14, 7)], fill=(255, 204, 68, 255))

    # 2. Spiny posterior abdomen
    draw.rectangle([24, 0, 63, 17], fill=(42, 36, 32, 255))
    # Abdominal chitin ridges and spine accents
    for x in [30, 36, 42, 48, 54]:
        draw.line([(x, 3), (x, 14)], fill=(24, 20, 18, 255))
        draw.point([(x, 2), (x, 15)], fill=(65, 52, 45, 255))

    # 3. Multi-jointed legs & curved chelicerae mandibles
    draw.rectangle([0, 16, 63, 31], fill=(26, 22, 20, 255))
    # Ivory mandible tips
    draw.point([(6, 17), (7, 17), (16, 17), (17, 17)], fill=(230, 220, 200, 255))
    # Leg joint banding
    for x in range(4, 60, 8):
        draw.line([(x, 22), (x + 2, 22)], fill=(50, 42, 36, 255))

    tex.save(target_path, "PNG")
    return tex


def ensure_all_creature_textures() -> Dict[str, Path]:
    """Ensure all 7 original Verdant creature textures exist on disk."""
    paths = {
        "wayfarer": PLAYER_TEXTURE_DIR / "wayfarer.png",
        "mossback_boar": PASSIVE_TEXTURE_DIR / "mossback_boar.png",
        "cloud_ram": PASSIVE_TEXTURE_DIR / "cloud_ram.png",
        "hollow_stalker": HOSTILE_TEXTURE_DIR / "hollow_stalker.png",
        "briar_reaver": HOSTILE_TEXTURE_DIR / "briar_reaver.png",
        "spore_spire": HOSTILE_TEXTURE_DIR / "spore_spire.png",
        "skitterer": HOSTILE_TEXTURE_DIR / "skitterer.png",
    }

    if not paths["wayfarer"].is_file():
        build_wayfarer_texture()
    if not paths["mossback_boar"].is_file():
        build_mossback_boar_texture()
    if not paths["cloud_ram"].is_file():
        build_cloud_ram_texture()
    if not paths["hollow_stalker"].is_file():
        build_hollow_stalker_texture()
    if not paths["briar_reaver"].is_file():
        build_briar_reaver_texture()
    if not paths["spore_spire"].is_file():
        build_spore_spire_texture()
    if not paths["skitterer"].is_file():
        build_skitterer_texture()

    return paths
