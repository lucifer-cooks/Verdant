from pyglet import media

class SoundPoolEntry:

    def __init__(self, name, url):
        self.soundName = name
        self.soundUrl = url
        try:
            self.stream = media.load(url, streaming=False)
        except Exception:
            self.stream = None
