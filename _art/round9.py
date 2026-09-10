#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Round 9 commission: feedback 4.0, notes 2, 5, 9 and 10.

    note 2   "Recreate all these images and make it look more humanize"
             (the six frames of the panel rig on the home page)
    note 5   "It is not going to be a real round table conference, it is
             going to be virtual"   (the Experience page pair, left picture)
    note 9   "The image is not going with the page"   (the FAQ hero)
    note 10  "change the image to a more humanize person"   (the Apply hero,
             which is the same file as the rig's host frame, so note 2 and
             note 10 are answered by the same regeneration)

WHAT MADE THE RIG FACES READ AS GENERATED. Not the framing: a video call frame
really is eyes to camera, head and shoulders, centered. It was everything
around that. The six were lit identically, retouched to the same flat skin,
photographed against the same black void with nothing behind them, and all six
were sitting still with the same neutral expression. Six people cannot be that
alike. A real six-up grid is six different rooms, six different cameras, six
people at slightly different distances, and at any given moment one of them is
mid sentence.

So these keep the broadcast framing and change the six things that were the
same in all six: a real room behind each one instead of a void, a different
practical light in each, unretouched skin with visible texture, a different
moment caught in each, slightly different distances, and no two the same age
or coloring.

    python _art/round9.py            everything not yet on disk
    python _art/round9.py panel      just the ids starting "panel"
    python _art/round9.py --force    regenerate even if the file exists
"""
import sys, time, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from azure_art import azure_key, sess, generate, OUT  # noqa: E402

# Same house rules as round 8. Writing and hands are framed out rather than
# prompted away, and the palette is the September brand sheet.
HOUSE = (
    "Cinematic editorial photograph, shot on film. Deep charcoal near-black "
    "environment, warm key light, soft falloff into darkness, fine grain and "
    "shallow depth of field. Real skin tones, unretouched, visible skin "
    "texture and fine lines, no makeup sheen, no beauty retouching. "
    "Absolutely no writing anywhere in the frame: no handwriting, no print, no "
    "signage, no labels, no numbers, no letters, no logos, no watermark, no "
    "captions, no readable user interface. "
    "No stage curtains, no microphone stands, no podium, no lectern, no light "
    "fixtures visible in shot, no audience, no confetti. "
)

# Every rig frame inherits this. It is the part that was identical across all
# six and had to stop being identical.
RIG = (
    "Framed as a professional video call at broadcast quality: head and "
    "shoulders, centered, generous headroom, sharp and evenly exposed on the "
    "face, seen straight on at eye level as a good webcam would. Behind them "
    "is a real room, softly out of focus, dark and warm, with depth to it "
    "rather than a black backdrop. Documentary, caught rather than posed, no "
    "screen artefacts, no interface, nothing overlaid on the picture. "
)

SHOTS = [
    # ---- NOTE 2 and NOTE 10: the six frames of the rig ---------------------
    # The host frame is wide, because the tile it sits in is 16:9 and twice the
    # size of the others. It is also the Apply page hero, which is the picture
    # note 10 circled.
    ("host-onstage", "1536x1024", "high", RIG +
     "A woman in her late forties with dark hair to her shoulders, in a dark "
     "tailored blazer, speaking directly to the camera mid sentence with warmth "
     "and authority, one eyebrow slightly raised, head turned a few degrees off "
     "square. Positioned in the center of a wide frame with generous space "
     "either side. Behind her a dark warm room with a doorway and a lamp far out "
     "of focus. A single warm key from camera left and a weak cool fill from a "
     "screen just off camera right."),

    ("panel-a", "1024x1024", "high", RIG +
     "A woman in her late fifties with short silver-grey hair and reading "
     "glasses pushed up on her head, in a dark blazer over a soft collar, "
     "listening and just beginning to smile at something said off camera. Sat a "
     "little further back than most people sit. Behind her a dark room with a "
     "shelf of books far out of focus. Warm key from camera left, cooler "
     "daylight from a window behind her."),

    ("panel-b", "1024x1024", "high", RIG +
     # "brow furrowed in thought" came back as a scowl, which is not what a
     # panelist looks like while another one is talking. Same man, warmer beat.
     "A Black man in his forties, close-cropped hair, a slightly rumpled open "
     "collar shirt under a soft jacket, mid sentence and mid gesture of the "
     "head, relaxed and engaged, the beginning of a smile at the corner of his "
     "mouth. Sat close to the camera. Behind him a dark warm room with a "
     "doorway out of focus. One warm practical lamp from camera right, low and "
     "close."),

    ("panel-c", "1024x1024", "high", RIG +
     "A South Asian woman in her thirties with dark hair loosely tied back and "
     "a few strands escaping, in a plain tailored shirt, laughing gently at "
     "something off camera with her eyes creased. Behind her a dark room with a "
     "plant and a window far out of focus. Soft warm key from camera left, "
     "slightly uneven, the way a room lamp lights a face."),

    ("panel-d", "1024x1024", "high", RIG +
     "An East Asian man in his fifties, greying, wearing glasses and a dark "
     "knitted jumper, listening intently with his chin resting slightly forward, "
     "not smiling, entirely absorbed. Sat a little off center. Behind him a dark "
     "warm room with a wall and a picture frame far out of focus. Warm key from "
     "camera right, a screen's cool glow catching one side of his glasses."),

    ("panel-e", "1024x1024", "high", RIG +
     "A white woman in her late twenties with shoulder length blonde hair "
     "slightly tucked behind one ear, in a dark blouse, mid nod and about to "
     "speak, mouth just opening. Sat close and a fraction low in frame. Behind "
     "her a dark warm room with a corner and a soft lamp out of focus. Warm key "
     "from camera left and a little bounce from a desk below."),

    # ---- NOTE 5: the panel is virtual, not a room -------------------------
    # "It is not going to be a real round table conference, it is going to be
    # virtual." The old picture was four people in armchairs in one room, which
    # is an in-person panel and is the wrong product.
    ("panel-virtual", "1536x1024", "high",
     "Over the shoulder of a woman in a dark blazer seated at a desk in a dark "
     "warm room, seen from behind and to one side so she is a soft silhouette in "
     "the foreground. In front of her a large screen shows five other "
     "professionals of different ages and ethnicities in separate video call "
     "tiles, each one lit warmly in their own room, one of them talking and the "
     "others listening. The screen glow is the main light in the picture. "
     "Shallow focus, the screen soft and the tiles readable as people but not "
     "sharp. No text and no interface anywhere on the screen. Documentary, "
     "unposed, film grain."),

    # ---- NOTE 9: the FAQ hero ---------------------------------------------
    # "The image is not going with the page." The old one was a man alone at a
    # desk at night, which reads brooding and lonely against a bright premium
    # studio brand. Same beat, somebody weighing it up, but in this brand's
    # light and in this brand's world.
    ("reading-it", "1536x1024", "high",
     "A woman in her fifties in a dark jacket sitting back from a laptop at a "
     "warm wooden table, reading something on it carefully and taking her time, "
     "one hand resting still on the table. Late afternoon light from a window "
     "off to the left, the rest of the room falling away into warm shadow. Seen "
     "in a wide mid shot from slightly to the side with dark empty space beside "
     "her. Calm and unhurried, not worried. The laptop screen is soft and "
     "completely unreadable. Documentary, unposed, film grain."),
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
