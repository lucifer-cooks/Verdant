"""VERDANT New World Creation Screen."""

from __future__ import annotations

import math
from pyglet import gl, window

from mc.net.minecraft.client.gui.GuiScreen import GuiScreen
from mc.net.minecraft.client.gui.Gui import Gui
from verdant.menu.buttons import VerdantMenuButton
from verdant.menu.background import VerdantAtmosphericBackground
from verdant.menu.flow import start_verdant_world


class VerdantCreateWorldScreen(GuiScreen):
    """Authoritative screen for creating a new VERDANT survival world."""

    def __init__(self, parent_screen: GuiScreen) -> None:
        self._parent = parent_screen
        self._background = VerdantAtmosphericBackground()
        self.width = 427
        self.height = 240
        self.world_name = "My World"
        self.game_mode = "SURVIVAL"
        self.player_mode = "SINGLEPLAYER"
        self.is_name_focused = True
        self._cursor_counter = 0

    def updateScreen(self) -> None:
        self._cursor_counter += 1
        if self.width > 0 and self.height > 0:
            self._background.update(self.width, self.height)

    def _mouseClicked(self, xm: int, ym: int, button: int) -> None:
        # Check if clicking on World Name input box
        box_w = 210
        box_h = 22
        box_x = self.width // 2 - box_w // 2
        box_y = max(60, self.height // 2 - 60)

        if box_x <= xm < box_x + box_w and box_y <= ym < box_y + box_h:
            self.is_name_focused = True
        else:
            self.is_name_focused = False

        super()._mouseClicked(xm, ym, button)

    def _keyTyped(self, key: int, char: str, motion: int) -> None:
        if key == window.key.ESCAPE:
            self.mc.displayGuiScreen(self._parent)
            return

        if key in (window.key.ENTER, window.key.RETURN):
            if len(self.world_name.strip()) > 0:
                start_verdant_world(self.mc, self.world_name, self.game_mode, self.player_mode)
            return

        if self.is_name_focused:
            if (motion == window.key.MOTION_BACKSPACE or key == window.key.BACKSPACE) and len(self.world_name) > 0:
                self.world_name = self.world_name[:-1]
            elif char:
                allowed = (
                    "abcdefghijklmnopqrstuvwxyz"
                    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    "0123456789 _-!.'()"
                )
                if char in allowed and len(self.world_name) < 32:
                    self.world_name += char

            # Update CREATE WORLD button state
            self._update_create_button()

    def _update_create_button(self) -> None:
        # Button 10 is CREATE WORLD
        for b in self._controlList:
            if b.id == 10:
                b.enabled = len(self.world_name.strip()) > 0

    def initGui(self) -> None:
        self._controlList.clear()

        btn_w = 210
        btn_h = 22
        center_x = self.width // 2
        btn_x = center_x - btn_w // 2

        start_y = max(60, self.height // 2 - 60)
        mode_y = start_y + 36
        player_y = mode_y + 38

        # 0: GAME MODE (SURVIVAL)
        self._controlList.append(
            VerdantMenuButton(0, btn_x, mode_y, btn_w, btn_h, f"GAME MODE: {self.game_mode}")
        )
        # 1: PLAYER MODE (SINGLEPLAYER / MULTIPLAYER)
        self._controlList.append(
            VerdantMenuButton(1, btn_x, player_y, btn_w, btn_h, f"PLAYER MODE: {self.player_mode}")
        )

        # Action buttons at bottom: CREATE WORLD (id=10), BACK (id=11)
        act_w = 100
        act_h = 24
        act_y = player_y + 44
        self._controlList.append(
            VerdantMenuButton(10, center_x - act_w - 5, act_y, act_w, act_h, "CREATE WORLD")
        )
        self._controlList.append(
            VerdantMenuButton(11, center_x + 5, act_y, act_w, act_h, "BACK")
        )

        self._update_create_button()

    def _actionPerformed(self, button: VerdantMenuButton) -> None:
        if button.id == 11:
            # BACK
            self.mc.displayGuiScreen(self._parent)
        elif button.id == 10:
            # CREATE WORLD
            if len(self.world_name.strip()) > 0:
                start_verdant_world(self.mc, self.world_name, self.game_mode, self.player_mode)
        elif button.id == 0:
            # GAME MODE (Survival is the active authoritative mode)
            self.game_mode = "SURVIVAL"
            button.displayString = f"GAME MODE: {self.game_mode}"
        elif button.id == 1:
            # PLAYER MODE toggle
            self.player_mode = "MULTIPLAYER" if self.player_mode == "SINGLEPLAYER" else "SINGLEPLAYER"
            button.displayString = f"PLAYER MODE: {self.player_mode}"

    def drawScreen(self, xm: int, ym: int, renderPartialTicks: float) -> None:
        # 1. Background
        self._background.draw(self.width, self.height)

        font = self._fontRenderer
        center_x = self.width // 2

        # 2. Title
        title_y = max(16, self.height // 2 - 105)
        title_text = "C R E A T E   N E W   W O R L D"
        scale = 1.8

        gl.glPushMatrix()
        gl.glScalef(scale, scale, 1.0)
        scaled_x = center_x / scale
        scaled_y = title_y / scale
        font.drawStringWithShadow(
            title_text,
            int(scaled_x - font.getStringWidth(title_text) / 2),
            int(scaled_y),
            0x4ADE80
        )
        gl.glPopMatrix()

        # Horizon line beneath title
        bar_y = title_y + 20
        bar_half_w = 110
        self._drawGradientRect(center_x - bar_half_w, bar_y, center_x, bar_y + 1, 0x004ADE80, 0xCC4ADE80)
        self._drawGradientRect(center_x, bar_y, center_x + bar_half_w, bar_y + 1, 0xCC4ADE80, 0x004ADE80)

        # 3. Field 1: WORLD NAME
        box_w = 210
        box_h = 22
        box_x = center_x - box_w // 2
        box_y = max(60, self.height // 2 - 60)

        # Label
        font.drawStringWithShadow("WORLD NAME", box_x, box_y - 10, 0xA5D6B6)

        # Text input box border and fill
        border_col = 0xFF4ADE80 if self.is_name_focused else 0xFF243D2C
        fill_col = 0xEE0D1A12 if self.is_name_focused else 0xEE0A150F
        Gui._drawRect(box_x, box_y, box_x + box_w, box_y + box_h, border_col)
        Gui._drawRect(box_x + 1, box_y + 1, box_x + box_w - 1, box_y + box_h - 1, fill_col)

        # Blinking text cursor
        cursor = "_" if (self.is_name_focused and (self._cursor_counter // 8 % 2 == 0)) else ""
        display_str = self.world_name + cursor
        font_col = 0xF0FFF4 if self.is_name_focused else 0xC5DACB
        font.drawStringWithShadow(display_str, box_x + 6, box_y + 6, font_col)

        # 4. Field 2 & 3 Sub-labels
        mode_y = box_y + 36
        desc_y = mode_y + 24
        font.drawStringWithShadow(
            "Survive, gather resources, explore the island.",
            int(center_x - font.getStringWidth("Survive, gather resources, explore the island.") / 2),
            desc_y,
            0x5B7C68
        )

        player_y = mode_y + 38
        player_desc = (
            "Explore and survive the island alone."
            if self.player_mode == "SINGLEPLAYER"
            else "Direct network connection play."
        )
        desc2_y = player_y + 24
        font.drawStringWithShadow(
            player_desc,
            int(center_x - font.getStringWidth(player_desc) / 2),
            desc2_y,
            0x5B7C68
        )

        # 5. Controls
        super().drawScreen(xm, ym, renderPartialTicks)
