#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The hero clip, 14 September: the searching spotlight reveal.

Harsh dropped a new generation into the project folder and asked for it on
the site:

    Spotlight_revealing_person_in_dark_20260914121410_gwr_video_mvp.mp4
    1080x1920, 24fps, 8.0s, h264 + a silent AAC track, 1.6MB

Measured, not eyeballed (ffmpeg -> numpy, per frame):

    0.0 - 1.3s   the lamp fades up from black onto an empty floor
    2.0 - 2.8s   the beam blooms and settles, the search beat
    3.4 - 4.0s   the pool comes up to full
    4.4 - 5.0s   the figure resolves inside the light, no walk-in
    5.0 - 8.0s   she holds, arms folded, eye line to camera; the rim
                 light keeps building on her, the haze barely moves

    silhouette   x 400..612, head at y 682 (35.5%), feet at 1690 (88%),
                 her shadow to 1906; the pool is brightest at y 1552
    watermark    none. High pass of the temporal mean over the hold
                 peaks at 1.7 luma units outside the figure, which is
                 noise. The erasio clips needed a delogo box; this does
                 not.

It replaces hero-spotlight.mp4 (the erasio "illuminating person" cut from
feedback 4.0, built by hero_loop.py). New file NAMES, not the same path
with new bytes: media is not content hashed the way oyss.css and oyss.js
are, and GitHub Pages holds an mp4 at a given URL long enough that the
old clip would keep arriving for people who had seen it.

THE LOOP, and why the file does not start at its own first frame:

The element carries `loop` (feedback 4.0: "make sure that video will
play in loop") and the raw clip cannot loop: first frame against last,
mean absolute difference 53 of 255, and the whole subject is the
difference. So, exactly as hero_loop.py did, the tail dissolves into
the head using only the clip's own frames. Here the head is the lamp
fading up from black, so the dissolve reads as the light going down on
her and coming back up to search again, which is the sentence the clip
was generated to say.

The wrap sits at the START of the output rather than the end, for one
reason: the poster is the first frame. Frame 0 of the source is near
black (mean luma 6), and a black rectangle is what a slow connection
would show as the hero. Leading with the wrap makes the poster, and the
reduced-motion still, the lit woman.

The audio track is dropped. The element is muted anyway.

    python _art/hero_reveal.py
"""
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(r"F:\Annette\own your studio")
CLIP = SRC / "Spotlight_revealing_person_in_dark_20260914121410_gwr_video_mvp.mp4"

OUT = ROOT / "assets" / "media" / "hero-reveal.mp4"
POSTER = ROOT / "assets" / "media" / "hero-reveal-poster.jpg"
STILL = ROOT / "assets" / "media" / "hero-reveal-still.jpg"

L = 8.0                     # the whole clip; the search IS the content
D = 0.90                    # the wrap dissolve, inside the steady hold
FPS = 24


def run(*args):
    subprocess.run(list(args), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def main():
    # Output runs L-D seconds: the first D are the old tail dissolving
    # into the old head, the rest is the shot untouched. The output's
    # last frame and its first frame are then the same moment, so the
    # browser's own loop point has nothing to show.
    filt = (
        "[0:v]fps=%d,format=yuv420p,split=3[s0][s1][s2];"
        "[s0]trim=0:%.3f,setpts=PTS-STARTPTS[head];"
        "[s1]trim=%.3f:%.3f,setpts=PTS-STARTPTS[tail];"
        "[head][tail]blend=all_expr='B*(1-(T/%.3f))+A*(T/%.3f)'[wrap];"
        "[s2]trim=%.3f:%.3f,setpts=PTS-STARTPTS[mid];"
        "[wrap][mid]concat=n=2:v=1:a=0[v]"
    ) % (FPS, D, L - D, L, D, D, D, L - D)

    print("  whole clip, %.2fs wrap dissolve" % D, flush=True)
    run("ffmpeg", "-y", "-v", "error", "-i", str(CLIP), "-an",
        "-filter_complex", filt, "-map", "[v]",
        "-movflags", "+faststart",
        "-c:v", "libx264", "-preset", "veryslow", "-crf", "27",
        "-pix_fmt", "yuv420p",
        "-x264-params", "aq-mode=3:aq-strength=1.15:deblock=-1,-1",
        str(OUT))

    # Poster: the output's own first frame, so what the browser paints
    # before the clip arrives is the frame it then starts on.
    run("ffmpeg", "-y", "-v", "error", "-i", str(OUT), "-frames:v", "1",
        "-q:v", "4", str(POSTER))
    # Reduced-motion still: the held frame from the source, at full
    # quality, since it may be the only thing that reader ever sees.
    run("ffmpeg", "-y", "-v", "error", "-ss", "7.5", "-i", str(CLIP),
        "-frames:v", "1", "-q:v", "3", str(STILL))

    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "csv=p=0", str(OUT)],
                         capture_output=True, text=True).stdout.strip()
    for f in (OUT, POSTER, STILL):
        print("  %-24s %6.0f KB%s" % (f.name, f.stat().st_size / 1024.0,
                                      ("  %ss" % dur) if f is OUT else ""))


if __name__ == "__main__":
    main()
