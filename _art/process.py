#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turn the raw commissions in _art/raw into the web assets the site loads.

Photography stays photography and code stays code, so nothing here paints:
it crops to the aspect the component needs, grades a little toward the
palette, strips metadata and compresses. The brand furniture (nameplates,
the stage lip, the mark) is drawn live in CSS over the top.

    python _art/process.py
"""
import pathlib, subprocess, sys, io
import numpy as np
from PIL import Image, ImageEnhance

HERE = pathlib.Path(__file__).parent
RAW = HERE / "raw"
OUT = HERE.parent / "assets" / "media"

# name, source, target width, aspect (w/h) or None to keep, vertical focus 0..1
STILLS = [
    # the six frames of the rig: 16:9, cropped to hold head and shoulders
    ("panel-host",   "host-onstage.png",        1200, 16 / 9, 0.46),
    ("panel-a",      "panel-a.png",              900, 16 / 9, 0.42),
    ("panel-b",      "panel-b.png",              900, 16 / 9, 0.42),
    ("panel-c",      "panel-c.png",              900, 16 / 9, 0.42),
    ("panel-d",      "panel-d.png",              900, 16 / 9, 0.42),
    ("panel-e",      "panel-e.png",              900, 16 / 9, 0.42),
    # panel-f is generated but not shipped: the rig is one host plus five
    # panelists, so the sixth face has nowhere to sit. Kept in raw/ as a
    # spare in case a face needs replacing.
    # ("panel-f",    "panel-f.png",              900, 16 / 9, 0.42),
    # shot 01, for the essay column: kept portrait
    ("expert",       "host-portrait.png",        860, None,   0.50),
    # shots 02 to 06
    ("panel-room",   "panel-conversation.png",  1500, 3 / 2,  0.50),
    ("attendee",     "attendee-screenlight.png", 1400, 16 / 9, 0.50),
    ("room-empty",   "empty-room.png",          1500, 16 / 9, 0.52),
    # feedback 2.0: the About room was liked but empty; same room, one figure
    ("room-figure",  "room-figure.png",         1500, 16 / 9, 0.52),
    # the panelist pages had the Experience page's pictures
    ("panelist-mid", "panelist-speaking.png",   1500, 3 / 2,  0.48),
    ("panelist-one", "panelist-framed.png",      900, 16 / 9, 0.42),
    ("desk",         "desk-still.png",          1400, 16 / 9, 0.52),
    ("control",      "control-room.png",        1500, 16 / 9, 0.50),
    ("texture",      "texture-plate.png",       1400, 16 / 9, 0.50),
    ("clips",        "content-clips.png",       1400, 16 / 9, 0.50),
]

# name, source, seconds to keep, poster frame
CLIPS = [
    ("stage-build", "stage-build.mp4", None),
    ("panel-drift", "panel-room.mp4",  None),
]


def warm_shadows(im, amt_r=8.0, amt_b=11.0, knee=118.0, gamma=1.45):
    """Pull the blue out of the shadows.

    Every one of these commissions came back with a cool shadow: measured on
    the darkest 30% of each frame, blue ran 7 to 33 points ahead of red. That
    was right for the old identity, whose ground was Authority Navy. The
    September brand sheet's dark is Charcoal, a warm near-black, so a cool
    shadow now reads as a blue rectangle sitting on a brown page and it is
    the loudest thing left on the site that says the pictures and the palette
    were chosen by different people.

    The shift is masked by luminance, so it lands on the shadows and the
    lower mid-tones and leaves the key light alone. Faces sit in the key, so
    skin is untouched -- this warms the ROOM, not the people in it.
    """
    a = np.asarray(im).astype(np.float32)
    lum = .2126 * a[:, :, 0] + .7152 * a[:, :, 1] + .0722 * a[:, :, 2]
    w = np.clip((knee - lum) / knee, 0, 1) ** gamma
    a[:, :, 0] = np.clip(a[:, :, 0] + w * amt_r, 0, 255)
    a[:, :, 1] = np.clip(a[:, :, 1] - w * amt_b * .28, 0, 255)
    a[:, :, 2] = np.clip(a[:, :, 2] - w * amt_b, 0, 255)
    return Image.fromarray(a.astype(np.uint8))


def still(name, src, width, aspect, focus):
    p = RAW / src
    if not p.exists():
        print("  miss  %s" % src); return
    im = Image.open(p).convert("RGB")
    if aspect:
        w, h = im.size
        th = round(w / aspect)
        if th <= h:
            top = max(0, min(h - th, round(h * focus - th / 2)))
            im = im.crop((0, top, w, top + th))
        else:                                    # source is wider than the target
            tw = round(h * aspect)
            left = max(0, (w - tw) // 2)
            im = im.crop((left, 0, left + tw, h))
    im = im.resize((width, round(width * im.size[1] / im.size[0])), Image.LANCZOS)
    # A whisper toward the palette. The ground is Charcoal, not neutral
    # black and no longer Authority Navy, so the shadows come warm.
    im = warm_shadows(im)
    im = ImageEnhance.Color(im).enhance(0.96)
    im = ImageEnhance.Contrast(im).enhance(1.03)
    out = OUT / (name + ".jpg")
    im.save(out, quality=84, optimize=True, progressive=True)   # no exif carried
    print("  %-14s %s  %.0f KB" % (name, im.size, out.stat().st_size / 1024))


def clip(name, src, _):
    p = RAW / src
    if not p.exists():
        print("  miss  %s" % src); return
    out = OUT / (name + ".mp4")
    # "Video lacks clarity here." CRF 29 on a very dark, very fine-grained clip
    # is false economy: h.264 spends its bits on the grain and smears the faces,
    # and on a navy scene the blocking shows up as banding in the falloff. 23
    # with a tuned deblock roughly doubles the file and makes it a picture again.
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(p), "-an",
                    "-movflags", "+faststart", "-c:v", "libx264", "-preset", "veryslow",
                    "-crf", "23", "-pix_fmt", "yuv420p",
                    "-x264-params", "aq-mode=3:aq-strength=1.0:deblock=-1,-1:psy-rd=1.0,0.15",
                    # the same warm-shadow move the stills get, so a poster
                    # frame and the clip it came from are one picture
                    "-vf", "colorbalance=rs=0.055:gs=-0.016:bs=-0.075,scale=1280:-2",
                    str(out)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out),
                    "-vf", "select=eq(n\\,0)", "-frames:v", "1", "-q:v", "5",
                    str(OUT / (name + "-poster.jpg"))], check=True)
    print("  %-14s %.0f KB  (+poster)" % (name, out.stat().st_size / 1024))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    print("stills")
    for a in STILLS:
        still(*a)
    print("clips")
    for c in CLIPS:
        clip(*c)
