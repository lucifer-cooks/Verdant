from mc.net.minecraft.client.sound.SoundPool import SoundPool
from pyglet import clock

import pyglet
import math
import os

class SoundManager:
    NORMAL_CHANNELS = 28
    listener = pyglet.media.get_audio_driver().get_listener()
    __channels = [pyglet.media.Player() for _ in range(NORMAL_CHANNELS)]
    __musicStream = None
    __soundPoolSounds = SoundPool()
    __soundPoolMusic = SoundPool()
    __latestSoundID = 0
    __nextChannel = 0
    __sourceNames = [''] * NORMAL_CHANNELS
    __soundSources = {}
    __loaded = False

    def loadSoundSettings(self, options):
        self.__options = options
        if not self.__loaded and (options.sound or options.music):
            self.__tryToSetLibraryAndCodecs()

    def __tryToSetLibraryAndCodecs(self):
        sound = self.__options.sound
        music = self.__options.music
        self.__options.sound = False
        self.__options.music = False
        self.__options.saveOptions()
        self.__loaded = True
        try:
            import pyogg
        except:
            print('PyOGG is not available. PyOGG is recommended for audio support.')
            gstreamer = False
            if pyglet.compat_platform.startswith('linux'):
                try:
                    from gi.repository import Gst, GLib
                except:
                    pass
                else:
                    gstreamer = True

            if pyglet.media.have_ffmpeg():
                print('Using FFMPEG codec instead.')
            else:
                if pyglet.compat_platform.startswith('linux'):
                    if gstreamer:
                        print('Using gst-python audio library.')
                    else:
                        print('Alternate codecs FFMPEG and gst-python are also missing. Audio is not supported.')
                        self.__loaded = False
                else:
                    print('FFMPEG is additionally missing. Audio is not supported.')
                    self.__loaded = False

        if not self.__loaded:
            return

        self.__options.sound = sound
        self.__options.music = music
        self.__options.saveOptions()

        for root, dirs, files in os.walk(os.path.join(pyglet.resource.get_script_home(), os.path.sep.join(pyglet.resource.path))):
            for fileName in files:
                if fileName[-4:] != '.ogg':
                    continue

                folder = os.path.basename(root)
                if folder == 'music':
                    self.addMusic(fileName, os.path.join(root, fileName))
                else:
                    self.addSound(os.path.join(folder, fileName).replace('\\', '/'),
                                  os.path.join(root, fileName))

        clock.schedule_once(self.removeTempSources, 10)

    def onSoundOptionsChanged(self):
        if not self.__loaded and (self.__options.sound or self.__options.music):
            self.__tryToSetLibraryAndCodecs()

        if not self.__options.music and self.__musicStream and self.__musicStream._source:
            self.__musicStream.pause()
            self.__musicStream = None

    def closeMinecraft(self):
        if not self.__loaded:
            return

        if self.__musicStream and self.__musicStream._source:
            self.__musicStream.pause()
            self.__musicStream = None
        for player in self.__channels:
            player.delete()

    def addSound(self, sound, file):
        self.__soundPoolSounds.addSound(sound, file)

    def addMusic(self, music, file):
        self.__soundPoolMusic.addSound(music, file)

    def playRandomMusicIfReady(self, x, y, z):
        if not self.__options.music or not self.__loaded:
            return

        if not self.__musicStream or not self.__musicStream._source:
            entry = self.__soundPoolMusic.getRandomSoundFromSoundPool('calm')
            self.__musicStream = pyglet.media.load(entry.soundUrl).play()

    def setListener(self, listener, partialTick):
        if not self.__loaded or not self.__options.sound or not listener:
            return

        pitch = listener.prevRotationPitch + (listener.rotationPitch - listener.prevRotationPitch) * partialTick
        yaw = listener.prevRotationYaw + (listener.rotationYaw - listener.prevRotationYaw) * partialTick
        x = listener.prevPosX + (listener.posX - listener.prevPosX) * partialTick
        y = listener.prevPosY + (listener.posY - listener.prevPosY) * partialTick
        z = listener.prevPosZ + (listener.posZ - listener.prevPosZ) * partialTick
        upX = math.sin(-yaw * (math.pi / 180.0) - math.pi)
        upY = math.cos(-pitch * (math.pi / 180.0))
        upZ = math.cos(-yaw * (math.pi / 180.0) - math.pi)
        lookX = -upX * upY
        lookY = math.sin(-pitch * (math.pi / 180.0))
        lookZ = -upZ * upY
        upX = -upX * lookY
        upZ = -upZ * lookY
        self.listener.position = (x, y, z)
        self.listener.forward_orientation = (lookX, lookY, lookZ)
        self.listener.up_orientation = (upX, upY, upZ)

    def playSound(self, sound, x, y, z, volume, pitch):
        entry = self.__soundPoolSounds.getRandomSoundFromSoundPool(sound)
        if not entry or not self.__loaded or not self.__options.sound or \
           volume <= 0.0:
            return

        self.__latestSoundID = (self.__latestSoundID + 1) % 256

        xd = x - self.listener.position[0]
        yd = y - self.listener.position[1]
        zd = z - self.listener.position[2]
        distanceFromListener = math.sqrt(xd * xd + yd * yd + zd * zd)
        distOrRoll = 16.0 * volume if volume > 1.0 else 16.0
        if distanceFromListener <= 0:
            gain = 1.0
        elif distanceFromListener >= distOrRoll:
            gain = 0.0
        else:
            gain = 1.0 - (distanceFromListener / distOrRoll)

        if gain > 1.0:
            gain = 1.0
        if gain < 0.0:
            gain = 0.0

        priority = True if volume > 1.0 else False
        volume = min(gain * volume, 1.0)

        player = self.__getNextChannel(f'sound_{self.__latestSoundID}')
        if not player:
            return

        player.max_distance = distOrRoll
        player.position = (x, y, z)
        player.pitch = pitch
        player.volume = volume
        player.priority = priority
        self.__playSound(player, entry)

    def playSoundFX(self, sound, volume, pitch):
        entry = self.__soundPoolSounds.getRandomSoundFromSoundPool(sound)
        if not entry or not self.__loaded or not self.__options.sound:
            return

        self.__latestSoundID = (self.__latestSoundID + 1) % 256

        player = self.__getNextChannel(f'sound_{self.__latestSoundID}')
        if not player:
            return

        player.min_distance = 0.0
        player.max_distance = 100000000.
        player.position = (0.0, 0.0, 0.0)
        player.pitch = 1.0
        player.volume = 0.25
        player.priority = False
        self.__playSound(player, entry)

    def __playSound(self, player, entry):
        player.min_distance = 0.0
        player.cone_orientation = (0, 0, 0)
        player.cone_outer_gain = 0.0
        player.seek(0.0)
        player.queue(entry.stream)
        if player.playing:
            player.next_source()
        else:
            player.play()
            try: player._audio_player.alsource.rolloff_factor = 0.0
            except: pass

        self.__soundSources[f'sound_{self.__latestSoundID}'] = player

    def __getNextChannel(self, sound):
        if not sound:
            return

        channels = len(self.__channels)
        for i in range(channels):
            if sound == self.__sourceNames[i]:
                return self.__channels[i]

        n = self.__nextChannel
        for i in range(channels * 2):
            name = self.__sourceNames[n]
            src = self.__soundSources.get(name) if name else None
            if not src or not src.playing or (i >= channels and not src.priority):
                self.__nextChannel = (n + 1) % channels
                self.__sourceNames[n] = sound
                return self.__channels[n]

            n = self.__nextChannel if i == channels // 2 else (n + 1) % channels

        return None

    def removeTempSources(self, dt):
        for name, src in dict(self.__soundSources).items():
            if not src.playing:
                del self.__soundSources[name]

        clock.schedule_once(self.removeTempSources, 10)
