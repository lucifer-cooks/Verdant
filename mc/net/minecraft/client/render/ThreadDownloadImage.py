from threading import Thread
from base64 import b64decode
from io import BytesIO
from PIL import Image

import urllib.request
import traceback
import json

def getTextureInfo(properties):
    for prop in properties:
        if prop['name'] == 'textures':
            return json.loads(b64decode(prop['value'], validate=True).decode('utf-8'))

class ThreadDownloadImage(Thread):

    def __init__(self, imageData, location, buffer):
        super().__init__()
        self.__imageData = imageData
        self.__location = location
        self.__buffer = buffer

    def run(self):
        if not self.__location:
            return

        try:
            with urllib.request.urlopen(self.__location) as r:
                if r.code != 200:
                    return

                userId = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))['id']

            with urllib.request.urlopen(f'https://sessionserver.mojang.com/session/minecraft/profile/{userId}') as r:
                if r.code != 200:
                    return

                userInfo = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))

            textureInfo = getTextureInfo(userInfo['properties'])
            if not textureInfo:
                return

            try:
                skinUrl = textureInfo['textures']['SKIN']['url']
            except:
                return

            with urllib.request.urlopen(skinUrl) as r:
                if r.code != 200:
                    return

                if self.__buffer:
                    self.__imageData.image = self.__buffer.parseUserSkin(
                        Image.open(BytesIO(r.read())).convert('RGBA')
                    )
                else:
                    self.__imageData.image = Image.open(BytesIO(r.read())).convert('RGBA')
        except:
            print(traceback.format_exc())
