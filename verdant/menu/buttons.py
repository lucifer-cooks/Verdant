"""Custom stylized button component for the VERDANT user interface."""

from __future__ import annotations

from typing import Optional
from pyglet import gl

from mc.net.minecraft.client.gui.GuiButton import GuiButton
from mc.net.minecraft.client.gui.Gui import Gui


class VerdantMenuButton(GuiButton):
    """Clean, atmospheric survival-adventure button for the VERDANT interface."""

    def __init__(
        self,
        id_: int,
        x: int,
        y: int,
        width: int = 200,
        height: int = 24,
        string: str = "",
    ) -> None:
        super().__init__(id_, x, y, width, height, string)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_hovered = False

    def drawButton(self, mc, xMouse: int, yMouse: int) -> None:
        if not self.visible:
            return

        self.is_hovered = (
            self.x <= xMouse < self.x + self.width and
            self.y <= yMouse < self.y + self.height
        )

        font = mc.fontRenderer

        if not self.enabled:
            # Disabled state
            # Outer border
            Gui._drawRect(self.x, self.y, self.x + self.width, self.y + self.height, 0xFF1B241E)
            # Inner fill
            Gui._drawRect(self.x + 1, self.y + 1, self.x + self.width - 1, self.y + self.height - 1, 0xDD0D1510)
            text_color = 0x4A5C50
            display_text = self.displayString
        elif self.is_hovered:
            # Hovered state: glowing emerald border and rich moss gradient
            # Outer glow border
            Gui._drawRect(self.x, self.y, self.x + self.width, self.y + self.height, 0xFF4ADE80)
            # Inner gradient fill
            Gui._drawGradientRect(
                self.x + 1, self.y + 1, self.x + self.width - 1, self.y + self.height - 1,
                0xF0183322, 0xF01E422C
            )
            # Left accent highlight bar
            Gui._drawRect(self.x + 1, self.y + 1, self.x + 4, self.y + self.height - 1, 0xFF6EE7A0)
            text_color = 0xF0FFF4
            display_text = f"›  {self.displayString}  ‹"
        else:
            # Normal resting state: sleek dark slate/forest
            # Outer border
            Gui._drawRect(self.x, self.y, self.x + self.width, self.y + self.height, 0xFF2A4232)
            # Inner gradient fill
            Gui._drawGradientRect(
                self.x + 1, self.y + 1, self.x + self.width - 1, self.y + self.height - 1,
                0xEE0F1E16, 0xEE14281D
            )
            text_color = 0xC5DACB
            display_text = self.displayString

        # Render centered text with drop shadow
        text_y = self.y + (self.height - 8) // 2
        text_x = self.x + self.width // 2
        self.drawCenteredString(font, display_text, text_x, text_y, text_color)

    def mousePressed(self, xm: int, ym: int) -> bool:
        return (
            self.enabled and
            self.visible and
            self.x <= xm < self.x + self.width and
            self.y <= ym < self.y + self.height
        )
