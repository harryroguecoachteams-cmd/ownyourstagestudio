#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Own Your Stage Studio: Sora 2 clips, to the deck's environment specification.

    python _art/sora.py probe          does the deployment answer at all
    python _art/sora.py <id>           create, poll and download that clip
    python _art/sora.py                everything not yet on disk

Memory says the swedencentral sora-2 deployment 404'd for an hour in July and
the working one was eastus2 `sora-2.1`, whose key was never written to disk.
`probe` settles which of those is true today rather than assuming. A 400 does
NOT prove routing: body validation happens before deployment resolution, so
only a 200/201 create counts.
"""
import io, os, re, sys, json, time, zipfile, pathlib
import requests

KEYS_DOC = r"E:\atreya\Azure AI keys.docx"
BASE = "https://sai-mo2tz038-swedencentral.cognitiveservices.azure.com/openai/v1/videos"
OUT = pathlib.Path(__file__).parent / "raw"

HOUSE = (
    "Cinematic, editorial, premium corporate production. Deep navy near-black "
    "room, one warm amber light source from above, soft falloff, fine haze in "
    "the air, subtle film grain. Slow deliberate camera move, nothing frantic. "
    "No text, no lettering, no logos, no user interface. No stage curtains, no "
    "microphone stands, no podium, no visible light fixtures in shot, no "
    "audience, no confetti. "
)

CLIPS = [
    ("stage-build", "1280x720", "8",
     "A slow push in across an empty dark studio floor as a single warm shaft of "
     "light strengthens and settles into a soft pool on the ground, haze drifting "
     "through the beam. Nothing else moves. The camera comes to rest."),
    ("panel-room", "1280x720", "8",
     "A slow lateral drift past four professional adults seated in a loose "
     "semicircle mid conversation in a dark navy room, warm amber light from above "
     "and behind them, faces catching the key as the camera passes. Shallow focus, "
     "documentary, unhurried."),
]


def azure_key(label="sora-2"):
    z = zipfile.ZipFile(KEYS_DOC)
    xml = z.read("word/document.xml").decode("utf-8", "replace")
    txt = re.sub(r"<[^>]+>", "\n", re.sub(r"</w:p>", "\n", xml))
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    for i, l in enumerate(lines):
        if l == label:
            for j in range(i, min(i + 12, len(lines))):
                if lines[j].lower() == "key" and j + 1 < len(lines):
                    return lines[j + 1]
    raise SystemExit("no %s key in %s" % (label, KEYS_DOC))


def create(key, model, prompt, size, seconds):
    r = requests.post(BASE, headers={"api-key": key, "Content-Type": "application/json"},
                      json={"model": model, "prompt": prompt,
                            "size": size, "seconds": seconds}, timeout=120)
    return r


def probe():
    key = azure_key()
    for model in ("sora-2", "sora-2.1"):
        r = create(key, model, HOUSE + CLIPS[0][3], "1280x720", "4")
        print("  model=%-8s HTTP %s  %s" % (model, r.status_code, r.text[:240]))
        if r.status_code in (200, 201):
            print("  -> ROUTING OK on %s, job %s" % (model, r.json().get("id")))
            return model
    return None


def run(name, size, seconds, prompt, model="sora-2"):
    key = azure_key()
    out = OUT / (name + ".mp4")
    if out.exists():
        print("  have  %s" % name); return
    r = create(key, model, prompt, size, seconds)
    if r.status_code not in (200, 201):
        print("  create failed %s %s" % (r.status_code, r.text[:300])); return
    vid = r.json()["id"]
    print("  %s queued as %s" % (name, vid), flush=True)
    t0 = time.time()
    while time.time() - t0 < 1800:
        time.sleep(15)
        g = requests.get("%s/%s" % (BASE, vid), headers={"api-key": key}, timeout=60)
        st = g.json().get("status")
        print("    %5.0fs %s" % (time.time() - t0, st), flush=True)
        if st == "completed":
            c = requests.get("%s/%s/content" % (BASE, vid),
                             headers={"api-key": key}, timeout=600)
            OUT.mkdir(parents=True, exist_ok=True)
            io.open(out, "wb").write(c.content)
            print("    saved %s  %.0f KB" % (out, len(c.content) / 1024))
            return
        if st in ("failed", "cancelled"):
            print("    %s: %s" % (st, json.dumps(g.json())[:400])); return
    print("    timed out")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "probe":
        probe()
    else:
        want = sys.argv[1:] or [c[0] for c in CLIPS]
        for n, size, secs, p in CLIPS:
            if n in want:
                run(n, size, secs, HOUSE + p)
