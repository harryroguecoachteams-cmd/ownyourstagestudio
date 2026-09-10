#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The hero clip, rolled back and made loopable.

Feedback 4.0, note 1:

    "Roll It back to the previous video style, make sure that video will play
     in loop"

Round 8 had replaced the hero with a three beat sequence: her two clips cut to
the light only, then a photograph of a real person standing in the beam. That
answered feedback 3.0's "I absolutely dislike the artificial person stepping
into the spotlight", and she has now asked for the earlier footage back. This
script builds that earlier footage. The three beat version is in the history at
commit 59fd124 if it is ever wanted again.

The cut is the one from the human pass, unchanged and quoted from DELIVERY.md:

    ffmpeg -ss 3.5 -to 8.04 -i <source> -an -movflags +faststart \\
      -vf "delogo=x=843:y=1686:w=116:h=112" \\
      -c:v libx264 -preset veryslow -crf 27 -pix_fmt yuv420p \\
      -x264-params "aq-mode=3:aq-strength=1.15:deblock=-1,-1"

THE ONE THING THAT IS NOT A STRAIGHT ROLLBACK, and why:

That cut opens on a lit but empty stage and ends with the figure standing in
the beam. Put `loop` on it as it is and the figure vanishes every 4.5 seconds
and resolves again out of nothing. Measured, first frame against last: mean
absolute difference 18.93 of 255, and the whole subject IS the difference. It
does not read as a loop, it reads as a bug.

So the tail dissolves back into the head. Nothing is added: the dissolve is
made only out of this clip's own frames, and the output is the same shot with
its last 0.7 seconds cross faded onto its first 0.7. The light finds him,
holds, lets go, and finds him again, which is the sentence the clip was cut to
say in the first place.

    python _art/hero_loop.py
"""
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(r"F:\Annette\own your studio\new changes")
OUT = ROOT / "assets" / "media" / "hero-spotlight.mp4"
POSTER = ROOT / "assets" / "media" / "hero-spotlight-poster.jpg"

CLIP = SRC / "erasio_Spotlight_illuminating_person_in\u2026_1080p_202609081702.mp4"

# The generator's four point sparkle, invisible at normal exposure and obvious
# under a two stop lift.
DELOGO = "delogo=x=843:y=1686:w=116:h=112"

IN, TO = 3.5, 8.04          # the human pass cut, unchanged
L = TO - IN                 # 4.54s
D = 0.70                    # the wrap dissolve
FPS = 24


def run(*args):
    subprocess.run(list(args), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def main():
    # Output runs L-D seconds: the first D are the old tail dissolving into
    # the old head, the rest is the shot untouched. The output's last frame and
    # its first frame are then the same moment, so the browser's own loop point
    # has nothing to show.
    filt = (
        "[0:v]%s,fps=%d,format=yuv420p,split=3[s0][s1][s2];"
        "[s0]trim=0:%.3f,setpts=PTS-STARTPTS[head];"
        "[s1]trim=%.3f:%.3f,setpts=PTS-STARTPTS[tail];"
        "[head][tail]blend=all_expr='B*(1-(T/%.3f))+A*(T/%.3f)'[wrap];"
        "[s2]trim=%.3f:%.3f,setpts=PTS-STARTPTS[mid];"
        "[wrap][mid]concat=n=2:v=1:a=0[v]"
    ) % (DELOGO, FPS, D, L - D, L, D, D, D, L - D)

    print("  cut     %.2f to %.2f, %.2fs wrap dissolve" % (IN, TO, D), flush=True)
    run("ffmpeg", "-y", "-v", "error", "-ss", str(IN), "-to", str(TO),
        "-i", str(CLIP), "-an",
        "-filter_complex", filt, "-map", "[v]",
        "-movflags", "+faststart",
        "-c:v", "libx264", "-preset", "veryslow", "-crf", "27",
        "-pix_fmt", "yuv420p",
        "-x264-params", "aq-mode=3:aq-strength=1.15:deblock=-1,-1",
        str(OUT))

    run("ffmpeg", "-y", "-v", "error", "-i", str(OUT), "-frames:v", "1",
        "-q:v", "4", str(POSTER))

    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of", "csv=p=0", str(OUT)],
                         capture_output=True, text=True).stdout.strip()
    print("  %s  %.0f KB  %ss" % (OUT.name, OUT.stat().st_size / 1024.0, dur))
    print("  %s  %.0f KB" % (POSTER.name, POSTER.stat().st_size / 1024.0))


if __name__ == "__main__":
    main()
