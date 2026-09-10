#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Round 8 commission: the person in the spotlight, and the interior page shots.

Feedback 3.0, note 3: "I absolutely dislike the artificial person stepping into
the spotlight. Any chance your team could make him/her more natural and human
looking?"

The figure in the two generated clips is not disliked because it is small. It is
disliked because it MATERIALISES out of empty air in the beam, and because at
that distance the model rendered no shoulders, no face and legs a head too long.
Neither is fixable by prompting the same shot again: both failures come from
asking a generator for a full-length human at forty feet.

So the shot changes rather than the prompt. The figure is framed at a distance a
photographer would actually stand at for a portrait in a beam - knee up, three
quarter turn, face catching the edge of the key - which is the framing this
model renders convincingly, and the framing the site already proves it can (the
six panel portraits on the home page are the same lens).

    python _art/round8.py               everything not yet on disk
    python _art/round8.py spot          just the ids starting "spot"
    python _art/round8.py --force       regenerate even if the file exists

Raw masters land in _art/raw/ (gitignored). Grade and place them with
_art/process.py.
"""
import sys, time, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from azure_art import azure_key, sess, generate, OUT  # noqa: E402

# The September brand sheet, not the deck's navy. Every prompt inherits it.
# "Deep charcoal" reads to the model as a neutral near-black, which is what
# #1F1E1D is; "navy" was pulling the whole set blue and process.py was
# correcting it afterwards.
HOUSE = (
    "Cinematic editorial photograph, shot on film. Deep charcoal near-black "
    "environment, one warm key light, soft falloff into darkness, clean "
    "negative space, fine grain and shallow depth of field. Premium production "
    "still with the restraint of a Financial Times or Monocle portrait. Color "
    "limited to warm amber light, deep charcoal shadow and real skin tones. "
    # Writing and hands are the two things this model fails at unmistakably,
    # so both are framed out rather than prompted away.
    "Absolutely no writing anywhere in the frame: no handwriting, no print, no "
    "signage, no labels, no numbers, no letters, no logos, no watermark, no "
    "captions, no user interface. "
    "No stage curtains, no microphone stands, no podium, no lectern, no light "
    "fixtures visible in shot, no audience, no confetti. "
)

SHOTS = [
    # ---- 01 THE HERO FIGURE -------------------------------------------------
    # Replaces the dissolving figure in the generated clip. Vertical, because
    # the hero media panel is 0.77:1 and the beam is the composition.
    #
    # Everything here is aimed at the uncanny: a real age, real weight on one
    # leg, unretouched skin, a face that catches the edge of the key rather than
    # the middle of it, and a body big enough in frame that anatomy has to be
    # right rather than guessed.
    ("spot-figure", "1024x1536", "high",
     "A woman in her late forties in a well cut charcoal trouser suit standing "
     "still inside a hard column of warm light on a dark studio floor, "
     "photographed from the front and slightly below, framed from the knees up "
     "so she fills the middle half of the tall frame. Weight settled on one leg, "
     "shoulders square, chin level, looking just past the camera, not smiling. "
     "The beam comes steeply from high above and slightly behind, so it rims her "
     "hair and shoulders and only the top planes of her face catch it, and her "
     "eyes stay in soft shadow. Fine theatrical haze makes the column of light "
     "visible in the air around her. Everything outside the beam is deep "
     "charcoal black. Unretouched skin with visible texture and fine lines, "
     "natural hair, no makeup sheen. Shot on a 50mm lens on film, slight grain. "
     "Documentary theater photography, caught rather than posed."),

    # The same beat with a man, so the site is not casting one gender for
    # "the expert". The two alternate on the home page and the About page.
    ("spot-figure-alt", "1024x1536", "high",
     "A man in his fifties, greying at the temples, in a dark open collar shirt "
     "and unstructured jacket, standing still inside a hard column of warm light "
     "on a dark studio floor, photographed from the front and slightly below, "
     "framed from the knees up so he fills the middle half of the tall frame. "
     "Weight settled, hands loose at his sides, head turned a few degrees off "
     "camera. The beam comes steeply from high above and slightly behind, "
     "rimming his hair and shoulders, only the top planes of his face catching "
     "it. Fine theatrical haze makes the column visible in the air. Everything "
     "outside the beam is deep charcoal black. Unretouched skin with visible "
     "texture, no makeup sheen. Shot on a 50mm lens on film, slight grain. "
     "Documentary theater photography, caught rather than posed."),

    # ---- 02 THE ABOUT HERO --------------------------------------------------
    # room-figure.jpg has the same dissolving-figure problem at an even smaller
    # scale. Same room, same light, but the person is now near enough to read.
    ("room-figure-real", "1536x1024", "high",
     "A vast dark room in near-black, a single broad shaft of warm light "
     "entering from high on the right and landing as a soft pool on a dark "
     "textured floor. A woman in her fifties in a dark suit stands at the near "
     "edge of that pool, three quarters of the way to the right of the frame, "
     "photographed from the front at about twenty feet so she is roughly a third "
     "of the frame height and her face and posture read clearly. She is turned "
     "slightly away, still, looking up into the light. Fine haze in the beam. "
     "The entire left third of the frame is dark and empty. Architectural, wide, "
     "cinematic, nobody else present. Unretouched, film grain."),

    # ---- 03 INTERIOR PAGE SHOTS --------------------------------------------
    # The Experience, Panelists and FAQ heroes are currently three versions of
    # the same picture: a group of people in a dark room in conversation. They
    # are the reason the interior pages read as one template. Each page now gets
    # the shot that belongs to its own subject.
    #
    # The Experience page sells three months of production work, so the shot is
    # the work, not the event.
    # Hands are framed out, not prompted away. The first version put both of
    # his in the middle of the frame gesturing and the generator fused the
    # fingers on one of them, which is the single most recognizable tell there
    # is. Shoulders up puts them below the bottom edge.
    ("prep-session", "1536x1024", "high",
     "Two people talking across a dark table in a low lit room at night, seen "
     "from table height so both are framed from the shoulders up and their "
     "hands are below the bottom edge of the picture, out of shot. One "
     "listening, one mid sentence. Warm key from a small source off to one "
     "side, everything beyond them falling to charcoal black. Late, quiet, "
     "working. Documentary, unposed, shallow focus, no screens, no hands and "
     "no arms visible anywhere in the frame."),

    # The Panelist page sells ten minutes on someone else's stage, so the shot
    # is the moment before you go on.
    ("green-room", "1536x1024", "high",
     "A woman in her forties sitting alone on a dark bench in a corridor "
     "outside a room, waiting, elbows on knees, looking down and composing "
     "herself. A single warm light above her, the corridor falling away into "
     "charcoal black in both directions. Seen from a distance down the corridor. "
     "Still, quiet, a moment before something. Documentary, unposed, film grain, "
     "no doors marked, nothing written anywhere."),

    # The FAQ page is where somebody decides. The shot is a decision, not a
    # product: one person, late, weighing something up.
    ("deciding", "1536x1024", "high",
     "A man in his forties alone in a dark room at night, sitting back from a "
     "desk with his hands still, thinking, lit only by a warm lamp just out of "
     "frame to his left. The rest of the room is charcoal black. Seen in a wide "
     "mid shot from the side with a lot of empty dark space around him. "
     "Documentary, unposed, shallow focus, nothing readable on the desk."),

    # The Assessment page hero is currently a young man in profile which reads
    # as a stock portrait. The subject of that page is a ladder of visibility,
    # so the shot is a room seen from the back of it.
    # The first version put a grand piano on the stage, which is a concert
    # hall and the wrong association entirely. The stage is named as bare.
    ("back-of-room", "1536x1024", "high",
     "The back of a dark auditorium looking toward a distant lit stage, rows "
     "of empty seats in the foreground silhouetted almost to black, one warm "
     "pool of light far away at the front falling on a completely bare stage "
     "floor. Nobody in the seats. No piano, no instruments, no furniture and "
     "nothing at all standing on the stage. Deep charcoal darkness, fine haze, "
     "the light small and distant. Architectural, still, shot on film with "
     "visible grain."),

    # The Spotlight Call page. A conversation between two people, not a desk
    # still: the current shot is a notebook and pen, which is every consultancy
    # site on earth.
    ("two-talking", "1536x1024", "high",
     "Two women in a dark room in the middle of a conversation, one listening "
     "hard, the other speaking, seen in profile from one side at close range "
     "and framed tightly from the shoulders up so no hands and no arms appear "
     "anywhere in the picture. One warm key from above and between them, the "
     "room behind falling to charcoal black. Documentary, unposed, shallow "
     "focus, film grain, caught mid sentence."),
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
