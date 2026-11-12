# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine


def build_transparent_palette_gif():
    # 40x40 palette GIF. Palette index 0 is the background and is marked
    # transparent. Index 1 is a solid blue disc in the middle.
    img = Image.new("P", (40, 40), 0)
    palette = [0, 0, 0, 0, 0, 255] + [0, 0, 0] * 254
    img.putpalette(palette)
    for x in range(10, 30):
        for y in range(10, 30):
            img.putpixel((x, y), 1)
    buffer = BytesIO()
    img.save(buffer, "GIF", transparency=0)
    return buffer.getvalue()


def get_engine():
    cfg = Config(SECURITY_KEY="ACME-SEC", ENGINE="thumbor.engines.pil")
    cfg.PILLOW_PRESERVE_INDEXED_MODE = True
    return Engine(Context(config=cfg))


def test_resized_palette_gif_keeps_transparent_background():
    engine = get_engine()
    engine.load(build_transparent_palette_gif(), ".gif")
    assert engine.original_mode == "P"

    engine.resize(20, 20)
    result = engine.read(".gif")

    img = Image.open(BytesIO(result))
    assert img.format == "GIF"
    assert "transparency" in img.info
    # The corner was transparent in the source and must stay transparent
    assert img.convert("RGBA").getpixel((0, 0))[3] == 0
    # The blue disc in the middle must stay opaque
    assert img.convert("RGBA").getpixel((10, 10))[3] == 255
