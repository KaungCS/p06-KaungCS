# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO

from PIL import Image
from tornado.testing import gen_test

from tests.base import FilterTestCase


class RoundCornerFringeTestCase(FilterTestCase):
    @gen_test
    async def test_transparent_round_corner_edge_has_no_dark_fringe(self):
        # A solid white picture with a white fill: every pixel of the
        # picture and of the fill is white. With transparent=1 the curved
        # edge should only fade in alpha, so no visible corner pixel may
        # be darker than white.
        source = Image.new("RGB", (200, 200), (255, 255, 255))
        buffer = BytesIO()
        source.save(buffer, "PNG")

        fltr = self.get_filter(
            "thumbor.filters.round_corner",
            "round_corner(60,255,255,255,1)",
        )
        fltr.engine.load(buffer.getvalue(), ".png")
        fltr.context.transformer.img_operation_worker()
        await fltr.run()

        image = fltr.engine.image.convert("RGBA")
        assert image.size == (200, 200)

        # Step 1: no visible corner pixel may be a dark color.
        dark_visible_pixels = []
        for y in range(60):
            for x in range(60):
                r, g, b, a = image.getpixel((x, y))
                if a > 0 and (r, g, b) != (255, 255, 255):
                    dark_visible_pixels.append((x, y, (r, g, b, a)))
        assert len(dark_visible_pixels) == 0, (
            f"{len(dark_visible_pixels)} visible corner pixels are not "
            f"white, for example {dark_visible_pixels[:3]}"
        )

        # Step 2: the curved edge must fade through alpha.
        partial_alpha_pixels = 0
        for y in range(60):
            for x in range(60):
                _, _, _, a = image.getpixel((x, y))
                if 0 < a < 255:
                    partial_alpha_pixels += 1
        assert partial_alpha_pixels > 0
