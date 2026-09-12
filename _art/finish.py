#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spotlight hero: finish take7 into the 1920x1080 24fps 8s deliverable.

Sora would not pan the follow spot in nine takes, so the search is built here:
a crop window drifts over take7's own empty first 3.4s (the floor is
featureless, so a window pan reads as the light moving), eases to full frame
and locks at 4.0s, then the reveal plays untouched. The empty phase is
stretched 1.3x so the reveal lands at 4.4s as the brief asks. One Lanczos
resample per frame does both the crop and the 720p -> 1080p upscale.

    python _art/finish.py            writes raw/spotlight/spotlight-hero.mp4
"""
import subprocess, pathlib, numpy as np
from PIL import Image

D = pathlib.Path(__file__).parent / "raw" / "spotlight"
SRC = D / "take7.mp4"
OUT = D / "spotlight-hero.mp4"
W, H, SFPS = 1280, 720, 30
OW, OH, FPS, DUR = 1920, 1080, 24, 8.0
PX, PY = 515, 470          # measured pool centroid during the empty phase
SPLIT_SRC, SPLIT_OUT = 3.4, 4.4   # source 0..3.4s plays as output 0..4.4s

# (t, pool x fraction of output width, zoom)
KEYS = [(0.0, 0.40, 1.32), (0.8, 0.40, 1.32), (2.3, 0.27, 1.32),
        (3.4, 0.52, 1.32), (4.0, PX / W, 1.00), (99, PX / W, 1.00)]


def smooth(a, b, u):
    u = 0.0 if u < 0 else 1.0 if u > 1 else u
    u = u * u * (3 - 2 * u)
    return a + (b - a) * u


def keyed(t):
    for (t0, p0, z0), (t1, p1, z1) in zip(KEYS, KEYS[1:]):
        if t0 <= t < t1:
            u = (t - t0) / (t1 - t0)
            return smooth(p0, p1, u), smooth(z0, z1, u)
    return KEYS[-1][1], KEYS[-1][2]


def window(t):
    p, z = keyed(t)
    wob = 0.008 * max(0.0, 1 - t / 3.8) * np.sin(2 * np.pi * 0.9 * t + 1.1)  # hand on the handle
    p += wob
    cw, ch = W / z, H / z
    x = PX - p * cw
    y = PY - (PY / H) * ch
    x = min(max(x, 0), W - cw); y = min(max(y, 0), H - ch)
    return x, y, cw, ch


raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(SRC), "-f", "rawvideo",
                      "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
N = len(frames)

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                        "-s", "%dx%d" % (OW, OH), "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT)],
                       stdin=subprocess.PIPE)
for k in range(int(DUR * FPS)):
    t = k / FPS
    ts = t * SPLIT_SRC / SPLIT_OUT if t < SPLIT_OUT else SPLIT_SRC + (t - SPLIT_OUT)
    f = ts * SFPS
    i0 = min(int(f), N - 1); i1 = min(i0 + 1, N - 1); a = f - int(f)
    src = (frames[i0] * (1 - a) + frames[i1] * a).astype(np.uint8) if a > 0.01 else frames[i0]
    x, y, cw, ch = window(t)
    im = Image.fromarray(src).resize((OW, OH), Image.LANCZOS, box=(x, y, x + cw, y + ch))
    enc.stdin.write(np.asarray(im).tobytes())
enc.stdin.close(); enc.wait()
print("wrote", OUT, "%.0f KB" % (OUT.stat().st_size / 1024))
