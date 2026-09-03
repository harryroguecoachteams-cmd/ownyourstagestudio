#!/usr/bin/env python3
"""
Own Your Stage Studio - "How this works" brand film.

One continuous take on one stage, six beats. The stage never cuts: the
ground, the figure and the beam are constant, and each beat adds exactly
one idea on top of them. That is the deck's rule about light rendered as
a timeline - a light cue does not restart the scene, it changes what you
can see in it.

Renders raw RGB straight into ffmpeg. No frame files.
"""

import math
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1600, 900
FPS = 30

VOID = (5, 8, 15)
NAVY = (16, 26, 49)
IVORY = (247, 242, 232)
GOLD = (221, 170, 82)
WARM = (255, 235, 196)
CRIMSON = (201, 46, 56)
ASH = (215, 206, 192)

FDIR = "fonts/"
def serif(px, wght=400):
    f = ImageFont.truetype(FDIR + "CrimsonPro[wght].ttf", px)
    f.set_variation_by_axes([wght])
    return f
def sans(px, wght=400):
    f = ImageFont.truetype(FDIR + "WorkSans[wght].ttf", px)
    f.set_variation_by_axes([wght])
    return f

F_EYEBROW = sans(21, 600)
F_HEAD    = serif(78, 400)
F_SUB     = sans(28, 300)
F_TALLY   = sans(16, 600)
F_TILE    = sans(15, 500)
F_SIGN    = serif(70, 400)
F_MARK    = sans(22, 600)
F_MARKSUB = sans(12, 500)

# ---------------------------------------------------------------- geometry
CX, GY = 800, 800           # centre of the stage, and the floor it stands on
HOSTY = 410                 # where the host frame settles
ROWY  = 596                 # the panel row under it
STRIPY = 430                # where the rig flattens into a content strip
BEAT = [
    (0.0,  4.2),   # 0  hidden
    (4.2,  8.6),   # 1  the stage
    (8.6, 13.0),   # 2  the panel
    (13.0, 17.4),  # 3  live
    (17.4, 21.2),  # 4  after
    (21.2, 25.0),  # 5  sign off
]
DUR = BEAT[-1][1]
NFRAMES = int(DUR * FPS)

COPY = [
    ("The problem",  "You are your field's best kept secret.",
     "Which is a compliment and a business problem at the same time."),
    ("What we do",   "We build you a stage.",
     "One virtual panel event, produced properly, built around your subject."),
    ("Who is on it", "We cast the room.",
     "Up to five vetted experts, chosen to make your topic land harder."),
    ("On the night", "We run the show.",
     "Branded, produced, live. You lead the conversation. We handle the rest."),
    ("Afterwards",   "It keeps working.",
     "The recording becomes content that keeps you visible for months."),
]

# The five panelists sit in one row under a larger host frame: the rig the
# client actually buys, not an abstract arc. Offsets are from CX.
ROW = (-330, -165, 0, 165, 330)
FRAME_W, FRAME_H = 150, 92
HOST_W, HOST_H = 240, 148


# ---------------------------------------------------------------- helpers
def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v

def seg(t, t0, t1):
    """0..1 progress across a window."""
    return clamp((t - t0) / (t1 - t0)) if t1 > t0 else 0.0

def ease_out(t):
    return 1 - (1 - t) ** 3

def ease_io(t):
    return t * t * (3 - 2 * t)

def lerp(a, b, t):
    return a + (b - a) * t

def rgba(c, a):
    return (c[0], c[1], c[2], int(clamp(a) * 255))

def beat_alpha(t, i, hold_in=0.55, hold_out=0.42):
    """Type fades up at the head of its beat and out at the tail."""
    t0, t1 = BEAT[i]
    if t < t0 or t > t1:
        return 0.0, 0.0
    a_in = ease_out(seg(t, t0, t0 + hold_in))
    a_out = 1 - ease_io(seg(t, t1 - hold_out, t1))
    a = a_in * a_out
    rise = (1 - ease_out(seg(t, t0, t0 + hold_in))) * 16
    return a, rise

