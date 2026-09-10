#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The explainer video, encoded for the web.

Feedback 4.0, note 3: "Add the video here that I will be sharing it with you",
pointing at the wide figure at the end of the home page's "what you keep"
section. The file arrived as
`Own Your Stage Studio Explainer Video_1080p_caption.mp4`:
1920x1080, 25fps, 2 minutes 22, stereo AAC, **106 MB**.

106 MB cannot go on a web page, so this re-encodes it. Three decisions:

**720p, not 1080p.** The figure it sits in is at most 1180 CSS px wide, so 720p
is already above 1x on a normal screen and above 2x on a phone. The captions
are burned into the picture, which is the one thing that suffers from a
downscale, so the encode is tuned to protect fine detail rather than to hit a
number: CRF 26 with the same psy and deblock settings the site's other clips
use, and no denoise.

**The audio stays.** It is an explainer with a voice over. 128k AAC.

**It does not autoplay and does not preload.** A two minute video with sound is
something a reader chooses. The page ships a poster frame and the browser
fetches nothing until somebody presses play, so the ~11 MB costs nothing to
anyone who scrolls past it.

    python _art/explainer.py
"""
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = (pathlib.Path(r"F:\Annette\own your studio\new changes") /
       "Own Your Stage Studio Explainer Video_1080p_caption.mp4")
OUT = ROOT / "assets" / "media" / "explainer.mp4"
POSTER = ROOT / "assets" / "media" / "explainer-poster.jpg"

# The frame the poster is taken from. Second 4 caught the opening title
# mid dissolve, with half a sentence faded out, which looks like a broken
# render rather than a poster. Second 2 is the same card fully on.
POSTER_AT = "2.0"


def run(*args):
    subprocess.run(list(args), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def main():
    if not SRC.exists():
        raise SystemExit("missing source: %s" % SRC)
    print("  source  %.0f MB" % (SRC.stat().st_size / 1048576.0), flush=True)

    run("ffmpeg", "-y", "-v", "error", "-i", str(SRC),
        "-vf", "scale=1280:-2",
        "-movflags", "+faststart",
        "-c:v", "libx264", "-preset", "veryslow", "-crf", "26",
        "-pix_fmt", "yuv420p",
        "-x264-params", "aq-mode=3:aq-strength=1.0:deblock=-1,-1:psy-rd=1.0,0.15",
        "-c:a", "aac", "-b:a", "128k", "-ac", "2",
        str(OUT))

    run("ffmpeg", "-y", "-v", "error", "-ss", POSTER_AT, "-i", str(OUT),
        "-frames:v", "1", "-q:v", "4", str(POSTER))

    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "csv=p=0", str(OUT)],
                         capture_output=True, text=True).stdout.strip()
    print("  %s  %.1f MB  %ss" % (OUT.name, OUT.stat().st_size / 1048576.0, dur))
    print("  %s  %.0f KB" % (POSTER.name, POSTER.stat().st_size / 1024.0))


if __name__ == "__main__":
    main()
