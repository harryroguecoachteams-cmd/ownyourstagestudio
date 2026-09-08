#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Own Your Stage Studio: commission the deck's shot list with Azure gpt-image-2.

Page 21 of OYSS_Brand_Deck_v3 does not describe a mood, it hands over a
specification and a six item shot list "to commission or license". Nothing on
the site was shot to it. This generates it.

    PEOPLE & PANELS   Confident experts in warm, polished environments.
                      Shoulders up, shallow depth of field, one warm key at 45
                      degrees, eyes to camera. Virtual panels should look like
                      produced media, never a screen grab.
    ENVIRONMENT       Deep navy, soft amber light, clean negative space and
                      subtle texture. One light source, always from above or
                      behind. No props that turn the room into a set.
    ALWAYS AVOID      Curtains, microphones on stands, spotlights as objects,
                      applauding crowds, podiums, confetti, casual screen grabs.

The key is read out of the Azure keys docx so it is never written to disk here.

    python _art/azure_art.py            everything not yet on disk
    python _art/azure_art.py panel      just the ones whose id starts "panel"
    python _art/azure_art.py --force    regenerate even if the file exists
"""
import io, os, re, sys, base64, zipfile, time, pathlib
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

KEYS_DOC = r"E:\atreya\Azure AI keys.docx"
ENDPOINT = ("https://sai-mo2tz038-swedencentral.cognitiveservices.azure.com/openai/"
            "deployments/gpt-image-2/images/generations?api-version=2024-02-01")
OUT = pathlib.Path(__file__).parent / "raw"

# Every prompt inherits this. The deck's "always avoid" list is stated as things
# the frame does NOT contain rather than as negations of a subject, because a
# negative prompt reads to an image model as a mention.
HOUSE = (
    "Cinematic editorial photograph. Deep navy near-black environment, one warm "
    "amber key light, soft falloff into darkness, clean negative space, subtle "
    "grain and shallow depth of field. Premium corporate production still, the "
    "restraint of a Financial Times or Monocle portrait. Colour is limited to "
    "deep navy, warm amber gold and skin tones. No text, no lettering, no logos, "
    "no watermark, no captions, no user interface. No stage curtains, no "
    "microphone stands, no podium, no lectern, no visible lamps or light fixtures "
    "in shot, no audience, no confetti. "
)

SHOTS = [
    # --- 01 host portrait, shoulders up, warm key, navy background -----------
    ("host-portrait", "1024x1536", "high",
     "A confident woman in her late forties, business attire, shoulders up "
     "portrait, three quarter turn with eyes to camera, calm and authoritative "
     "expression. Single warm key light at 45 degrees from camera left, gentle "
     "rim light separating her from a deep navy background that falls off to "
     "black. Headroom at the top of the frame. Sharp on the eyes, background "
     "softly out of focus."),

    # --- 02 panel of four in conversation, mid shot, no podium --------------
    ("panel-conversation", "1536x1024", "high",
     "Four professional adults of different ages and ethnicities seated in a "
     "loose semicircle mid conversation, one speaking with a relaxed hand "
     "gesture and the others listening, mid shot from slightly off centre. A "
     "dark modern room, deep navy walls, one warm amber source from above and "
     "behind them. No table clutter. Editorial documentary feel, natural "
     "posture, nobody looking at the camera."),

    # --- 03 attendee watching intently, screen light on the face ------------
    ("attendee-screenlight", "1536x1024", "low",
     "A man in his thirties watching a screen just off camera, leaning slightly "
     "forward, absorbed. The only light on his face is the cool glow of the "
     "screen, everything behind him falls into deep navy darkness. Close mid "
     "shot from the side, shallow focus, quiet and unposed."),

    # --- 04 empty lit room, negative space for headline overlay -------------
    ("empty-room", "1536x1024", "low",
     "An empty modern room in deep navy near-darkness, a single shaft of warm "
     "amber light entering from high on the right and landing as a soft pool on "
     "a dark textured floor. Fine haze in the air. The entire left two thirds of "
     "the frame is dark and empty with nothing in it. Architectural, still, no "
     "furniture."),

    # --- 05 hands and notebook, shallow depth, warm desk lamp ---------------
    ("hands-notebook", "1536x1024", "low",
     "Close overhead crop of a pair of hands writing in an open notebook on a "
     "dark walnut desk, a warm pool of amber light falling across the page from "
     "the upper left, the rest of the desk falling into deep navy shadow. Very "
     "shallow depth of field, the pen nib sharp and the far edge of the desk "
     "soft. Quiet, expensive, unstyled."),

    # --- 06 texture plate, dark surface with a single light shaft -----------
    ("texture-plate", "1536x1024", "low",
     "Abstract texture plate. A dark charcoal navy plaster wall with a single "
     "narrow shaft of warm amber light raking across it from the upper right, "
     "revealing fine surface grain and falling off into black. No subject, no "
     "objects, no horizon. Flat on, filling the frame."),

    # --- the panel itself: six webcam-framed portraits for the rig ----------
    # The deck's virtual stage frames keep their centre two thirds empty because
    # that is where the person sits. Empty on a website they read as backdrops,
    # which is exactly the note that came back. These are the people who sit in
    # them, shot to the same key so the grid reads as one production.
    ("panel-a", "1024x1024", "high",
     "A woman in her fifties with silver-grey hair, dark blazer, seated at a "
     "desk facing the camera, head and shoulders centred with headroom above, "
     "speaking. Warm amber key light at 45 degrees from camera left, deep navy "
     "background falling to black behind her. Framed as a professional video "
     "call at broadcast quality, sharp, evenly lit, no screen artefacts."),
    ("panel-b", "1024x1024", "high",
     "A Black man in his forties, close-cropped hair, open collar shirt and "
     "jacket, seated facing the camera, head and shoulders centred with headroom "
     "above, listening attentively. Warm amber key light at 45 degrees from "
     "camera right, deep navy background falling to black. Broadcast quality "
     "video call framing, sharp, evenly lit."),
    ("panel-c", "1024x1024", "high",
     "A South Asian woman in her thirties, dark hair tied back, tailored shirt, "
     "seated facing the camera, head and shoulders centred with headroom above, "
     "mid sentence with a slight smile. Warm amber key at 45 degrees from camera "
     "left, deep navy background falling to black. Broadcast quality video call "
     "framing, sharp, evenly lit."),
    ("panel-d", "1024x1024", "high",
     "An East Asian man in his fifties, glasses, dark knit and jacket, seated "
     "facing the camera, head and shoulders centred with headroom above, calm "
     "and considered. Warm amber key at 45 degrees from camera right, deep navy "
     "background falling to black. Broadcast quality video call framing, sharp, "
     "evenly lit."),
    ("panel-e", "1024x1024", "high",
     "A white woman in her late twenties, shoulder length blonde hair, dark "
     "blouse, seated facing the camera, head and shoulders centred with headroom "
     "above, engaged and mid nod. Warm amber key at 45 degrees from camera left, "
     "deep navy background falling to black. Broadcast quality video call "
     "framing, sharp, evenly lit."),
    ("panel-f", "1024x1024", "high",
     "A Latin American man in his forties, short beard, dark shirt, seated "
     "facing the camera, head and shoulders centred with headroom above, "
     "speaking with quiet confidence. Warm amber key at 45 degrees from camera "
     "right, deep navy background falling to black. Broadcast quality video call "
     "framing, sharp, evenly lit."),

    # --- the host, framed for the big host tile ------------------------------
    ("host-onstage", "1536x1024", "high",
     "A woman in her late forties, dark tailored blazer, seated at a desk facing "
     "the camera and speaking directly to it with authority and warmth. Head and "
     "shoulders, positioned in the centre of a wide frame with generous space "
     "either side. One warm amber key light at 45 degrees, deep navy background "
     "receding to black. Broadcast quality, the look of a produced panel event "
     "rather than a webcam."),

    # --- what you keep: the content afterwards -------------------------------
    # First pass put sunsets and mountains on these screens, which is travel
    # photography, not panel footage. The screens have to carry the same room
    # the rest of the page is shot in, so the subject is named explicitly.
    ("content-clips", "1536x1024", "high",
     "Three modern smartphones standing upright in a row on a dark surface, each "
     "screen showing a vertical video still of a different person talking to "
     "camera in a dark navy room, shoulders up, lit by one warm key. Seen from a "
     "low three quarter angle, deep navy surroundings, one warm amber light from "
     "above left, soft reflections on the dark surface. Product photography, "
     "shallow depth of field. No landscapes, no sunsets, no scenery on the "
     "screens. The screens carry no readable text and no user interface."),
]


def azure_key():
    z = zipfile.ZipFile(KEYS_DOC)
    xml = z.read("word/document.xml").decode("utf-8", "replace")
    txt = re.sub(r"<[^>]+>", "\n", re.sub(r"</w:p>", "\n", xml))
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    for i, l in enumerate(lines):
        if l == "gpt-image-2":
            for j in range(i, min(i + 12, len(lines))):
                if lines[j].lower() == "key" and j + 1 < len(lines):
                    return lines[j + 1]
    raise SystemExit("no gpt-image-2 key in " + KEYS_DOC)


def sess():
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=Retry(
        total=3, backoff_factor=6, status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"])))
    return s


def generate(key, s, prompt, out, size, quality, tries=3):
    body = {"prompt": prompt, "n": 1, "size": size,
            "quality": quality, "output_format": "png"}
    for a in range(tries):
        r = s.post(ENDPOINT, headers={"api-key": key, "Content-Type": "application/json"},
                   json=body, timeout=420)
        if r.status_code == 200:
            d = r.json()["data"][0]
            raw = (base64.b64decode(d["b64_json"]) if "b64_json" in d
                   else requests.get(d["url"], timeout=240).content)
            io.open(out, "wb").write(raw)
            return True
        print("    HTTP %s %s" % (r.status_code, r.text[:220]))
        time.sleep(10 * (a + 1))
    return False


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    key, s = azure_key(), sess()
    todo = [x for x in SHOTS if not args or any(x[0].startswith(a) for a in args)]
    for name, size, quality, prompt in todo:
        out = OUT / (name + ".png")
        if out.exists() and not force:
            print("  have  %s" % name); continue
        t0 = time.time()
        print("  gen   %-20s %s %s" % (name, size, quality), flush=True)
        ok = generate(key, s, HOUSE + prompt, out, size, quality)
        print("    %s  %.0fs  %.0f KB" % ("ok" if ok else "FAILED", time.time() - t0,
                                          out.stat().st_size / 1024 if ok else 0), flush=True)


if __name__ == "__main__":
    main()
