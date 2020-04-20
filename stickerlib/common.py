# Sticker Common Utils
from pathlib import Path
import json

class Sticker:
    def __init__(self, id=int(), static=None, animation=None, sound=None):
        self._id = id
        self._static = static
        self._animation = animation
        self._sound = sound

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        assert (isinstance(value, int)), "Value must be a number."
        self._id = value
    
    @property
    def static(self):
        return self._static

    @static.setter
    def static(self, value):
        assert (isinstance(value, bytes)), "Value must be a bytes sequence."
        self._static = value

    @property
    def animation(self):
        return self._animation

    @animation.setter
    def animation(self, value):
        assert (isinstance(value, bytes)), "Value must be a bytes sequence."
        self._animation = value
    
    @property
    def has_animation(self):
        return isinstance(self._animation, bytes)

    @property
    def sound(self):
        return self._sound

    @sound.setter
    def sound(self, value):
        assert (isinstance(value, bytes)), "Value must be a bytes sequence."
        self._sound = value

    @property
    def has_sound(self):
        return isinstance(self._sound, bytes)

class StickerPack:
    def __init__(self, id = int(), title = str(), author = str(), has_animation = bool(), has_sound = bool(), icon = bytes()):
        self._id = id
        self._title = title
        self._author = author
        self._has_animation = has_animation
        self._has_sound = has_sound
        self._icon = icon
        self._stickers = list()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        assert (isinstance(value, int)), "Value must be a number."
        self._id = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        assert (isinstance(value, str)), "Value must be a string."
        self._title = value

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        assert (isinstance(value, str)), "Value must be a string."
        self._author = value
    
    @property
    def has_animation(self):
        return self._has_animation

    @has_animation.setter
    def has_animation(self, value):
        assert (isinstance(value, bool)), "Value must be a bool."
        self._has_animation = value

    @property
    def has_sound(self):
        return self._has_sound

    @has_sound.setter
    def has_sound(self, value):
        assert (isinstance(value, bool)), "Value must be a bool."
        self._has_sound = value

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        assert (isinstance(value, bytes)), "Value must be a bytes sequence."
        self._icon = value

    @property
    def stickers(self):
        return self._stickers
    
    @stickers.setter
    def stickers(self, value):
        assert(isinstance(value, list)), "Value must be a list."
        self._stickers = value

    def add_sticker(self, sticker = Sticker()):
        assert (self.has_animation == sticker.has_animation), "Sticker should have animation as Sticker Pack"
        assert (self.has_sound == sticker.has_sound), "Sticker should have sound as Sticker Pack"
        self._stickers.append(sticker)

def StickerPackSaver(workdir = Path(), pack_data = StickerPack()):
    def cleanup_path_name(str):
        str = str.replace(":", " ")
        tokens = str.split()
        out = " ".join(tokens)
        return out

    save_path = workdir
    save_path /= cleanup_path_name(pack_data.title)
    
    assert (save_path.exists() == False), "Sticker Pack directory already exists."

    save_path.mkdir()

    # Save Meta data
    meta = dict()
    meta['pack_id'] = pack_data.id
    meta['title'] = pack_data.title
    meta['author'] = pack_data.author
    meta['has_animation'] = pack_data.has_animation
    meta['has_sound'] = pack_data.has_sound
    meta['stickers'] = list()
    for idx, sticker_data in enumerate(pack_data.stickers, start=1):
        meta['stickers'].append({'id': sticker_data.id, 'file_base' : "sticker{:02d}".format(idx)})

    meta_file = open(save_path / "info.json", "w")
    json.dump(meta, meta_file, indent = 4)
    meta_file.close()

    # Create directories
    save_path_static = save_path / "static"
    save_path_static.mkdir()

    if (pack_data.has_animation):
        save_path_animation = save_path / "animation"
        save_path_animation.mkdir() 

    if (pack_data.has_sound):
        save_path_sound = save_path / "sound"
        save_path_sound.mkdir()

    # Write icon
    icon_file = open(save_path / "icon.png", "wb")
    icon_file.write(pack_data.icon)
    icon_file.close()

    # Write Stickers
    for idx, sticker_data in enumerate(pack_data.stickers, start=1):
        # Write Sticker Static
        sticker_file = open(save_path_static / "sticker{:02d}.png".format(idx), 'wb')
        sticker_file.write(sticker_data.static)
        sticker_file.close()

        # Write Sticker Animation
        if (pack_data.has_animation):
            sticker_file = open(save_path_animation / "sticker{:02d}.png".format(idx), 'wb')
            sticker_file.write(sticker_data.animation)
            sticker_file.close()

        # Write Sticker Sound
        if (pack_data.has_sound):
            sticker_file = open(save_path_sound / "sticker{:02d}.m4a".format(idx), 'wb')
            sticker_file.write(sticker_data.sound)
            sticker_file.close()

def StickerPackLoader(pack_location = Path()):
    meta_file = open(pack_location / "info.json", "r")
    meta_data = json.load(meta_file)

    # Read Meta data
    pack_data = StickerPack(meta_data['pack_id'], meta_data['title'],
                            meta_data['author'], meta_data['has_animation'],
                            meta_data['has_sound'])
    
    # Read icon
    icon_file = open(pack_location / "icon.png", 'rb')
    pack_data.icon = icon_file.read()
    icon_file.close()

    # Sticker directories
    sticker_path_static = pack_location / "static"
    assert (sticker_path_static.is_dir()), "Missing static directory."

    if (pack_data.has_animation):
        sticker_path_animation = pack_location / "animation"
        assert (sticker_path_animation.is_dir()), "Missing animation directory."

    if (pack_data.has_sound):
        sticker_path_sound = pack_location / "sound"
        assert (sticker_path_sound.is_dir()), "Missing sound directory."

    for sticker_meta_data in meta_data['stickers']:
        sticker_data = Sticker(sticker_meta_data['id'])

        # Read Sticker Static
        sticker_file = open(sticker_path_static / "{}.png".format(sticker_meta_data['file_base']), 'rb')
        sticker_data.static = sticker_file.read()
        sticker_file.close()

        # Read Sticker Animation
        if (pack_data.has_animation):
            sticker_file = open(sticker_path_animation / "{}.png".format(sticker_meta_data['file_base']), 'rb')
            sticker_data.animation = sticker_file.read()
            sticker_file.close()

        # Read Sticker Sound
        if (pack_data.has_sound):
            sticker_file = open(sticker_path_sound / "{}.m4a".format(sticker_meta_data['file_base']), 'rb')
            sticker_data.sound = sticker_file.read()
            sticker_file.close()

        pack_data.add_sticker(sticker_data)

    return pack_data

if __name__ == "__main__":
    pass