def tracked(d, xy, text, font, fill, track=3.4):
    """Work Sans has no tracking in PIL, so letter-space by hand."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + track
    return x


# ---------------------------------------------------------------- prebuilt layers
def build_ground():
    """Navy sky, void floor, one horizon. Built once."""
    base = Image.new("RGB", (W, H), VOID)
    px = base.load()
    for y in range(H):
        if y < GY:
            k = (y / GY) ** 1.25
            c = tuple(int(lerp(NAVY[i], (9, 14, 26)[i], k)) for i in range(3))
        else:
            k = (y - GY) / (H - GY)
            c = tuple(int(lerp((11, 17, 32)[i], VOID[i], k ** 0.7)) for i in range(3))
        for x in range(W):
            px[x, y] = c
    # a wide, very soft pool of ambient on the horizon so the floor reads as a floor
    amb = Image.new("L", (W, H), 0)
    ImageDraw.Draw(amb).ellipse([CX - 640, GY - 66, CX + 640, GY + 66], fill=38)
    amb = amb.filter(ImageFilter.GaussianBlur(70))
    base = Image.composite(Image.new("RGB", (W, H), (26, 36, 60)), base, amb)
    return base


def build_beam():
    """The cone. Precomputed at full strength; per frame we only scale alpha."""
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.polygon([(CX - 26, -60), (CX + 26, -60), (CX + 250, GY + 20), (CX - 250, GY + 20)], fill=150)
    d.polygon([(CX - 12, -60), (CX + 12, -60), (CX + 120, GY + 20), (CX - 120, GY + 20)], fill=225)
    m = m.filter(ImageFilter.GaussianBlur(34))
    # light falls off as it travels
    fall = Image.new("L", (W, H), 0)
    fp = fall.load()
    for y in range(H):
        v = int(255 * clamp(1.0 - (y / (GY + 60)) ** 1.5))
        for x in range(W):
            fp[x, y] = v
    m = Image.composite(m, Image.new("L", (W, H), 0), fall)
    layer = Image.new("RGBA", (W, H), WARM + (0,))
    layer.putalpha(m)
    return layer


def build_pool():
    """Where the beam lands. Gold, flat, no flare."""
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([CX - 250, GY - 34, CX + 250, GY + 34], fill=78)
    d.ellipse([CX - 132, GY - 17, CX + 132, GY + 17], fill=140)
    m = m.filter(ImageFilter.GaussianBlur(40))
    layer = Image.new("RGBA", (W, H), GOLD + (0,))
    layer.putalpha(m)
    return layer


def build_scrim():
    """The beam's hottest column runs straight through the title safe area.
    One gradient over the top third buys the type its contrast back without
    touching the stage."""
    m = Image.new("L", (W, H), 0)
    mp = m.load()
    for y in range(H):
        v = int(232 * clamp(1 - (y / 360) ** 1.4)) if y < 360 else 0
        for x in range(W):
            mp[x, y] = v
    layer = Image.new("RGBA", (W, H), (4, 7, 14, 0))
    layer.putalpha(m)
    return layer


def scale_alpha(layer, k):
    if k <= 0.001:
        return None
    out = layer.copy()
    a = out.getchannel("A").point(lambda v, k=k: int(v * k))
    out.putalpha(a)
    return out


GROUND = build_ground()
BEAM = build_beam()
POOL = build_pool()
SCRIM = build_scrim()


# ---------------------------------------------------------------- the rig
def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def draw_figure(d, lit, a=1.0):
    """One person, standing. Never a lamp, never a podium, never a mic stand."""
    if a <= 0.01:
        return
    v = int(lerp(34, 250, lit))
    c = (v, v, v, int(255 * a))
    d.ellipse([CX - 11, GY - 152, CX + 11, GY - 127], fill=c)
    P = lambda x, y: (CX + x, GY + y)
    d.polygon([P(-25, -112), P(-14, -124), P(14, -124), P(25, -112),
               P(28, -74), P(23, -60), P(18, -74), P(17, -42),
               P(15, 0), P(4, 0), P(5, -42),
               P(-5, -42), P(-4, 0), P(-15, 0),
               P(-17, -42), P(-18, -74), P(-23, -60), P(-28, -74)], fill=c)
    d.ellipse([CX - 52, GY - 8, CX + 52, GY + 10], fill=(0, 0, 0, int(160 * lit * a)))


def draw_frame(d, cx, cy, w, h, a, host=False, on=False):
    """A branded panel frame. It has to read as a person on a stage at 120px."""
    if a <= 0.008:
        return
    A = lambda k: int(255 * clamp(a * k))
    box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
    rrect(d, box, 7, fill=(17, 27, 50, A(0.94)))
    lit = host or on
    rrect(d, box, 7, outline=(GOLD if lit else ASH) + (A(0.95 if lit else 0.40),),
          width=3 if lit else 1)
    # the person inside it
    hr = h * 0.125
    sk = (150, 162, 186) if lit else (104, 116, 140)
    d.ellipse([cx - hr, cy - h * 0.30, cx + hr, cy - h * 0.30 + 2 * hr], fill=sk + (A(0.9),))
    d.polygon([(cx - hr * 2.0, cy - h * 0.02), (cx + hr * 2.0, cy - h * 0.02),
               (cx + hr * 1.5, cy + h * 0.30), (cx - hr * 1.5, cy + h * 0.30)],
              fill=sk + (A(0.9),))
    # the lower third: the thing that makes a call look produced
    pw = w * 0.52
    d.rectangle([cx - w / 2 + 9, cy + h / 2 - 17, cx - w / 2 + 9 + pw, cy + h / 2 - 11],
                fill=(GOLD if lit else ASH) + (A(0.62),))
    d.rectangle([cx - w / 2 + 9, cy + h / 2 - 8, cx - w / 2 + 9 + pw * 0.62, cy + h / 2 - 4],
                fill=ASH + (A(0.30),))


def slot(t, i):
    """Where rig element i is at time t. 0 is the host, 1..5 the panel.

    One function so the fly-in, the settle and the flatten cannot disagree
    about where a frame is, which is how a rig ends up with a frame in two
    places at once."""
    if i == 0:
        born = ease_out(seg(t, BEAT[2][0], BEAT[2][0] + 1.0))
        # the host frame grows out of the figure standing in the beam
        x, y = CX, lerp(GY - 100, HOSTY, born)
        s = lerp(0.16, 1.0, born)
        w, h = HOST_W, HOST_H
        a = born
        sx = CX - 455
    else:
        t0 = BEAT[2][0] + 0.55 + (i - 1) * 0.20
        born = ease_out(seg(t, t0, t0 + 0.85))
        x = lerp(CX, CX + ROW[i - 1], born)
        y = lerp(HOSTY + 30, ROWY, born)
        s = lerp(0.42, 1.0, born)
        w, h = FRAME_W, FRAME_H
        a = born
        sx = CX - 455 + i * 182
    # beat 4: the rig flattens into a strip of things you keep
    fr = ease_io(seg(t, BEAT[4][0] + 0.15, BEAT[4][0] + 1.35))
    if fr > 0:
        x = lerp(x, sx, fr)
        y = lerp(y, STRIPY, fr)
        s = lerp(s, (135 / w), fr)
    a *= 1 - ease_io(seg(t, BEAT[5][0], BEAT[5][0] + 0.9))
    return x, y, w * s, h * s, a


# ---------------------------------------------------------------- the frame
def render(t):
    img = GROUND.copy()

    # --- the light --------------------------------------------------------
    # Beat 0 is one dim work light. The beam strikes on the head of beat 1
    # and never restarts, because a cue does not fire twice.
    strike = ease_out(seg(t, BEAT[1][0], BEAT[1][0] + 1.3))
    beam_k = 0.11 + 0.89 * strike
    pool_k = 0.05 + 0.95 * ease_out(seg(t, BEAT[1][0] + 0.3, BEAT[1][0] + 1.8))
    pool_k *= lerp(1.0, 0.45, ease_io(seg(t, BEAT[2][0], BEAT[2][0] + 1.2)))
    if t > BEAT[5][0]:
        dip = lerp(1.0, 0.22, ease_io(seg(t, BEAT[5][0], BEAT[5][0] + 1.1)))
        beam_k *= dip
        pool_k *= dip
    beam_k *= 1 + 0.035 * math.sin(t * 1.15)

    for layer, k in ((BEAM, beam_k), (POOL, pool_k)):
        sc = scale_alpha(layer, clamp(k))
        if sc:
            img = Image.alpha_composite(img.convert("RGBA"), sc).convert("RGB")

    img = Image.alpha_composite(img.convert("RGBA"), SCRIM).convert("RGB")

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    # --- the room ---------------------------------------------------------
    # An audience drawn as light, not as people: three shallow rows of it
    # in the foreground, filling while the show is live.
    aa = ease_out(seg(t, BEAT[3][0] + 0.4, BEAT[3][0] + 2.4)) * \
         (1 - ease_io(seg(t, BEAT[4][0], BEAT[4][0] + 0.9)))
    if aa > 0.01:
        for r, (ry, n, sp) in enumerate(((712, 15, 96), (766, 17, 86), (826, 19, 78))):
            for i in range(n):
                ax = CX + (i - (n - 1) / 2) * sp
                ay = ry + math.sin(i * 1.7 + r) * 5
                if not (30 < ax < W - 30):
                    continue
                k = aa * (0.46 - r * 0.10) * (0.55 + 0.45 * math.cos((ax - CX) / 700))
                rad = 4 + r
                d.ellipse([ax - rad, ay - rad, ax + rad, ay + rad], fill=rgba(GOLD, k))

    # --- the figure, and the rig it becomes -------------------------------
    lit = 0.16 + 0.84 * ease_out(seg(t, BEAT[1][0] + 0.2, BEAT[1][0] + 1.5))
    draw_figure(d, lit, 1 - ease_io(seg(t, BEAT[2][0], BEAT[2][0] + 0.6)))

    live = BEAT[3][0] < t < BEAT[4][0]
    cut = int((t - BEAT[3][0]) / 0.66) % 6 if live else -1
    for i in (1, 2, 3, 4, 5, 0):          # host painted last, it sits in front
        x, y, w, h, a = slot(t, i)
        draw_frame(d, x, y, w, h, a, host=(i == 0), on=(i == cut))

    # --- the tally --------------------------------------------------------
    la = ease_out(seg(t, BEAT[3][0] + 0.15, BEAT[3][0] + 0.7)) * \
         (1 - ease_io(seg(t, BEAT[4][0] - 0.45, BEAT[4][0])))
    if la > 0.01:
        blink = 0.70 + 0.30 * (math.sin(t * 4.6) * 0.5 + 0.5)
        by = HOSTY - HOST_H / 2 - 34
        rrect(d, [CX - 66, by - 18, CX + 66, by + 18], 18, fill=rgba(CRIMSON, la * blink))
        tracked(d, (CX - 42, by - 10), "ON AIR", F_TALLY, rgba(IVORY, la), 2.6)

    # --- what you keep ----------------------------------------------------
    ca = ease_out(seg(t, BEAT[4][0] + 1.05, BEAT[4][0] + 1.7)) * \
         (1 - ease_io(seg(t, BEAT[5][0] - 0.5, BEAT[5][0])))
    if ca > 0.01:
        for i, lab in enumerate(("REPLAY", "CLIPS", "QUOTES", "AUDIO", "POSTS", "PROOF")):
            x = CX - 455 + i * 182
            wlab = sum(d.textlength(c, font=F_TILE) + 2.2 for c in lab)
            tracked(d, (x - wlab / 2, STRIPY + 60), lab, F_TILE, rgba(ASH, ca * 0.85), 2.2)

    # --- type -------------------------------------------------------------
    for i, (eyebrow, head, sub) in enumerate(COPY):
        a, rise = beat_alpha(t, i)
        if a <= 0.01:
            continue
        y = 92 + rise
        we = sum(d.textlength(c, font=F_EYEBROW) + 3.8 for c in eyebrow.upper())
        tracked(d, (CX - we / 2, y), eyebrow.upper(), F_EYEBROW, rgba(GOLD, a * 0.95), 3.8)
        d.text((CX, y + 32), head, font=F_HEAD, fill=rgba(IVORY, a), anchor="ma")
        d.text((CX, y + 132), sub, font=F_SUB, fill=rgba(IVORY, a * 0.60), anchor="ma")

    # --- sign off ---------------------------------------------------------
    sa = ease_out(seg(t, BEAT[5][0] + 0.55, BEAT[5][0] + 1.5))
    if sa > 0.01:
        my, k = 300, 2.6            # the mark, at the deck's own proportions
        px, py = CX - 32 * k, my - 32 * k
        P = lambda x, y: (px + x * k, py + y * k)
        d.ellipse([P(0, 0), P(64, 64)], fill=(16, 26, 49, int(255 * sa)))
        d.polygon([P(27.5, 13), P(31, 13), P(26, 42), P(21, 42)], fill=rgba(GOLD, sa))
        d.polygon([P(33, 13), P(36.5, 13), P(43, 42), P(38, 42)], fill=rgba(GOLD, sa))
        d.ellipse([P(17.5, 43.8), P(46.5, 50.2)], fill=rgba(GOLD, sa))
        d.text((CX, my + 128), "We build the stage.", font=F_SIGN,
               fill=rgba(IVORY, sa), anchor="ma")
        d.text((CX, my + 208), "You steal the show.", font=F_SIGN,
               fill=rgba(GOLD, sa), anchor="ma")
        wm = "OWN YOUR STAGE STUDIO"
        ww = sum(d.textlength(c, font=F_MARK) + 4.6 for c in wm)
        tracked(d, (CX - ww / 2, my + 320), wm, F_MARK, rgba(ASH, sa * 0.66), 4.6)

    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    fade = min(ease_io(seg(t, 0, 0.7)), 1 - ease_io(seg(t, DUR - 0.8, DUR)))
    if fade < 0.999:
        img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, clamp(fade))
    return img


def main(out):
    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "24",
         "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart",
         "-g", str(FPS * 2), out],
        stdin=subprocess.PIPE)
    for n in range(NFRAMES):
        ff.stdin.write(render(n / FPS).tobytes())
        if n % 90 == 0:
            print(f"  {n}/{NFRAMES}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("done", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "oyss-film.mp4")
