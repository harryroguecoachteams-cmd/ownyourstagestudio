#!/usr/bin/env python3
"""
Feedback 9.0 imagery.

  note 2  the home essay portrait is replaced (a different expert)
  note 4  a picture for every service on the services page and the home
          "what we produce" cards
  note 6  the Strategy Session hero depicts a call, with Annette on it

    python _art/round14.py [names...] [--force]
"""
import sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from azure_art import azure_key, sess, generate, OUT  # noqa: E402
from round12 import edit, HOUSE  # noqa: E402

GEN = [
    ("expert-ready2", "1024x1536", "high", HOUSE +
     "Waist-up portrait of an accomplished woman in her mid fifties, a consultant and "
     "author, standing in a warm modern studio just before she goes on. Shoulder-length "
     "softly waved chestnut hair with a few silver strands, light skin, small pearl "
     "earrings, a tailored charcoal blazer over a soft blush silk blouse. She looks "
     "straight into the camera with a warm, assured smile, chin level. Arms relaxed and "
     "cropped out at the waist. Behind her the studio falls away into warm charcoal with "
     "the soft golden bloom of a stage light high behind her left shoulder, a gentle rim "
     "of light on her hair. 85mm lens, sharp on the eyes, real unretouched skin texture."),

    ("svc-webinar", "1536x1024", "high", HOUSE +
     "A woman expert in her fifties teaching a live online masterclass from a small, "
     "beautifully lit home studio: she sits at a clean desk facing a camera on a tripod "
     "with a soft key light, gesturing gently mid-sentence, warm and engaged. We see her "
     "three-quarter from the side, the camera and the light in the foreground softly out "
     "of focus. Warm charcoal walls, one small red accent object on a shelf."),

    ("svc-interview", "1536x1024", "high", HOUSE +
     "Two professionals in their forties and fifties seated in two armchairs angled toward "
     "each other on a dark, intimate interview set, a man and a woman, mid-conversation, "
     "she is the host listening with a warm smile while he answers. Two cinema cameras on "
     "tripods at the edges of the frame, softly out of focus. A warm key light and a "
     "charcoal backdrop."),

    ("svc-podcast", "1536x1024", "high", HOUSE +
     "A podcast-style conversation in a warm, dark studio: two people in their fifties at "
     "a round wooden table, each with a broadcast microphone on a boom arm and headphones "
     "around the neck, laughing together mid-conversation. Shallow depth of field, the "
     "nearer microphone sharp in the foreground."),

    ("svc-prep", "1536x1024", "high", HOUSE +
     "A speaker rehearsal: an expert woman in her fifties stands in a warmly lit studio "
     "practicing her talk toward a camera, while a coach in the foreground, seen from "
     "behind and out of focus, watches and listens. Soft stage light, charcoal walls, "
     "calm and focused, confident posture."),

    ("svc-series", "1536x1024", "high", HOUSE +
     "A produced studio stage for a recurring expert show: two lounge chairs and a low "
     "table on a small raised platform, a warm pool of light on the stage, a thin red "
     "light line along the floor edge, broadcast cameras and a lighting rig silhouetted "
     "in the dark around it, empty and ready for the next episode. Wide shot."),
]

EDITS = [
    ("annette-call", "1536x1024", "high",
     ["_art/raw/annette-ref-a.png", "_art/raw/annette-ref-b.png", "_art/raw/annette-close.png"],
     "Create a photograph of the woman shown in these images (the same real person), keeping "
     "her exact face, her long straight black hair and her olive skin tone so she is "
     "immediately recognizable. She sits at a clean wooden desk in a warmly lit home office "
     "in the evening, on a video call: an open laptop in front of her, its screen turned "
     "away from the camera so nothing on it is visible, and she is smiling warmly toward "
     "the laptop mid-conversation, one hand relaxed on the desk. She wears the black "
     "tailored blazer over a dark top. A small notebook beside the laptop, a warm desk lamp "
     "glow, charcoal walls, one small red accent. Seen three-quarter from the side, her "
     "face clearly visible and well lit. " + HOUSE),
]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    key, s = azure_key(), sess()
    want = lambda n: not args or any(n.startswith(a) for a in args)
    for name, size, quality, prompt in GEN:
        if not want(name): continue
        out = OUT / (name + ".png")
        if out.exists() and not force: print("  have  %s" % out.name); continue
        t0 = time.time(); print("  gen   %-18s" % name, flush=True)
        ok = generate(key, s, prompt, out, size, quality)
        print("    %s  %.0fs" % ("ok" if ok else "FAILED", time.time() - t0), flush=True)
    for name, size, quality, images, prompt in EDITS:
        if not want(name): continue
        out = OUT / (name + ".png")
        if out.exists() and not force: print("  have  %s" % out.name); continue
        t0 = time.time(); print("  edit  %-18s" % name, flush=True)
        ok = edit(key, s, prompt, images, out, size, quality)
        print("    %s  %.0fs" % ("ok" if ok else "FAILED", time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
