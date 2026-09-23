#!/usr/bin/env python3
"""
Feedback 8.0, note 11: "Change the annette to a close up short image,
currently it is looking very small." The About hero showed her full length
at about a sixth of the frame height. This is the same room and the same
warm shaft of light, framed as a waist-up close-up so her face carries the
panel. Built from her two real photographs, as round 12 was.

    python _art/round13.py [--force] [--tag=_b]
"""
import sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from azure_art import azure_key, sess, OUT  # noqa: E402
from round12 import edit, HOUSE  # noqa: E402

EDITS = [
    ("annette-close", "1024x1536", "high",
     ["_art/raw/annette-ref-a.png", "_art/raw/annette-ref-b.png", "_art/raw/room-annette.png"],
     "Create a close-up portrait photograph of the woman shown in the first and second "
     "images (the same real person). Keep her exact face and features, her long straight "
     "black hair falling past her shoulders, her olive skin tone and her slim build, so she "
     "is immediately recognizable as the same person. Frame her from the waist up, her face "
     "in the upper third of a tall vertical frame, filling most of the frame width, looking "
     "straight into the camera with a warm, confident, natural smile, head up, shoulders "
     "relaxed and slightly turned. She wears the tailored black trouser suit jacket from the "
     "third image over a simple dark top. The setting and light are the third image's: a dark "
     "charcoal stage, a single warm golden shaft of light falling on her from high on the "
     "right, soft falloff into darkness behind her, subtle haze in the beam. Her face is well "
     "lit and clearly visible, with gentle warm fill so no deep shadows cross it. Hands out "
     "of frame. " + HOUSE),
]


def main():
    force = "--force" in sys.argv
    tag = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--tag=")), "")
    key, s = azure_key(), sess()
    for name, size, quality, images, prompt in EDITS:
        out = OUT / (name + tag + ".png")
        if out.exists() and not force:
            print("  have  %s" % out.name); continue
        t0 = time.time()
        print("  edit  %-20s %s %s" % (out.name, size, quality), flush=True)
        ok = edit(key, s, prompt, images, out, size, quality)
        print("    %s  %.0fs" % ("ok" if ok else "FAILED", time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
