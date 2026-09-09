from mc.net.minecraft.client.render.ThreadDownloadImage import ThreadDownloadImage

class ThreadDownloadImageData:

    def __init__(self, location, buffer):
        self.image = None
        self.referenceCount = 1
        self.textureName = -1
        self.textureSetupComplete = False
        ThreadDownloadImage(self, location, buffer).start()
