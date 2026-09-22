#!/usr/bin/env python3
"""
Round 12: raw -> assets/media for feedback 7.0.

New file names rather than overwrites. Media is not content hashed, so a
replaced picture under an old name keeps being served from the Pages cache
to anybody who has seen it (the same reason hero-spotlight.* was retired).

    python _art/round12_finish.py
"""
import pathlib
from PIL import Image, ImageChops, ImageEnhance, ImageOps

HERE = pathlib.Path(__file__).parent
RAW = HERE / "raw"
MEDIA = HERE.parent / "assets" / "media"

# name, output size (w, h) or None for the source size, JPEG quality,
# brightness lift, and why.
JOBS = [
    ("expert-ready", (860, 1290), 84, 1.00),   # home essay portrait, 2:3
    ("panelist-live", (1500, 1000), 84, 1.00),  # panelists hero
    ("mic-stage", (1536, 1024), 84, 1.06),     # the microphone Annette loves
    # The auditorium was "looking quite dull". The edit already lifted it;
    # a little more so the seats read as seats on a dim laptop panel.
    ("house-lit", (1500, 1000), 84, 1.05),
    # About hero. Cropped in around Annette rather than shown whole: in the
    # full frame she was a 200px figure in a wide room, too small to be
    # recognizably her, which was the whole point of the note.
    ("room-annette", None, 88, 1.00),
    # Footer plate. silk-footer (a lower-left sweep) was generated first and
    # dropped: in a banner 2.6 times wider than tall it filled one corner.
    # silk-banner crosses the full width. Multiplied by the site's warm
    # neutral so its white IS the footer's ground, with no seam where the
    # banner ends and the links begin.
    ("silk-banner", (1536, 1024), 80, 1.00),
]


def cover(im, size):
    """Center-crop to the target aspect, then resize."""
    tw, th = size
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    im = im.resize((round(sw * scale), round(sh * scale)), Image.LANCZOS)
    x = (im.width - tw) // 2
    y = (im.height - th) // 2
    return im.crop((x, y, x + tw, y + th))


def main():
    for name, size, q, lift in JOBS:
        src = RAW / f"{name}.png"
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        if name == "room-annette":
            im = im.crop((560, 0, 1480, 1024))      # 920 x 1024, her and the beam
        if size:
            im = cover(im, size)
        if lift != 1.0:
            im = ImageEnhance.Brightness(im).enhance(lift)
        if name == "silk-banner":
            im = ImageChops.multiply(im, Image.new("RGB", im.size, (251, 244, 240)))
        out = MEDIA / f"{name}.jpg"
        # A fresh Image carries no EXIF, and progressive JPEG paints a whole
        # low resolution frame first, which is what a hero should do.
        im.save(out, "JPEG", quality=q, optimize=True, progressive=True)
        print(f"  {out.name:22s} {im.width}x{im.height}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
