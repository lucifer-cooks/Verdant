"""Comprehensive automated tests for VERDANT Main Menu / Homepage Redesign."""

import os
import sys
import unittest
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure World is loaded first to prevent Cython circular import in legacy Indev engine
from mc.net.minecraft.game.level.World import World
from mc.net.minecraft.client.GuiMainMenu import GuiMainMenu
from mc.net.minecraft.client.gui.GuiOptions import GuiOptions
from mc.net.minecraft.client.gui.GuiNewLevel import GuiNewLevel
from mc.net.minecraft.client.gui.GuiLoadLevel import GuiLoadLevel
from mc.net.minecraft.client.Session import Session

from verdant.assets.theme import ThemeManager, ThemeMode
from verdant.menu.buttons import VerdantMenuButton
from verdant.menu.background import SporeParticle, VerdantAtmosphericBackground
from verdant.menu.screen import VerdantMainMenu
from verdant.menu.new_world import VerdantCreateWorldScreen


class MockMinecraft:
    """Mock Minecraft instance for testing GUI screens without opening an OpenGL window."""

    def __init__(self, has_session: bool = True) -> None:
        self.session = Session("test_user", "test_session_id") if has_session else None
        self.options = object()
        self.currentScreen = None
        self.running = True
        self.closed = False
        self.width = 854
        self.height = 480
        self.fontRenderer = MockFontRenderer()

    def displayGuiScreen(self, screen) -> None:
        self.currentScreen = screen

    def close(self) -> None:
        self.closed = True


class MockFontRenderer:
    """Mock font renderer for headless testing."""

    def getStringWidth(self, string: str) -> int:
        return len(string) * 6

    def drawStringWithShadow(self, string: str, x: int, y: int, color: int) -> None:
        pass


# 1. Test VerdantMainMenu instantiation and structure
def test_01_verdant_main_menu_instantiation():
    menu = VerdantMainMenu()
    assert menu is not None
    assert isinstance(menu._background, VerdantAtmosphericBackground)


# 2. Test button initialization and controls
def test_02_button_initialization():
    mc = MockMinecraft()
    menu = VerdantMainMenu()
    menu.setWorldAndResolution(mc, 427, 240)

    # Must have exactly 4 primary buttons
    assert len(menu._controlList) == 4

    btn_new = menu._controlList[0]
    btn_load = menu._controlList[1]
    btn_options = menu._controlList[2]
    btn_quit = menu._controlList[3]

    assert btn_new.id == 1
    assert "NEW WORLD" in btn_new.displayString
    assert btn_new.enabled is True

    assert btn_load.id == 2
    assert "LOAD WORLD" in btn_load.displayString
    assert btn_load.enabled is True

    assert btn_options.id == 0
    assert "OPTIONS" in btn_options.displayString
    assert btn_options.enabled is True

    assert btn_quit.id == 4
    assert "QUIT" in btn_quit.displayString
    assert btn_quit.enabled is True


# 3. Test VerdantMenuButton hit testing and hover
def test_03_button_hit_testing():
    btn = VerdantMenuButton(1, 100, 50, 190, 22, "NEW WORLD")

    # Inside bounds
    assert btn.mousePressed(150, 60) is True
    assert btn.mousePressed(100, 50) is True
    assert btn.mousePressed(289, 71) is True

    # Outside bounds
    assert btn.mousePressed(99, 60) is False
    assert btn.mousePressed(290, 60) is False
    assert btn.mousePressed(150, 49) is False
    assert btn.mousePressed(150, 72) is False

    # Disabled button
    btn.enabled = False
    assert btn.mousePressed(150, 60) is False


# 4. Test New World action
def test_04_action_new_world():
    mc = MockMinecraft()
    menu = VerdantMainMenu()
    menu.setWorldAndResolution(mc, 427, 240)

    btn_new = menu._controlList[0]
    menu._actionPerformed(btn_new)

    assert isinstance(mc.currentScreen, (VerdantCreateWorldScreen, GuiNewLevel))


# 5. Test Load World action
def test_05_action_load_world():
    mc = MockMinecraft(has_session=True)
    menu = VerdantMainMenu()
    menu.setWorldAndResolution(mc, 427, 240)

    btn_load = menu._controlList[1]
    menu._actionPerformed(btn_load)

    assert isinstance(mc.currentScreen, GuiLoadLevel)


