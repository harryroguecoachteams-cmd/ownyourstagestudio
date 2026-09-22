#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Round 12 commission: feedback 7.0 (Google Doc, 23 Sep 2026).

    note 2  home, "Most experts are not short of expertise": the portrait
            "creates a feeling of sorrow, sadness which she wants to avoid"
    note 4  "Somewhere on the site you can use this picture, Annette shared
            it... do not blindly add this. Generate a high quality one"
            (a phone photo of a laptop screen: a chrome microphone, warm
            orange stage light, violet haze)
    note 5  the footer mockup: red silk sweeping across a warm white ground
    note 7  assessment hero, the auditorium: "looking quite dull", brighten
            it, and put a figure under the light "in a shadow style"
    note 8  panelists hero: "the lady is giving a feeling of sadness"
    note 9  about hero: "swap the current lady face with Annette's face"

WHY TWO OF THE PICTURES READ AS SAD. Both were made to the old house prompt,
which asked for "one warm key, hard falloff into darkness" and for a subject
"caught mid thought, not smiling". Applied to a lone woman that produces a
chin on a hand and a woman sitting with her head down in an empty corridor:
technically on brief, emotionally a person having a bad day. The brief for a
visibility brand is the moment AFTER the decision, so the new house prompt
keeps the warm key and the dark ground but asks for the expression and the
exposure of someone who is ready: an open face, lifted shadows, eyes up.

    python _art/round12.py            everything not yet on disk
    python _art/round12.py mic        just the ones whose id starts "mic"
    python _art/round12.py --force    regenerate even if the file exists
