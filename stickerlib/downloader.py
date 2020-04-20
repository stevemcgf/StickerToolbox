import requests
import json
import distutils.util
from PIL import Image
import io

from stickerlib.common import StickerPack
from stickerlib.common import Sticker

def load_binary_url(url):
    binary_stream = io.BytesIO()

    response = requests.get(url, stream=True)
    assert (response.status_code == 200), "Failed to download binary file."

    for chunk in response.iter_content(chunk_size = 10240):
        binary_stream.write(chunk)

    binary_stream.seek(0)

    return binary_stream

# Line Sticker Downloader
class LineStickerDownloader:
    def __init__(self, pack_id):
        print("Pack Id: {}".format(pack_id))

        assert (isinstance(pack_id, int)), "Pack Id must be a number."
        
        self.pack_data = StickerPack(pack_id)
        self.load_pack_meta()
        self.load_icon()
        self.load_stickers()

    def load_pack_meta(self):
        print("Loading Metadata.")

        pack_meta_url = "http://dl.stickershop.line.naver.jp/products/0/0/1/{pack_id}/android/productInfo.meta".format(pack_id=self.pack_data.id)

        response = requests.get(pack_meta_url)
        assert (response.status_code == 200), "Sticker pack not found."

        pack_meta = json.loads(response.text)

        self.pack_data.title = pack_meta['title']['en'].strip()
        self.pack_data.author = pack_meta['author']['en'].strip()

        if ('stickerResourceType' in pack_meta):
            self.pack_resource_type = pack_meta['stickerResourceType']
        else:
            self.pack_resource_type = 'UNDEFINED'

        if (self.pack_resource_type == "POPUP"):
            self.pack_data.has_animation = True
        elif ('hasAnimation' in pack_meta):
            self.pack_data.has_animation = pack_meta['hasAnimation']
        else:
            self.pack_data.has_animation = False

        if ('hasSound' in pack_meta):
            self.pack_data.has_sound = pack_meta['hasSound']
        else:
            self.pack_data.has_sound = False
        
        self.pack_stickers_meta = pack_meta['stickers']
        
        print("Pack Title: '{}'".format(self.pack_data.title))
        print("Pack Author: '{}'".format(self.pack_data.author))
        print("Has Animation: {}".format(self.pack_data.has_animation))
        print("Has Sound: {}".format(self.pack_data.has_sound))
        print("Resource Type: '{}'".format(self.pack_resource_type))
        print("Sticker Count: {}".format(len(self.pack_stickers_meta)))

    def load_icon(self):
        print("Loading Icon.")
        
        icon_url = "http://dl.stickershop.line.naver.jp/products/0/0/1/{pack_id}/android/main.png".format(pack_id=self.pack_data.id)
        sticker_stream = load_binary_url(icon_url)
        sticker_stream.seek(0)

        self.pack_data.icon = sticker_stream.read()

    def load_stickers(self):
        print("Loading Stickers.")

        for sticker_meta in self.pack_stickers_meta:
            sticker_id = sticker_meta['id']
            sticker_data = Sticker(sticker_id)

            sticker_width = sticker_meta['width']
            sticker_height = sticker_meta['height']
        
            print("Retreving Sticker Id: {}, Width: {}, Height: {}".format(sticker_id, sticker_width, sticker_height))
            if (self.pack_resource_type == "PER_STICKER_TEXT"):
                sticker_data.static = self.load_static_sticker_with_text(sticker_id)
            else:
                sticker_data.static = self.load_static_sticker(sticker_id)

            if (self.pack_resource_type == "POPUP"):
                sticker_data.animation = self.load_animation_popup_sticker(sticker_id)
            elif (self.pack_data.has_animation):
                sticker_data.animation = self.load_animation_sticker(sticker_id)

            if (self.pack_data.has_sound):
                sticker_data.sound = self.load_sound_sticker(sticker_id)

            self.pack_data.add_sticker(sticker_data)

    def load_static_sticker(self, sticker_id):
        sticker_url = "http://dl.stickershop.line.naver.jp/stickershop/v1/sticker/{sticker_id}/android/sticker.png".format(sticker_id=sticker_id)
        sticker_stream = load_binary_url(sticker_url)
        sticker_stream.seek(0)

        return sticker_stream.read()

    def load_static_sticker_with_text(self, sticker_id):
        sticker_base_url = "https://stickershop.line-scdn.net/stickershop/v1/sticker/{sticker_id}/android/base/plus/sticker.png".format(sticker_id=sticker_id)
        sticker_overlay_url = "https://stickershop.line-scdn.net/stickershop/v1/product/{pack_id}/sticker/{sticker_id}/android/overlay/plus/default/sticker.png".format(pack_id=self.pack_data.id, sticker_id=sticker_id)

        sticker_base_stream = load_binary_url(sticker_base_url)
        sticker_base_img = Image.open(sticker_base_stream)
        sticker_base_img = sticker_base_img.convert("RGBA")

        sticker_overlay_stream = load_binary_url(sticker_overlay_url)
        sticker_overlay_img = Image.open(sticker_overlay_stream)

        sticker_base_img.paste(sticker_overlay_img, (0, 0), sticker_overlay_img)
        
        sticker_stream = io.BytesIO()
        sticker_base_img.save(sticker_stream, format="PNG")
        sticker_stream.seek(0)

        return sticker_stream.read()

    def load_animation_popup_sticker(self, sticker_id):
        sticker_url = "https://stickershop.line-scdn.net/stickershop/v1/sticker/{sticker_id}/android/sticker_popup.png".format(sticker_id=sticker_id)
        sticker_stream = load_binary_url(sticker_url)
        sticker_stream.seek(0)

        return sticker_stream.read()

    def load_animation_sticker(self, sticker_id):
        sticker_url = "https://sdl-stickershop.line.naver.jp/products/0/0/1/{pack_id}/android/animation/{sticker_id}.png".format(pack_id=self.pack_data.id, sticker_id=sticker_id)
        sticker_stream = load_binary_url(sticker_url)
        sticker_stream.seek(0)

        return sticker_stream.read()

    def load_sound_sticker(self, sticker_id):
        sticker_url = "https://stickershop.line-scdn.net/stickershop/v1/sticker/{sticker_id}/android/sticker_sound.m4a".format(sticker_id=sticker_id)
        sticker_stream = load_binary_url(sticker_url)
        sticker_stream.seek(0)

        return sticker_stream.read()

    def get_sticker_pack(self):
        return self.pack_data

if __name__ == "__main__":
    pass
