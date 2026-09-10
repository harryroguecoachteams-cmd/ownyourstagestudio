#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The hero loop: three beats of one lamp, joined so it never goes dark.

Feedback 3.0 asks for two things that pull against each other.

  note 1  "Lets use both the videos on the header and keep it in loop play one
           after the other make sure the transition is very smooth"
  note 3  "I absolutely dislike the artificial person stepping into the
           spotlight. Any chance your team could make him/her more natural and
           human looking?"

Both clips carry the same figure, and it is the figure she is objecting to. It
is not disliked for being small. It is disliked because it MATERIALISES out of
empty air inside the beam, and because at forty feet the generator gave it no
shoulders, no face and legs a head too long.

So the clips are used for the thing they are genuinely good at, which is the
light, and the person is a photograph.

    A   illuminating_person, 1.1s to 4.8s   the beam ignites and blooms
    B   searching_person,    1.2s to 4.4s   a narrower beam, different haze
    C   spot-figure.png                     a real person standing in it

A and B are cut BEFORE their figure appears, so nothing in this loop dissolves
into existence. A joins B on a slow cross fade, because they are the same
composition and the eye reads it as the light changing rather than as a cut.
B joins C on a shorter dissolve, and it is the one transition where the shot
size changes: a wide room becomes a portrait, so the beam appears to come
toward the camera rather than a person appearing inside it. C joins back to A
on a cross fade. Nothing in the loop flashes; a hero that strobes is a hero
somebody has to look away from.

    python _art/hero_loop.py            build assets/media/hero-spotlight.mp4
    python _art/hero_loop.py --keep     leave the intermediate beats on disk