"""
import io, sys, time, base64, pathlib
import requests

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from azure_art import azure_key, sess, generate, OUT  # noqa: E402

ROOT = pathlib.Path(__file__).parent.parent
PHOTOS = ROOT.parent / "_annette_photos"
EDIT_ENDPOINT = ("https://sai-mo2tz038-swedencentral.cognitiveservices.azure.com/openai/"
                 "deployments/gpt-image-2/images/edits?api-version=2025-04-01-preview")

# The new house prompt. Same production values as round 5 (one warm key, a
# dark charcoal ground, grain, shallow focus) with the mood turned the other
# way, and the brand's own colors named: charcoal, warm neutral, one accent of
# signature red. Writing and hands stay framed OUT, not prompted away.
HOUSE = (
    "Cinematic editorial photograph for a premium visibility and speaking "
    "studio. Warm charcoal and soft warm-neutral tones with one small accent of "
    "deep signature red, warm golden key light, lifted shadows, subtle film "
    "grain, shallow depth of field. The mood is confident, warm and optimistic: "
    "a person who has decided to be seen. Open, engaged expression, eyes bright "
    "and up, relaxed shoulders. Nothing melancholy, nothing lonely, no bowed "
    "head, no hand on the chin. "
    "Absolutely no writing anywhere in the frame: no print, no signage, no "
    "labels, no numbers, no letters, no logos, no watermark, no user interface. "
    "Any screen is turned away from the camera or too far out of focus to read. "
    "Hands are out of frame or relaxed and still. "
)

GEN = [
    # ---- NOTE 2: the home essay portrait ---------------------------------
    # 860 x 1290 on the page, portrait, beside "Most experts are not short of
    # expertise". The paragraph is about someone good at the work and known
    # inside their circle, so the picture is that person, in their element.
    ("expert-ready", "1024x1536", "high", HOUSE +
     "Waist-up portrait of an accomplished Black woman in her mid fifties, a "
     "consultant and author, standing in a warm modern studio just before she "
     "goes on. Short natural hair with silver at the temples, small gold "
     "earrings, a tailored charcoal blazer over a soft blush silk blouse. She "
     "is looking straight into the camera with a warm, assured, closed-mouth "
     "smile, chin level. Arms relaxed at her sides and cropped out of frame at "
     "the waist. Behind her the studio falls away into warm charcoal with the "
     "soft golden bloom of a stage light high behind her left shoulder, "
     "creating a gentle rim of light on her hair. Shot on an 85mm lens, sharp "
     "on the eyes, skin texture real and unretouched."),

    # ---- NOTE 8: the panelist hero ----------------------------------------
    # Shown as the right-hand panel of a split hero, so the subject sits right
    # of center and the left third can fall into shadow under the fade.
    ("panelist-live", "1536x1024", "high", HOUSE +
     "A woman in her late forties, Latina, dark hair in a low loose bun, in a "
     "cream blouse and a deep red jacket, seated at a clean desk in a warm, "
     "tasteful home studio, turned three quarters toward a laptop whose screen "
     "faces away from the camera at the left of the frame. She is mid-laugh "
     "in a live panel conversation, genuinely delighted, eyes bright, lit by a "
     "soft warm key from the laptop side and the golden glow of a lamp far "
     "behind her. Behind her, softly out of focus, warm shelves with plants "
     "and a few books without visible titles. She sits right of center; the "
     "left third of the frame is dark and quiet. Hands out of frame below the "
     "desk edge. Photographed from slightly below eye level, 50mm."),

    # ---- NOTE 4: the microphone Annette loves -----------------------------
    # Her reference is a phone photo of a laptop screen: a chrome cage
    # microphone in the left third, a warm orange stage light blooming behind
    # its head, a white light top right, violet and blue haze and a blurred
    # truss on the right. Rebuilt at full resolution in the same composition,
    # with the violet pulled toward the brand's red so it sits on the site.
    ("mic-stage", "1536x1024", "high",
     "Cinematic close-up photograph of a classic vintage chrome cage "
     "microphone, 1950s broadcast style, on a slim stand in the left third of "
     "the frame, sharp and gleaming, catching a warm orange rim light along "
     "its grille. Behind it a dark concert stage dissolves into large soft "
     "circular bokeh: a big warm orange-gold stage light blooming just above "
     "and behind the microphone head, a bright white light at the top right, "
     "and on the right side a deep crimson and magenta haze with a blurred "
     "lighting truss and floating dust particles. Very shallow depth of "
     "field, 85mm f/1.4, rich contrast, deep charcoal blacks. No people in "
     "focus, no audience, no text, no logos, no watermark."),

    # ---- NOTE 5: the footer silk ------------------------------------------
    # The mockup is a warm white banner with red chiffon sweeping up from the
    # lower left. Generated as a plate rather than drawn so it has the depth
    # of real fabric; the type and the links stay live over it.
    ("silk-footer", "1536x1024", "high",
     "Minimal luxury abstract background: layered ribbons of translucent red "
     "silk chiffon flowing in smooth waves from the lower left corner, rising "
     "gently across the lower half of the frame and fading out toward the "
     "right edge. The fabric runs from deep crimson in the folds to soft blush "
     "pink where it thins, with a delicate sheen. The entire upper half and "
     "the upper right are a clean, soft warm white with the faintest blush "
     "gradient, completely empty. Soft diffused studio light, no shadows on "
     "the ground, no objects, no text, no logos, no watermark."),

    # The first plate is a lower-left sweep: right for a square, wrong for a
    # footer 2.6 times wider than it is tall, where it filled one corner and
    # left the middle empty. This one is composed for the banner: fabric
    # across the full width, low, with the top forty percent left clear for
    # the lockup and the words.
    ("silk-banner", "1536x1024", "high",
     "Minimal luxury abstract background: a wide flowing band of translucent "
     "red silk chiffon crossing the ENTIRE width of the frame in one long "
     "gentle wave. It enters at the left edge at about sixty percent of the "
     "height, rises to a soft crest just right of center at about forty five "
     "percent of the height, and sweeps down to leave the right edge near the "
     "bottom. Several layered folds, deep crimson where the folds are dense at "
     "the lower left, thinning to soft blush pink toward the right. The top "
     "forty percent of the frame is a clean, soft warm white, completely empty, "
     "and the fabric never rises into it. Soft diffused studio light, a "
     "delicate sheen, no shadows, no objects, no text, no logos, no watermark."),
]

EDITS = [
    # ---- NOTE 7: the auditorium, brightened, with a figure in the pool ----
    ("house-lit", "1536x1024", "high", ["assets/media/house.jpg"],
     "Edit this photograph of an empty auditorium seen from the back. Keep the "
     "same camera position, the same rows of seats, the same stage and the "
     "same composition. Make the whole room noticeably brighter and warmer: "
     "lift the exposure about one and a half stops, reveal the warm wood and "
     "red velvet of the seats and the side walls, and make the pool of light "
     "on the stage a richer, brighter golden white with a visible soft beam "
     "coming down into it through faint haze. Add one person standing in the "
     "center of the pool of light on the stage: a confident woman seen at a "
     "distance, rendered almost entirely as a dark silhouette against the "
     "light, standing tall with her shoulders open and her head up, as if "
     "about to speak. She is small in the frame, in proportion to the "
     "distance. No text, no logos, no audience."),

    # ---- NOTE 9: Annette, in the About hero -------------------------------
    # Image 1 is the current hero, image 2 is Annette. The figure is small in
    # the frame, so likeness is carried by hair, skin tone and build as much
    # as by the face; all three are named.
    ("room-annette", "1536x1024", "high",
     ["_art/raw/room-figure.png", "_art/raw/annette-ref-a.png", "_art/raw/annette-ref-b.png"],
     "Edit the first image. Replace the woman standing in the pool of light "
     "with the woman shown in the second and third images (the same person), keeping her exact face, her long "
     "straight black hair falling past her shoulders, her olive skin tone and "
     "her slim build, so that she is clearly recognizable as the same person. "
     "She stands in the same place and at the same size in the frame, in a "
     "tailored black trouser suit, turned toward the camera with a warm, "
     "confident smile, head up, relaxed and proud. Keep the room, the shaft "
     "of warm light, the pool on the floor, the darkness, the grain and the "
     "composition of the first image exactly as they are. No text, no logos."),
]


def edit(key, s, prompt, images, out, size, quality, tries=3):
    for a in range(tries):
        files = []
        for p in images:
            path = (ROOT / p).resolve()
            mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
            files.append(("image[]", (path.name, open(path, "rb").read(), mime)))
        data = {"prompt": prompt, "n": "1", "size": size, "quality": quality}
        r = s.post(EDIT_ENDPOINT, headers={"api-key": key}, data=data, files=files,
                   timeout=600)
        if r.status_code == 200:
            d = r.json()["data"][0]
            raw = (base64.b64decode(d["b64_json"]) if "b64_json" in d
                   else requests.get(d["url"], timeout=240).content)
            io.open(out, "wb").write(raw)
            return True
        print("    HTTP %s %s" % (r.status_code, r.text[:300]), flush=True)
        time.sleep(10 * (a + 1))
    return False


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    tag = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--tag=")), "")
    OUT.mkdir(parents=True, exist_ok=True)
    key, s = azure_key(), sess()

    def want(name):
        return not args or any(name.startswith(a) for a in args)

    for name, size, quality, prompt in GEN:
        if not want(name):
            continue
        out = OUT / (name + tag + ".png")
        if out.exists() and not force:
            print("  have  %s" % out.name); continue
        t0 = time.time()
        print("  gen   %-20s %s %s" % (out.name, size, quality), flush=True)
        ok = generate(key, s, prompt, out, size, quality)
        print("    %s  %.0fs" % ("ok" if ok else "FAILED", time.time() - t0), flush=True)

    for name, size, quality, images, prompt in EDITS:
        if not want(name):
            continue
        out = OUT / (name + tag + ".png")
        if out.exists() and not force:
            print("  have  %s" % out.name); continue
        t0 = time.time()
        print("  edit  %-20s %s %s" % (out.name, size, quality), flush=True)
        ok = edit(key, s, prompt, images, out, size, quality)
        print("    %s  %.0fs" % ("ok" if ok else "FAILED", time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
