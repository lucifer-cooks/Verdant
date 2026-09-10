"""Automated test suite for VERDANT New World Creation Flow Redesign."""

import os
import sys
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Pre-import World to prevent Cython circular import in legacy Indev engine
from mc.net.minecraft.game.level.World import World
from mc.net.minecraft.client.gui.GuiNewLevel import GuiNewLevel
from mc.net.minecraft.client.GuiMainMenu import GuiMainMenu
from mc.net.minecraft.client.Session import Session

from verdant.assets.theme import ThemeManager, ThemeMode
from verdant.menu.new_world import VerdantCreateWorldScreen
from verdant.menu.flow import start_verdant_world


class MockMinecraftForWorldGen:
    """Mock client for testing world creation flow without graphics hardware."""

    def __init__(self) -> None:
        self.session = Session("test_pilot", "session_123")
        self.currentScreen = None
        self.theWorld = None
        self.running = True
        self.in_focus = False
        self.last_gen_params = None
        self.fontRenderer = MockFontRenderer()
        self.width = 854
        self.height = 480

        from verdant.world.state import VerdantWorldState
        self.verdant_world_state = VerdantWorldState()

    def displayGuiScreen(self, screen) -> None:
        self.currentScreen = screen

    def setIngameFocus(self) -> None:
        self.in_focus = True

    def generateLevel(self, size: int, shape: int, levelType: int, theme: int) -> None:
        self.last_gen_params = {
            "size": size,
            "shape": shape,
            "levelType": levelType,
            "theme": theme,
        }
        w = World()
        w.generate(16, 16, 16, bytearray(16 * 16 * 16), bytearray(16 * 16 * 16))
        self.theWorld = w


class MockFontRenderer:
    def getStringWidth(self, string: str) -> int:
        return len(string) * 6

    def drawStringWithShadow(self, string: str, x: int, y: int, color: int) -> None:
        pass


# 1. Test VerdantCreateWorldScreen instantiation and defaults
def test_01_screen_defaults():
    parent = object()
    screen = VerdantCreateWorldScreen(parent)
    assert screen._parent is parent
    assert screen.world_name == "My World"
    assert screen.game_mode == "SURVIVAL"
    assert screen.player_mode == "SINGLEPLAYER"
    assert screen.is_name_focused is True


# 2. Test control list population and layout
def test_02_controls_population():
    mc = MockMinecraftForWorldGen()
    parent = object()
    screen = VerdantCreateWorldScreen(parent)
    screen.setWorldAndResolution(mc, 427, 240)

    # Must contain Game Mode (0), Player Mode (1), Create World (10), Back (11)
    control_ids = [b.id for b in screen._controlList]
    assert 0 in control_ids
    assert 1 in control_ids
    assert 10 in control_ids
    assert 11 in control_ids

    btn_create = [b for b in screen._controlList if b.id == 10][0]
    btn_back = [b for b in screen._controlList if b.id == 11][0]
    assert btn_create.enabled is True
    assert btn_create.displayString == "CREATE WORLD"
    assert btn_back.displayString == "BACK"


# 3. Test text field editing (append, backspace, trim)
def test_03_text_editing():
    from pyglet import window
    parent = object()
    screen = VerdantCreateWorldScreen(parent)
    screen._controlList = []
    screen.initGui()

    # Backspace "My World" down to ""
    for _ in range(len("My World")):
        screen._keyTyped(window.key.BACKSPACE, "", window.key.MOTION_BACKSPACE)
    assert screen.world_name == ""

    # When empty, CREATE button must be disabled
    btn_create = [b for b in screen._controlList if b.id == 10][0]
    assert btn_create.enabled is False

    # Type new name "Verdant Island"
    for ch in "Verdant Island":
        screen._keyTyped(0, ch, 0)
    assert screen.world_name == "Verdant Island"
    assert btn_create.enabled is True


# 4. Test Game Mode and Player Mode actions
def test_04_mode_actions():
    mc = MockMinecraftForWorldGen()
    screen = VerdantCreateWorldScreen(object())
    screen.setWorldAndResolution(mc, 427, 240)

    btn_player = [b for b in screen._controlList if b.id == 1][0]
    assert screen.player_mode == "SINGLEPLAYER"

    # Toggle to MULTIPLAYER
    screen._actionPerformed(btn_player)
    assert screen.player_mode == "MULTIPLAYER"
    assert "MULTIPLAYER" in btn_player.displayString

    # Toggle back to SINGLEPLAYER
    screen._actionPerformed(btn_player)
    assert screen.player_mode == "SINGLEPLAYER"
    assert "SINGLEPLAYER" in btn_player.displayString


# 5. Test Back action
def test_05_back_action():
    mc = MockMinecraftForWorldGen()
    parent = object()
    screen = VerdantCreateWorldScreen(parent)
    screen.setWorldAndResolution(mc, 427, 240)

    btn_back = [b for b in screen._controlList if b.id == 11][0]
    screen._actionPerformed(btn_back)
    assert mc.currentScreen is parent


# 6. Test start_verdant_world orchestrator
def test_06_start_verdant_world():
    mc = MockMinecraftForWorldGen()
    start_verdant_world(mc, "Emerald Isle", "SURVIVAL", "SINGLEPLAYER")

    assert mc.last_gen_params is not None
    # Must use Island parameters (levelType=1)
    assert mc.last_gen_params["levelType"] == 1
    assert mc.last_gen_params["size"] == 1
    assert mc.last_gen_params["shape"] == 0
    assert mc.theWorld is not None
    assert mc.theWorld.name == "Emerald Isle"
    assert mc.verdant_world_state.world_name == "Emerald Isle"
    assert mc.currentScreen is None
    assert mc.in_focus is True


