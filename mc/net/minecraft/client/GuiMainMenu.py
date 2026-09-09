from mc.net.minecraft.client.gui.GuiScreen import GuiScreen
from mc.net.minecraft.client.gui.GuiOptions import GuiOptions
from mc.net.minecraft.client.gui.GuiNewLevel import GuiNewLevel
from mc.net.minecraft.client.gui.GuiLoadLevel import GuiLoadLevel
from mc.net.minecraft.client.gui.GuiButton import GuiButton
from mc.net.minecraft.client.render.Tessellator import tessellator
from mc.JavaUtils import getMillis, random
from pyglet import gl

import math

class GuiMainMenu(GuiScreen):

    def __init__(self):
        self.__updateCounter = 0.0
        self.__splashes = (
            'Pre-beta!', 'As seen on TV!', 'Awesome!', '100% pure!', 'May contain nuts!',
            'Better than Prey!', 'More polygons!', 'Sexy!', 'Limited edition!',
            'Flashing letters!', 'Made by Notch!', 'Coming soon!', 'Best in class!',
            'When it\'s finished!', 'Absolutely dragon free!', 'Excitement!',
            'More than 5000 sold!', 'One of a kind!', '700+ hits on YouTube!', 'Indev!',
            'Spiders everywhere!', 'Check it out!', 'Holy cow, man!', 'It\'s a game!',
            'Made in Sweden!', 'Uses Pyglet!', 'Written in Python!', 'Reticulating splines!',
            'Minecraft!', 'Yaaay!', 'Alpha version!', 'Singleplayer!', 'Keyboard compatible!',
            'Undocumented!', 'Ingots!', 'Exploding creepers!', 'That\'s not a moon!',
            'l33t!', 'Create!', 'Survive!', 'Dungeon!', 'Exclusive!', 'The bee\'s knees!',
            'Down with O.P.P.!', 'Closed source!', 'Classy!', 'Wow!', 'Not on steam!',
            '9.95 euro!', 'Half price!', 'Oh man!', 'Check it out!', 'Awesome community!',
            'Pixels!', 'Teetsuuuuoooo!', 'Kaaneeeedaaaa!', 'Now with difficulty!',
            'Enhanced!', '90% bug free!', 'Pretty!', '12 herbs and spices!', 'Fat free!',
            'Absolutely no memes!', 'Free dental!', 'Ask your doctor!', 'Minors welcome!',
            'Cloud computing!', 'Legal in Finland!', 'Hard to label!', 'Technically good!',
            'Bringing home the bacon!', 'Indie!', 'GOTY!', 'Ceci n\'est pas une title screen!',
            'Euclidian!', 'Now in 3D!', 'Inspirational!', 'Herregud!',
            'Complex cellular automata!', 'Yes, sir!', 'Played by cowboys!', 'OpenGL 1.1!',
            'Thousands of colors!', 'Try it!', 'Age of Wonders is better!',
            'Try the mushroom stew!', 'Sensational!', 'Hot tamale, hot hot tamale!',
            'Play him off, keyboard cat!', 'Guaranteed!', 'Macroscopic!', 'Bring it on!',
            'Random splash!', 'Call your mother!', 'Monster infighting!', 'Loved by millions!',
            'Ultimate edition!', 'Freaky!', 'You\'ve got a brand new key!', 'Water proof!',
            'Uninflammable!', 'Whoa, dude!', 'All inclusive!', 'Tell your friends!',
            'NP is not in P!', 'Notch <3 Ez!', 'Music by C418!'
        )
        self.__currentSplash = self.__splashes[int(random() * len(self.__splashes))]

    def updateScreen(self):
        self.__updateCounter += 0.01

    def _keyTyped(self, key, char, motion):
        pass

    def initGui(self):
        self._controlList.clear()
        self._controlList.append(GuiButton(1, self.width // 2 - 100,
                                           self.height // 4 + 48, 'Generate new level...'))
        self._controlList.append(GuiButton(2, self.width // 2 - 100,
                                           self.height // 4 + 72, 'Load level..'))
        self._controlList.append(GuiButton(3, self.width // 2 - 100,
                                           self.height // 4 + 96, 'Play tutorial level'))
        self._controlList.append(GuiButton(0, self.width // 2 - 100,
                                           self.height // 4 + 120 + 12, 'Options...'))
        self._controlList[2].enabled = False
        if not self.mc.session:
            self._controlList[1].enabled = False

    def _actionPerformed(self, button):
        if button.id == 0:
            self.mc.displayGuiScreen(GuiOptions(self, self.mc.options))
        elif button.id == 1:
            self.mc.displayGuiScreen(GuiNewLevel(self))
        elif self.mc.session and button.id == 2:
            self.mc.displayGuiScreen(GuiLoadLevel(self))

    def drawScreen(self, xm, ym, renderPartialTicks):
        self.drawDefaultBackground()
        t = tessellator
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.mc.renderEngine.getTexture('gui/logo.png'))
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)
        t.setColorOpaque_I(16777215)
        self.drawTexturedModalRect((self.width - 256) // 2, 30, 0, 0, 256, 49)
        gl.glPushMatrix()
        gl.glTranslatef(self.width / 2 + 90, 70.0, 0.0)
        gl.glRotatef(-20.0, 0.0, 0.0, 1.0)
        size = 1.8 - abs(math.sin((getMillis() % 1000) / 1000.0 * math.pi * 2.0) * 0.1)
        gl.glScalef(size, size, size)
        self.drawCenteredString(self._fontRenderer, self.__currentSplash, 0, -8, 16776960)
        gl.glPopMatrix()
        copyright = 'Copyright Mojang Specifications. Do not distribute.'
        self.drawString(
            self._fontRenderer, copyright,
            self.width - self._fontRenderer.getStringWidth(copyright) - 2,
            self.height - 10, 16777215
        )
        super().drawScreen(xm, ym, renderPartialTicks)
