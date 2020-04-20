# Line Sticker Downloader

import requests
import json
import distutils.util
from PIL import Image
import io
from pathlib import Path

from stickerlib.common import StickerPackSaver
from stickerlib.downloader import LineStickerDownloader

def main():
    print("Line Sticker Downloader")

    workdir = Path(".") / "sticker_workdir"
    if (not workdir.exists()):
        workdir.mkdir()

    pack_id = int(input("Enter the sticker pack Id: "))
    dl = LineStickerDownloader(pack_id)

    StickerPackSaver(workdir, dl.get_sticker_pack())

if __name__ == "__main__":
    main()
