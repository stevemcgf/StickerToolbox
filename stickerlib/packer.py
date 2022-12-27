from PIL import Image
from pathlib import Path
import random, string
import io
import zipfile

from stickerlib.common import StickerPack
from stickerlib.common import Sticker
from stickerlib.common import StickerUtils

MAGIC_DATA = b'nu\x0e\x00{u\xa1t\x80\x81\x00\x00\x00\x00\x00\x00\x00\x00'

def cleanup_file_name(str):
    str = str.replace(":", " ")
    str = str.replace("\\", " ")
    tokens = str.split()
    out = " ".join(tokens)
    return out

# WhatsApp Sticker Packer
class WhatsAppStickerPacker:
    def __init__(self, workdir, pack_data = StickerPack()):

        assert (isinstance(pack_data, StickerPack)), "Must be a valid Sticker Pack."

        print("Title: {}".format(pack_data.title))
        print("Author: {}".format(pack_data.author))
        print("Sticker count: {}".format(len(pack_data.stickers)))

        if (len(pack_data.title) > 64):
            print("Title will be reduced to 64 characters.")
            pack_data.title = pack_data.title[0:64]

        if (len(pack_data.author) > 64):
            print("Author will be reduced to 30 characters.")
            pack_data.author = pack_data.author[0:64]

        if (len(pack_data.stickers) > 30):
            print("More than 30 Stickers. Only 30 stickers will be used.")
            pack_data.stickers = pack_data.stickers[0:30]

        self.workdir = workdir
        self.pack_data = pack_data
        self.create_zip_file()
        self.save_stickers()
        self.save_meta()
        self.save_icon()
    
    def create_zip_file(self):
        wasticker_name = self.workdir / "{}.wastickers".format(StickerUtils.cleanup_path_name(self.pack_data.title))
        wastickers_file = open(wasticker_name, "wb")
        self.wastickers_zip = zipfile.ZipFile(wastickers_file, mode="x", compression=zipfile.ZIP_DEFLATED)

    def save_meta(self):
        self.wastickers_zip.writestr("/author.txt", self.pack_data.author)
        self.wastickers_zip.writestr("/title.txt", self.pack_data.title)

    def save_icon(self):
        # 96 x 96
        icon_stream = io.BytesIO()
        icon_stream.write(self.pack_data.icon)
        icon_stream.seek(0)
        icon_image_original = Image.open(icon_stream)
        icon_image_original = icon_image_original.convert("RGBA")

        width, height = icon_image_original.size

        if (width == height):
            icon_image_square = icon_image_original
        elif (width > height):
            icon_image_square = Image.new("RGBA", (width, width), (0, 0, 0, 0))
            icon_image_square.paste(icon_image_original, (0, (width - height) // 2))
        else:
            icon_image_square = Image.new("RGBA", (height, height), (0, 0, 0, 0))
            icon_image_square.paste(icon_image_original, ((height - width) // 2, 0))

        icon_image = icon_image_square.resize((96,96))

        icon_image_stream = io.BytesIO()
        icon_image.save(icon_image_stream, "PNG")
        icon_image_stream.seek(0)

        self.wastickers_zip.writestr("/{0}.png".format(self.pack_data.id), icon_image_stream.read())

    def save_stickers(self):
        for sticker in self.pack_data.stickers:
            self.save_sticker(sticker)

    def save_sticker(self, sticker = Sticker()):
        # 512 x 512
        sticker_stream = io.BytesIO()
        sticker_stream.write(sticker.static)
        sticker_stream.seek(0)
        sticker_image_original = Image.open(sticker_stream)
        sticker_image_original = sticker_image_original.convert("RGBA")

        width, height = sticker_image_original.size

        if (width == height):
            sticker_image_square = sticker_image_original
        elif (width > height):
            sticker_image_square = Image.new("RGBA", (width, width), (0, 0, 0, 0))
            sticker_image_square.paste(sticker_image_original, (0, (width - height) // 2))
        else:
            sticker_image_square = Image.new("RGBA", (height, height), (0, 0, 0, 0))
            sticker_image_square.paste(sticker_image_original, ((height - width) // 2, 0))

        sticker_image = sticker_image_square.resize((512,512))

        sticker_image_stream = io.BytesIO()
        sticker_image.save(sticker_image_stream, "WEBP")
        sticker_image_stream.seek(0)

        self.wastickers_zip.writestr("/{0}.webp".format(sticker.id), sticker_image_stream.read())
