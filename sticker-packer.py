# WhatsApp Sticker Packer

import json
from pathlib import Path

from stickerlib.common import StickerPackLoader
from stickerlib.packer import WhatsAppStickerPacker

def main():
    print("WhatsApp Sticker Packer")

    workdir = Path(".") / "sticker_workdir"
    if (not workdir.exists()):
        workdir.mkdir()

    sticker_location = select_location(workdir)
    pack_data = StickerPackLoader(sticker_location)

    WhatsAppStickerPacker(workdir, pack_data)


def select_location(workdir):

    stickerlst = list(workdir.glob("**/info.json"))

    assert (len(stickerlst) > 0), "Sticker directory not found."

    for idx, sticker_info_file in enumerate(stickerlst, start=1):
        sticker_meta_file = open(sticker_info_file, 'r')
        sticker_meta = json.load(sticker_meta_file)
        print("{}. Title: '{}'".format(idx, sticker_meta['title']))

    pack_idx = int(input("Select a sticker pack: ")) - 1

    assert (pack_idx >= 0 and pack_idx < len(stickerlst)), "Please enter a number from the list."

    return stickerlst[pack_idx].parent

if __name__ == "__main__":
    main()
