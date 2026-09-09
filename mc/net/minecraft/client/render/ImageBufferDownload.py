from PIL import Image

class ImageBufferDownload:

    def parseUserSkin(self, image):
        self.__imageWidth = 64
        self.__imageHeight = 32
        img = Image.new('RGBA', (self.__imageWidth, self.__imageHeight))
        img.paste(image)
        self.__imageData = list(img.getdata())

        def tupleToPixel(c):
            x = c[0] << 16 | c[1] << 8 | c[2] | c[3] << 24
            if x >= 1 << 31:
                x -= 1 << 32

            return x

        def pixelToTuple(x):
            r = (x >> 24) & 0xFF
            g = x & 0xFF
            b = (x >> 8) & 0xFF
            a = (x >> 16) & 0xFF

            return (a, b, g, r)

        self.__imageData = [tupleToPixel(pixel) for pixel in self.__imageData]

        self.__setAreaOpaque(0, 0, 32, 16)
        self.__setAreaTransparent(32, 0, 64, 32)
        self.__setAreaOpaque(0, 16, 64, 32)

        img.putdata([pixelToTuple(pixel) for pixel in self.__imageData])
        return img

    def __setAreaTransparent(self, x0, z0, x1, z1):
        x = x0
        while True:
            if x >= x1:
                break

            for z in range(z0, z1):
                if ((self.__imageData[x + z * self.__imageWidth] % 0x100000000) >> 24) < 128:
                    break
            else:
                x += 1
                continue

            break

        if x >= x1:
            for x in range(32, 64):
                for z in range(0, 32):
                    self.__imageData[x + z * self.__imageWidth] &= 16777215

    def __setAreaOpaque(self, x0, z0, x1, z1):
        for x in range(0, x1):
            for z in range(z0, z1):
                self.__imageData[x + z * self.__imageWidth] |= -16777216
