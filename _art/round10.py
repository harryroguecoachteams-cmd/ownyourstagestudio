#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Round 10 commission: feedback 5.0, notes 3 and 7.

    note 3  "These two images are not looking good can you change it"
            (panel-c and panel-d, the two frames boxed together on the rig)
    note 7  "Both the images are looking same there is not clear distinction
            in between them. It is quite confusing for people both on desktop
            and mobile too"   (the Experience page pair)

WHY THOSE TWO RIG FRAMES STOOD OUT. Round 9 fixed six identical frames by
making all six different, and overshot on these two. panel-c came back with a
broad open laugh against the brightest background in the grid, and panel-d came
back near black and stern. Side by side they read as one person having a great
time next to one person having a terrible one, which is what the box in the
screenshot is around. Both move back toward the middle: same rooms, same
lighting idea, calmer expressions and a matched exposure.

WHY THE PAIR LOOKED LIKE ONE PICTURE. Both were a person shot from behind,
in silhouette, facing a screen full of faces. The subjects are different, the
compositions were not. The operator shot is re-framed from the side at close
range, so the two pictures no longer share a shape.

    python _art/round10.py            everything not yet on disk
    python _art/round10.py --force    regenerate even if the file exists
"""
import sys, time, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from azure_art import azure_key, sess, generate, OUT  # noqa: E402
from round9 import HOUSE, RIG  # noqa: E402

SHOTS = [
    # ---- NOTE 3: the two frames that stood out ----------------------------
    ("panel-c", "1024x1024", "high", RIG +
     "A South Asian woman in her thirties with dark hair loosely tied back and "
     "a few strands escaping, in a plain tailored shirt, listening with a small "
     "closed-mouth smile, head tilted very slightly. Not laughing. Behind her a "
     "dark room with a doorway and a plant far out of focus, dim, no window and "
     "no daylight. One soft warm key from camera left and deep shadow on the "
     "other side of her face, exposed so the room behind her stays dark."),

    ("panel-d", "1024x1024", "high", RIG +
     "An East Asian man in his fifties, greying, wearing glasses and a dark "
     "knitted jumper, listening with an easy open expression and the beginning "
     "of a nod, relaxed rather than stern. Behind him a dark warm room with a "
     "wall and a picture frame far out of focus. A clear warm key from camera "
     "right so his eyes and the top of his face are properly lit, not a dark "
     "silhouette."),

    # ---- NOTE 7: the operator, re-framed ---------------------------------
    # The old one was over the shoulder of a silhouetted figure facing a wall
    # of monitors, which is the same composition as the picture beside it.
    ("operator-side", "1536x1024", "high",
     "A close side-on portrait of a producer in her forties at a darkened "
     "production desk, seen in profile from her left at arm's length, her face "
     "and the front of her shoulder lit by the cool glow of screens that are "
     "entirely out of frame. She is concentrating, eyes tracking something off "
     "camera, lips slightly parted. Behind her the room falls away to complete "
     "black with one small warm lamp far out of focus. Nothing else in the "
     "picture: no monitors visible, no desk clutter, no keyboard, no hands. "
     "Tight, quiet, shallow focus, film grain, documentary."),
]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    key, s = azure_key(), sess()
    todo = [x for x in SHOTS if not args or any(x[0].startswith(a) for a in args)]
    for name, size, quality, prompt in todo:
        out = OUT / (name + ".png")
        if out.exists() and not force:
            print("  have  %s" % name)
            continue
        t0 = time.time()
        print("  gen   %-20s %s %s" % (name, size, quality), flush=True)
        ok = generate(key, s, HOUSE + prompt, out, size, quality)
        print("    %s  %.0fs  %.0f KB" % ("ok" if ok else "FAILED", time.time() - t0,
                                          out.stat().st_size / 1024 if ok else 0),
              flush=True)


if __name__ == "__main__":
    main()