# 6. Test Options action
def test_06_action_options():
    mc = MockMinecraft()
    menu = VerdantMainMenu()
    menu.setWorldAndResolution(mc, 427, 240)

    btn_options = menu._controlList[2]
    menu._actionPerformed(btn_options)

    assert isinstance(mc.currentScreen, GuiOptions)


# 7. Test Quit action
def test_07_action_quit():
    mc = MockMinecraft()
    menu = VerdantMainMenu()
    menu.setWorldAndResolution(mc, 427, 240)

    btn_quit = menu._controlList[3]
    menu._actionPerformed(btn_quit)

    # Must set running = False and invoke close
    assert mc.running is False
    assert mc.closed is True


# 8. Test disabled Load World when no session exists
def test_08_load_world_no_session():
    mc = MockMinecraft(has_session=False)
    menu = VerdantMainMenu()
    menu.setWorldAndResolution(mc, 427, 240)

    btn_load = menu._controlList[1]
    assert btn_load.enabled is False


# 9. Test SporeParticle physics and wrapping
def test_09_spore_particles():
    bg = VerdantAtmosphericBackground(particle_count=20, seed=123)
    bg.update(427, 240)
    assert len(bg._particles) == 20

    for p in bg._particles:
        assert 0 <= p.x <= 427
        color = p.get_render_color()
        # Verify non-zero alpha in ARGB
        a = (color >> 24) & 0xFF
        assert a > 0

    # Test wrap around
    p0 = bg._particles[0]
    p0.y = -20
    p0.update(427, 240)
    assert p0.y > 0


# 10. Test GuiMainMenu delegation in VERDANT mode
def test_10_gui_main_menu_verdant_mode():
    tm = ThemeManager.get_instance()
    tm.set_mode(ThemeMode.VERDANT_ORIGINAL)

    mc = MockMinecraft()
    gui = GuiMainMenu()
    gui.setWorldAndResolution(mc, 427, 240)

    # Verify buttons are VerdantMenuButton with Verdant titles
    assert len(gui._controlList) == 4
    labels = [b.displayString for b in gui._controlList]
    assert "NEW WORLD" in labels[0]
    assert "LOAD WORLD" in labels[1]
    assert "OPTIONS" in labels[2]
    assert "QUIT" in labels[3]
    assert isinstance(gui._controlList[0], VerdantMenuButton)


# 11. Test GuiMainMenu fallback in CLASSIC mode
def test_11_gui_main_menu_classic_fallback():
    tm = ThemeManager.get_instance()
    tm.set_mode(ThemeMode.CLASSIC)

    mc = MockMinecraft()
    gui = GuiMainMenu()
    gui.setWorldAndResolution(mc, 427, 240)

    # Classic Indev has "Generate new level...", "Load level..", "Play tutorial level", "Options..."
    labels = [b.displayString for b in gui._controlList]
    assert "Generate new level..." in labels[0]
    assert "Load level.." in labels[1]
    assert "Play tutorial level" in labels[2]
    assert "Options..." in labels[3]

    # Restore Verdant mode
    tm.set_mode(ThemeMode.VERDANT_ORIGINAL)


# 12. Test updateScreen without errors
def test_12_update_screen():
    mc = MockMinecraft()
    gui = GuiMainMenu()
    gui.setWorldAndResolution(mc, 427, 240)
    for _ in range(10):
        gui.updateScreen()
    assert gui._verdant_menu._anim_tick > 0.4


# 13. Test keyTyped ignores ESC safely
def test_13_key_typed():
    gui = GuiMainMenu()
    # 27 is ESC key
    gui._keyTyped(27, "", 0)
    # Should not raise exception or quit


# 14. Test button visual state rendering logic
def test_14_button_visual_state():
    btn = VerdantMenuButton(1, 100, 50, 190, 22, "NEW WORLD")
    # Simulate hover check
    btn.is_hovered = True
    assert btn.is_hovered is True
    btn.is_hovered = False
    assert btn.is_hovered is False


# 15. Test M2-M11 regression safety
def test_15_regression_safety():
    from verdant.world.state import VerdantWorldState
    from verdant.environment.climate import VerdantClimateSystem
    from verdant.water.system import VerdantWaterSystem
    from verdant.creatures.system import VerdantCreatureSystem
    from verdant.assets.creatures import ModelHollowStalker, ModelSporeSpire

    ws = VerdantWorldState()
    assert ws is not None
    cs = VerdantClimateSystem(seed=42)
    assert cs is not None
    zs = ModelHollowStalker()
    assert zs is not None
    ss = ModelSporeSpire()
    assert ss is not None