# 7. Test Create World button triggers start_verdant_world
def test_07_create_button_action():
    mc = MockMinecraftForWorldGen()
    screen = VerdantCreateWorldScreen(object())
    screen.setWorldAndResolution(mc, 427, 240)
    screen.world_name = "Paradise Alpha"

    btn_create = [b for b in screen._controlList if b.id == 10][0]
    screen._actionPerformed(btn_create)

    assert mc.last_gen_params is not None
    assert mc.theWorld.name == "Paradise Alpha"


# 8. Test GuiNewLevel delegation in VERDANT mode
def test_08_gui_new_level_verdant_mode():
    tm = ThemeManager.get_instance()
    tm.set_mode(ThemeMode.VERDANT_ORIGINAL)

    mc = MockMinecraftForWorldGen()
    parent = object()
    gui = GuiNewLevel(parent)
    gui.setWorldAndResolution(mc, 427, 240)

    # In Verdant mode, control list has Verdant controls
    control_ids = [b.id for b in gui._controlList]
    assert 10 in control_ids  # CREATE WORLD
    assert 11 in control_ids  # BACK

    labels = " ".join([b.displayString for b in gui._controlList])
    assert "CREATE WORLD" in labels
    assert "Type:" not in labels
    assert "Inland" not in labels
    assert "Floating" not in labels
    assert "Flat" not in labels


# 9. Test GuiNewLevel fallback in CLASSIC mode
def test_09_gui_new_level_classic_mode():
    tm = ThemeManager.get_instance()
    tm.set_mode(ThemeMode.CLASSIC)

    mc = MockMinecraftForWorldGen()
    parent = object()
    gui = GuiNewLevel(parent)
    gui.setWorldAndResolution(mc, 427, 240)

    # In classic mode, legacy controls appear
    labels = " ".join([b.displayString for b in gui._controlList])
    assert "Type:" in labels
    assert "Shape:" in labels
    assert "Size:" in labels
    assert "Theme:" in labels

    # Restore Verdant mode
    tm.set_mode(ThemeMode.VERDANT_ORIGINAL)


# 10. Test Enter / Return key submits creation
def test_10_enter_key_submit():
    mc = MockMinecraftForWorldGen()
    screen = VerdantCreateWorldScreen(object())
    screen.setWorldAndResolution(mc, 427, 240)
    screen.world_name = "Quick Enter"

    # Pyglet Enter key is 65293 (or 10)
    screen._keyTyped(65293, "\r", 0)
    assert mc.theWorld is not None
    assert mc.theWorld.name == "Quick Enter"


# 11. Test Escape key goes back
def test_11_escape_key_back():
    mc = MockMinecraftForWorldGen()
    parent = object()
    screen = VerdantCreateWorldScreen(parent)
    screen.setWorldAndResolution(mc, 427, 240)

    # 65307 is ESC
    screen._keyTyped(65307, "", 0)
    assert mc.currentScreen is parent


# 12. Test mouse clicking outside text field unfocuses it
def test_12_focus_handling():
    screen = VerdantCreateWorldScreen(object())
    screen.setWorldAndResolution(MockMinecraftForWorldGen(), 427, 240)
    screen.is_name_focused = True

    # Click at top left corner (outside text box)
    screen._mouseClicked(10, 10, 0)
    assert screen.is_name_focused is False

    # Click in text box area (center x, y=max(60, 120-60)=60)
    box_x = 427 // 2
    screen._mouseClicked(box_x, 65, 0)
    assert screen.is_name_focused is True


# 13. Test updateScreen tick increments
def test_13_update_screen_ticks():
    screen = VerdantCreateWorldScreen(object())
    screen.setWorldAndResolution(MockMinecraftForWorldGen(), 427, 240)
    for _ in range(5):
        screen.updateScreen()
    assert screen._cursor_counter == 5


# 14. Test MainMenu to CreateWorldScreen flow
def test_14_main_menu_to_new_world():
    from verdant.menu.screen import VerdantMainMenu
    mc = MockMinecraftForWorldGen()
    main_menu = VerdantMainMenu()
    main_menu.setWorldAndResolution(mc, 427, 240)

    # Click NEW WORLD (button id=1)
    btn_new = [b for b in main_menu._controlList if b.id == 1][0]
    main_menu._actionPerformed(btn_new)

    assert isinstance(mc.currentScreen, VerdantCreateWorldScreen)
    assert mc.currentScreen._parent is main_menu


# 15. Regression safety check across M2–M11 systems
def test_15_regression_safety():
    from verdant.world.state import VerdantWorldState
    from verdant.environment.climate import VerdantClimateSystem
    from verdant.water.system import VerdantWaterSystem
    from verdant.creatures.system import VerdantCreatureSystem
    from verdant.assets.creatures import ModelHollowStalker, ModelSporeSpire

    ws = VerdantWorldState()
    assert ws is not None
    cs = VerdantClimateSystem(seed=101)
    assert cs is not None
    assert ModelHollowStalker() is not None
    assert ModelSporeSpire() is not None