The still is prepared here rather than in process.py because its geometry is
decided by where the loop needs the head to sit, not by the grade.
"""
import os
import sys
import shutil
import pathlib
import subprocess

from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(r"F:\Annette\own your studio\new changes")
RAW = ROOT / "_art" / "raw"
WORK = ROOT / "_art" / "_loop"
OUT = ROOT / "assets" / "media" / "hero-spotlight.mp4"
POSTER = ROOT / "assets" / "media" / "hero-spotlight-poster.jpg"
STILL = ROOT / "assets" / "media" / "hero-spotlight-still.jpg"

CLIP_A = SRC / "erasio_Spotlight_illuminating_person_in\u2026_1080p_202609081702.mp4"
CLIP_B = SRC / "erasio_Spotlight_searching_for_person_1080p_202609081634.mp4"

# The generator's four point sparkle, invisible at normal exposure and obvious
# under a two stop lift. Same box on everything that comes out of it.
DELOGO = "delogo=x=843:y=1686:w=116:h=112"

W, H = 1080, 1920
FPS = 24
# The panel is about 630 CSS px wide at 1440, so 1080 is already 1.7x. The
# expensive frames are the two wides, whose haze is fine moving grain; the one
# frame with a face in it barely moves, so x264 spends almost nothing on it.
CRF = 26

# Cuts. Both clips ignite from black; both hold an empty lit stage until their
# figure starts to resolve, A at 5.5s and B at 4.5s.
A_IN, A_OUT = 1.10, 4.80
B_IN, B_OUT = 1.20, 4.40
C_DUR = 4.30
XFADE = 0.85          # A to B, and C back to A
CLOSE = 0.55          # B to C, the one change of shot size

# Where the person sits in a 1080x1920 frame.
#
# The panel is object-fit:cover with object-position 50% 58%, and its aspect
# runs from 0.48 at a 900px viewport to 1.44 on a phone, where the hero stacks
# into a band. Solving cover at both ends leaves one horizontal strip that is
# on screen at every width:
#
#     y 740 to 1488
#
# The head goes just inside the top of it and the frame is dark below the hip,
# which is also where the generator put a hand it could not draw.
HEAD_Y = 800          # where the top of the hair lands
SRC_HEAD = 155        # top of the hair in spot-figure.png
SRC_CUT = 1180        # crop the still here: below the hip, above the hand


def run(*args):
    subprocess.run([a for a in args if a is not None], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def beam_extension(im, top_rows=48):
    """Continue the still's beam upward.

    The still is 1536 tall and only carries 155px above the head; the loop needs
    800. The extension is not invented light: it is the top of this frame's own
    column, sampled, narrowed toward the source the way a real beam converges,
    and blurred so there is no seam.
    """
    w = im.width
    strip = im.crop((0, 0, w, top_rows)).resize((w, 1), Image.LANCZOS)
    px = strip.load()
    return [px[x, 0] for x in range(w)]


def prep_still():
    """spot-figure.png -> a 1080x1920 frame the loop can cut to."""
    im = Image.open(RAW / "spot-figure.png").convert("RGB")
    sw, sh = im.size

    scale = W / float(sw)
    im = im.resize((W, int(round(sh * scale))), Image.LANCZOS)
    head = int(round(SRC_HEAD * scale))
    cut = int(round(SRC_CUT * scale))
    im = im.crop((0, 0, W, cut))

    canvas = Image.new("RGB", (W, H), (9, 8, 8))
    top = HEAD_Y - head                      # where row 0 of the still lands
    canvas.paste(im, (0, top))

    # --- the beam above the still -----------------------------------------
    row = beam_extension(im)
    ext = Image.new("RGB", (W, max(top, 1)))
    px = ext.load()
    n = ext.height
    for y in range(n):
        # 0 at the top of the frame, 1 where the still starts
        t = (y + 1) / float(n)
        # A beam narrows toward its source. Sampling the still's own top row
        # from the middle outwards at a shrinking width does that, and keeps
        # the color of this photograph rather than a color I chose.
        span = 0.34 + 0.66 * t
        for x in range(W):
            u = (x - W / 2.0) / span + W / 2.0
            if u < 0 or u >= W:
                px[x, y] = (9, 8, 8)
                continue
            r, g, b = row[int(u)]
            # falls off toward the fixture, which is out of frame
            k = 0.55 + 0.45 * t
            px[x, y] = (int(r * k), int(g * k), int(b * k))
    ext = ext.filter(ImageFilter.GaussianBlur(9))
    canvas.paste(ext, (0, 0))

    # feather the join so the sampled row is not a hard line
    band = 90
    joint = canvas.crop((0, top - band, W, top + band))
    joint = joint.filter(ImageFilter.GaussianBlur(7))
    canvas.paste(joint, (0, top - band))

    # --- the floor below the crop -----------------------------------------
    # Nothing is invented down here. The room falls off to black below the hip,
    # which is what the two clips do and what the panel's own bottom scrim
    # expects.
    floor = Image.new("RGB", (W, H - (top + im.height)), (9, 8, 8))
    canvas.paste(floor, (0, top + im.height))
    fade = canvas.crop((0, top + im.height - 220, W, top + im.height + 60))
    fpx = fade.load()
    for y in range(fade.height):
        k = max(0.0, 1.0 - (y / float(fade.height)) ** 0.75)
        for x in range(W):
            r, g, b = fpx[x, y]
            fpx[x, y] = (int(r * k) + 9, int(g * k) + 8, int(b * k) + 8)
    canvas.paste(fade.filter(ImageFilter.GaussianBlur(3)), (0, top + im.height - 220))

    WORK.mkdir(parents=True, exist_ok=True)
    out = WORK / "beat-c.png"
    canvas.save(out)
    return out


def cut(src, t_in, t_out, dst):
    run("ffmpeg", "-y", "-v", "error", "-ss", str(t_in), "-to", str(t_out),
        "-i", str(src), "-an",
        "-vf", "%s,fps=%d,scale=%d:%d,format=yuv420p" % (DELOGO, FPS, W, H),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", str(dst))


def push(still, dst, dur=C_DUR):
    """The still, given a very slow push in so it is a shot and not a photo."""
    run("ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", str(dur),
        "-i", str(still), "-an",
        "-vf", ("scale=%d:%d,zoompan=z='1.0+0.052*on/%d':d=1:"
                "x='iw/2-(iw/zoom/2)':y='ih*0.56-(ih/zoom*0.56)':s=%dx%d:fps=%d,"
                "format=yuv420p") % (W * 2, H * 2, int(dur * FPS), W, H, FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", str(dst))


def main():
    keep = "--keep" in sys.argv
    WORK.mkdir(parents=True, exist_ok=True)

    print("  beat A  illuminating %.2f-%.2f" % (A_IN, A_OUT), flush=True)
    cut(CLIP_A, A_IN, A_OUT, WORK / "a.mp4")
    print("  beat B  searching    %.2f-%.2f" % (B_IN, B_OUT), flush=True)
    cut(CLIP_B, B_IN, B_OUT, WORK / "b.mp4")
    print("  beat C  the person   %.2fs" % C_DUR, flush=True)
    push(prep_still(), WORK / "c.mp4")

    a = A_OUT - A_IN
    b = B_OUT - B_IN
    # xfade offsets are measured on the running timeline, and each transition
    # eats its own duration out of it.
    off_ab = a - XFADE
    off_bc = off_ab + b - CLOSE
    off_ca = off_bc + C_DUR - XFADE

    # The loop closes on itself: the tail of C dissolves into the head of A, so
    # the file's last frame already IS the first frame and the browser's own
    # loop point is invisible. That needs A twice, once as the opening shot and
    # once as the thing C dissolves into.
    filt = (
        "[0:v][1:v]xfade=transition=fade:duration=%.2f:offset=%.2f[ab];"
        "[ab][2:v]xfade=transition=fade:duration=%.2f:offset=%.2f[abc];"
        "[abc][3:v]xfade=transition=fade:duration=%.2f:offset=%.2f,"
        "format=yuv420p[v]"
    ) % (XFADE, off_ab, CLOSE, off_bc, XFADE, off_ca)

    print("  join    A+B+C, loop closed on A", flush=True)
    run("ffmpeg", "-y", "-v", "error",
        "-i", str(WORK / "a.mp4"), "-i", str(WORK / "b.mp4"),
        "-i", str(WORK / "c.mp4"),
        # the wrap: the first XFADE seconds of A again
        "-ss", "0", "-t", str(XFADE + 0.05), "-i", str(WORK / "a.mp4"),
        "-filter_complex", filt, "-map", "[v]", "-an",
        "-movflags", "+faststart",
        "-c:v", "libx264", "-preset", "veryslow", "-crf", str(CRF),
        "-pix_fmt", "yuv420p",
        "-x264-params", "aq-mode=3:aq-strength=1.15:deblock=-1,-1:psy-rd=1.0,0.15",
        str(OUT))

    # The poster is the first frame of A, so the panel is already lit before a
    # single byte of video has decoded.
    run("ffmpeg", "-y", "-v", "error", "-i", str(OUT), "-frames:v", "1",
        "-q:v", "4", str(POSTER))
    # The no-JS / reduced-motion still is beat C: if the room cannot move, the
    # thing worth showing is the person in the light, not an empty stage.
    Image.open(WORK / "beat-c.png").convert("RGB").save(STILL, quality=86,
                                                        optimize=True)

    kb = OUT.stat().st_size / 1024.0
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "csv=p=0", str(OUT)],
                         capture_output=True, text=True).stdout.strip()
    print("  %s  %.0f KB  %ss" % (OUT.name, kb, dur))
    print("  %s  %.0f KB" % (POSTER.name, POSTER.stat().st_size / 1024.0))
    print("  %s  %.0f KB" % (STILL.name, STILL.stat().st_size / 1024.0))
    if not keep:
        shutil.rmtree(WORK, ignore_errors=True)


if __name__ == "__main__":
    main()
