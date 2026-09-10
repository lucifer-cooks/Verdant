"""VERDANT Main Menu / Homepage Screen."""

from __future__ import annotations

import math
from pyglet import gl

from mc.net.minecraft.client.gui.GuiScreen import GuiScreen
from mc.net.minecraft.client.gui.GuiOptions import GuiOptions
from mc.net.minecraft.client.gui.GuiNewLevel import GuiNewLevel
from mc.net.minecraft.client.gui.GuiLoadLevel import GuiLoadLevel
from verdant.menu.buttons import VerdantMenuButton
from verdant.menu.background import VerdantAtmosphericBackground
from verdant.menu.new_world import VerdantCreateWorldScreen


class VerdantMainMenu(GuiScreen):
    """Authoritative homepage and main menu for VERDANT."""

    def __init__(self) -> None:
        self._background = VerdantAtmosphericBackground()
        self._anim_tick = 0.0

    def updateScreen(self) -> None:
        self._anim_tick += 0.05
        if self.width > 0 and self.height > 0:
            self._background.update(self.width, self.height)

    def _keyTyped(self, key: int, char: str, motion: int) -> None:
        # Ignore ESC on main menu to avoid quitting unintentionally
        pass

    def initGui(self) -> None:
        self._controlList.clear()

        btn_w = 190
        btn_h = 22
        spacing = 26
        btn_x = self.width // 2 - btn_w // 2
        start_y = max(92, self.height // 2 - 35)

        # 1. NEW WORLD
        self._controlList.append(
            VerdantMenuButton(1, btn_x, start_y, btn_w, btn_h, "NEW WORLD")
        )
        # 2. LOAD WORLD
        self._controlList.append(
            VerdantMenuButton(2, btn_x, start_y + spacing, btn_w, btn_h, "LOAD WORLD")
        )
        # 3. OPTIONS
        self._controlList.append(
            VerdantMenuButton(0, btn_x, start_y + spacing * 2, btn_w, btn_h, "OPTIONS")
        )
        # 4. QUIT
        self._controlList.append(
            VerdantMenuButton(4, btn_x, start_y + spacing * 3, btn_w, btn_h, "QUIT")
        )

        # Check session support for Load World
        if self.mc is not None and not getattr(self.mc, "session", None):
            self._controlList[1].enabled = False

    def _actionPerformed(self, button: VerdantMenuButton) -> None:
        if button.id == 0:
            # OPTIONS
            self.mc.displayGuiScreen(GuiOptions(self, self.mc.options))
        elif button.id == 1:
            # NEW WORLD
            self.mc.displayGuiScreen(VerdantCreateWorldScreen(self))
        elif button.id == 2:
            # LOAD WORLD
            if getattr(self.mc, "session", None):
                self.mc.displayGuiScreen(GuiLoadLevel(self))
        elif button.id == 4:
            # QUIT
            self.mc.running = False
            if hasattr(self.mc, "close"):
                try:
                    self.mc.close()
                except Exception:
                    pass

    def drawScreen(self, xm: int, ym: int, renderPartialTicks: float) -> None:
        # 1. Draw atmospheric background (gradient + vignette + floating spores)
        self._background.draw(self.width, self.height)

        font = self._fontRenderer
        center_x = self.width // 2
        title_y = max(24, self.height // 2 - 95)

        # 2. Render VERDANT Title with styled letter spacing and emerald-tinted drop shadow
        title_text = "V  E  R  D  A  N  T"
        scale = 2.4

        gl.glPushMatrix()
        gl.glScalef(scale, scale, 1.0)
        scaled_x = (center_x / scale)
        scaled_y = (title_y / scale)

        font.drawStringWithShadow(
            title_text,
            int(scaled_x - font.getStringWidth(title_text) / 2),
            int(scaled_y),
            0x4ADE80  # Vibrant emerald bio-glow
        )
        gl.glPopMatrix()

        # 3. Elegant glowing horizon accent bar below title
        bar_y = title_y + 26
        bar_half_w = 95
        self._drawGradientRect(center_x - bar_half_w, bar_y, center_x, bar_y + 1, 0x004ADE80, 0xCC4ADE80)
        self._drawGradientRect(center_x, bar_y, center_x + bar_half_w, bar_y + 1, 0xCC4ADE80, 0x004ADE80)

        # 4. Tagline: THE WORLD IS ALIVE
        tagline = "T H E   W O R L D   I S   A L I V E"
        tagline_y = bar_y + 6
        self.drawCenteredString(font, tagline, center_x, tagline_y, 0xA5D6B6)

        # 5. Footer metadata
        footer_y = self.height - 12
        left_info = "VERDANT  •  Alpha"
        right_info = "Living Ecosystem"

        font.drawStringWithShadow(left_info, 8, footer_y, 0x6A8F78)
        font.drawStringWithShadow(
            right_info,
            self.width - font.getStringWidth(right_info) - 8,
            footer_y,
            0x6A8F78
        )

        # 6. Render all menu buttons
        super().drawScreen(xm, ym, renderPartialTicks)
