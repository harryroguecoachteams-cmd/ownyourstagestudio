#!/usr/bin/env python3
"""
Feedback 11 imagery.

  note 3  the two About page pictures ("not liking these two images at all"):
          a man lit by a laptop in the dark and a man alone in a column of light.
          Both read as night, alone, unconnected to the words beside them.
          The captions stay; the pictures now show what they say, warmly.

    python _art/round15.py [names...] [--force]
    python _art/round15.py finish
"""
import sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from azure_art import azure_key, sess, generate, OUT  # noqa: E402
from round12 import HOUSE  # noqa: E402
from round12_finish import cover  # noqa: E402
from PIL import Image, ImageOps

GEN = [
    # caption: "Somebody on the other end of it, watching. The whole engagement is
    # built backwards from this: what has to be true for a stranger to give an
    # expert ninety minutes."
    ("about-watching", "1536x1024", "high", HOUSE +
     "A woman in her forties with dark brown skin and natural hair pulled back, in a soft "
     "cream sweater, sits at her kitchen table in the early evening watching a live expert "
     "panel on an open laptop. The laptop is seen from behind and the side, its screen "
     "facing away from the camera so nothing on it is visible. She leans in slightly, "
     "clearly absorbed and nodding along, a small appreciative smile, a pen resting beside "
     "an open notebook and a cup of tea. Warm lamp light on her face, a warm home interior "
     "softly out of focus behind her, one small red accent. Seen three-quarter from the "
     "front, her face sharp and well lit."),

    # caption: "And the person it exists for: already good at the work, already
    # respected inside a small circle, and unknown outside it."
    ("about-expert", "1024x1536", "high", HOUSE +
     "Three-quarter length portrait of an accomplished man in his late fifties, a senior "
     "consultant, standing in his own warm, book-lined office in the late afternoon. "
     "Silver hair neatly cut, light olive skin, a navy blazer over an open-collared white "
     "shirt, no tie. He looks straight into the camera with a calm, assured, friendly "
     "smile, shoulders relaxed, arms loosely at his sides. Warm window light from the side, "
     "shelves of books and framed pieces softly out of focus behind him, one small red "
     "accent object on a shelf. 85mm lens, sharp on the eyes, real skin texture."),
]

MEDIA = pathlib.Path(__file__).parent.parent / "assets" / "media"
FINISH = [("about-watching", (1400, 788)), ("about-expert", (900, 1350))]


def finish():
    for name, size in FINISH:
        im = ImageOps.exif_transpose(Image.open(OUT / f"{name}.png")).convert("RGB")
        im = cover(im, size)
        out = MEDIA / f"{name}.jpg"
        im.save(out, "JPEG", quality=84, optimize=True, progressive=True)
        print("  wrote", out.name, im.size, out.stat().st_size // 1024, "KB")


def main():
    if "finish" in sys.argv:
        return finish()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    key, s = azure_key(), sess()
    for name, size, quality, prompt in GEN:
        if args and not any(name.startswith(a) for a in args): continue
        out = OUT / (name + ".png")
        if out.exists() and not force: print("  have  %s" % out.name); continue
        t0 = time.time(); print("  gen   %-18s" % name, flush=True)
        ok = generate(key, s, prompt, out, size, quality)
        print("    %s  %.0fs" % ("ok" if ok else "FAILED", time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
