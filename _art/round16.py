#!/usr/bin/env python3
"""
Feedback 11 follow-up: the home essay picture. Harsh on the headshot:
"something about this photo is not giving that vibe, something feels missing."
The paragraph is about an expert who is excellent at the work and known only
inside her own circle. A headshot says none of that. These show the work
itself, in the small room where she is already respected.

    python _art/round16.py [names...] [--force]
    python _art/round16.py finish <name>
"""
import sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from azure_art import azure_key, sess, generate, OUT  # noqa: E402
from round12 import HOUSE  # noqa: E402
from round12_finish import cover  # noqa: E402
from PIL import Image, ImageOps

GEN = [
    ("essay-circle", "1024x1024", "high", HOUSE +
     "An accomplished woman consultant in her mid fifties, shoulder-length chestnut hair "
     "with a few silver strands, a charcoal blazer over a soft blush blouse, leads a small "
     "strategy session for four business owners around a wooden table in a warm, "
     "intimate boutique meeting room in the late afternoon. She is mid-sentence, "
     "confident and warm, clearly the expert in the room; the four clients lean in, "
     "listening intently, one smiling and nodding. Notebooks and coffee cups on the table. "
     "Warm window light and a soft practical lamp, charcoal walls, one small red accent. "
     "She is sharp and in the center of the frame, the clients around her slightly softer. "
     "The feeling: she is brilliant at this, and the room knows it."),

    ("essay-client", "1024x1024", "high", HOUSE +
     "An accomplished woman consultant in her mid fifties, shoulder-length chestnut hair "
     "with a few silver strands, a charcoal blazer over a soft blush blouse, sits across "
     "a small table from one client, a man in his forties, in a warm, book-lined private "
     "office. She is explaining something with calm authority and a warm smile; he is "
     "leaning forward, visibly impressed, mid-laugh of recognition. Seen over the "
     "client's shoulder so her face is sharp and fully lit, his softly out of focus. "
     "Warm late afternoon window light, charcoal and warm wood tones, one small red "
     "accent. The feeling: a trusted advisor at her best, in a room of one."),
]

MEDIA = pathlib.Path(__file__).parent.parent / "assets" / "media"


def finish(name):
    im = ImageOps.exif_transpose(Image.open(OUT / f"{name}.png")).convert("RGB")
    im = cover(im, (1000, 1000))
    out = MEDIA / f"{name}.jpg"
    im.save(out, "JPEG", quality=84, optimize=True, progressive=True)
    print("  wrote", out.name, im.size, out.stat().st_size // 1024, "KB")


def main():
    if sys.argv[1:2] == ["finish"]:
        return finish(sys.argv[2])
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
