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
from thumbor.transformer import Transformer


class _Request:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.fit_in = False
        self.stretch = False
        self.full = False
        self.debug = False
        self.filters = []
        self.adaptive = False
        self.trim = None
        self.should_crop = False
        self.crop = {}
        self.focal_points = []
        self.halign = "center"
        self.valign = "middle"
        self.engine = None


def build_transparent_rainbow_png():
    # 16x16 RGBA PNG: opaque vertical colour bars with transparent gaps,
    # the same kind of source as course/images/rainbow.png.
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    colours = [
        (255, 0, 0, 255),
        (0, 255, 0, 255),
        (0, 0, 255, 255),
        (255, 255, 0, 255),
    ]
    for x in range(0, 16, 2):
        for y in range(16):
            img.putpixel((x, y), colours[(x // 4) % 4])
    buffer = BytesIO()
    img.save(buffer, "PNG")
    return buffer.getvalue()


def test_wide_request_for_transparent_png_is_not_empty():
    # Request 800x20 for a 16x16 transparent PNG. The output must be an
    # 800x20 picture that still has opaque pixels, not one where every
    # pixel is fully transparent.
    cfg = Config(SECURITY_KEY="ACME-SEC", ENGINE="thumbor.engines.pil")
    context = Context(config=cfg)
    context.request = _Request(800, 20)
    engine = Engine(context)
    engine.load(build_transparent_rainbow_png(), ".png")
    context.request.engine = engine

    transformer = Transformer(context)
    transformer._calculate_target_dimensions()
    transformer.adjust_focal_points()
    transformer.auto_crop()
    transformer.resize()

    out = Image.open(BytesIO(engine.read(".png"))).convert("RGBA")
    assert out.size == (800, 20)
    assert out.getchannel("A").getextrema()[1] == 255
