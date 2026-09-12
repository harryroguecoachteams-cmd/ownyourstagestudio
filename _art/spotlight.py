#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Own Your Stage Studio: spotlight hero reveal, Sora 2 on Azure.

    python _art/spotlight.py reveal 2   two 8s reveal takes, 1280x720 (Azure max)
    python _art/spotlight.py sweep 2    two 4s light-only search clips
    python _art/spotlight.py resume     poll any job ids left in jobs.json

Brief: 12 Sep 2026 JSON spec. Azure caps at 1280x720, so the 1920x1080
deliverable is an upscale done in finish.py after a take is chosen.
$0.10/s => $0.80 per take.
"""
import io, sys, json, time, pathlib, requests
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from sora import azure_key, BASE

OUT = pathlib.Path(__file__).parent / "raw" / "spotlight"
JOBS = OUT / "jobs.json"

PROMPT = (
    "Live-action cinematic brand film, photorealistic, medium-wide shot, locked-off "
    "camera. A dark empty studio floor in deep navy-black, thin haze near the ground, a "
    "little dust in the air. The only light is a soft-edged warm golden follow spot "
    "operated by hand from high above and out of frame. "
    "FIRST HALF, empty floor only: the shot opens nearly black. A diffused warm pool of "
    "light fades up on the floor. The follow spot slowly drifts left across the empty "
    "floor, hunting, slightly uneven like a human on the handle. It stops, swings back "
    "and sweeps right, speeding up then easing off with a small overshoot. It comes back "
    "and settles in the exact center of the frame. The pool sits empty for a moment. "
    "SECOND HALF: the light at center now reaches a woman who was standing there in the "
    "dark all along. She is revealed only by the light landing on her; she does not walk, "
    "step, fade or materialize. An adult professional speaker, upright, square to camera, "
    "eyes on the lens, hands lightly clasped in front, calm grounded self-assured "
    "expression. She holds the pose to the end with only natural breathing and tiny "
    "settling of the shoulders and head, like a person holding still for a portrait. "
    "Real skin texture, natural hair, subtle facial asymmetry, correct anatomy and "
    "hands, understated dark professional clothing. The spot gives warm highlights with "
    "soft falloff, elegant shadow on the face, a correct floor shadow, haze visible in "
    "the beam. She fills about half the frame height so her face reads clearly. "
    "No text, no logos, no microphone, no curtains, no equipment, no audience, no "
    "visible light fixture, no glow or particle effects, no camera movement, no pose "
    "change after the reveal. The spotlight stays at full strength through the very last "
    "frame; it never dims, flickers or fades out."
)


SWEEP = (
    "Live-action cinematic brand film, photorealistic, medium-wide shot, locked-off "
    "camera. A completely empty dark studio floor in deep navy-black, thin haze near the "
    "ground, a little dust in the air. Nobody is in the shot at any point. The only light "
    "is a soft-edged warm golden follow spot operated by hand from high above and out of "
    "frame. The shot opens nearly black. A diffused warm pool of light fades up on the "
    "floor left of center. The pool slowly drifts further left across the empty floor, "
    "hunting, slightly uneven like a human on the handle. It stops, swings back and "
    "sweeps right past center, speeding up then easing off with a small overshoot, then "
    "glides back and settles in the exact center of the frame at full strength and stays "
    "there. Haze visible in the beam, soft falloff on the floor. No text, no logos, no "
    "people, no equipment, no visible light fixture, no glow or particle effects, no "
    "camera movement."
)

DRIFT = (
    "Live-action cinematic brand film, photorealistic, medium-wide shot. A dark empty "
    "studio floor in deep navy-black, thin haze near the ground, a little dust in the "
    "air. The only light is one soft-edged warm golden spotlight from high above, "
    "fixture out of frame, making a single diffused pool on the floor. "
    "FIRST HALF: the shot opens nearly black as the pool fades up. The camera, on a "
    "slow hand-guided pan, searches: it drifts so the pool slides to the left third of "
    "the frame, pauses, then pans the other way so the pool travels right past center "
    "with a small overshoot, then eases back until the pool sits dead center and the "
    "camera locks. The pool holds empty for a beat. "
    "SECOND HALF: with the camera now still, the light at center reaches a woman who "
    "was standing in that spot in the dark the whole time. She is revealed only by the "
    "light reaching her; she does not walk, step, fade or materialize. An adult "
    "professional speaker, upright, square to camera, eyes on the lens, hands lightly "
    "clasped in front, calm grounded self-assured expression, holding the pose to the "
    "end with only natural breathing and tiny settling of shoulders and head. Real skin "
    "texture, natural hair, subtle facial asymmetry, correct anatomy and hands, "
    "understated dark professional clothing. Warm highlights with soft falloff, elegant "
    "shadow on the face, correct floor shadow, haze in the beam. She fills about half "
    "the frame height. The spotlight stays at full strength through the last frame. "
    "No text, no logos, no microphone, no curtains, no equipment, no audience, no "
    "visible light fixture, no glow or particle effects, no camera movement after the "
    "lock, no pose change after the reveal."
)

PROMPTS = {"reveal": PROMPT, "sweep": SWEEP, "drift": DRIFT}
SECONDS = {"reveal": "8", "sweep": "4", "drift": "8"}


def load_jobs():
    return json.loads(JOBS.read_text()) if JOBS.exists() else {}


def save_jobs(j):
    JOBS.write_text(json.dumps(j, indent=1))


def create(key, name, kind="reveal"):
    r = requests.post(BASE, headers={"api-key": key, "Content-Type": "application/json"},
                      json={"model": "sora-2", "prompt": PROMPTS[kind],
                            "size": "1280x720", "seconds": SECONDS[kind]}, timeout=120)
    if r.status_code not in (200, 201):
        print("  create failed %s %s" % (r.status_code, r.text[:300])); return None
    vid = r.json()["id"]
    print("  %s queued as %s" % (name, vid), flush=True)
    return vid


def poll(key, jobs):
    t0 = time.time()
    pending = {n: v for n, v in jobs.items() if not (OUT / (n + ".mp4")).exists()}
    while pending and time.time() - t0 < 1800:
        time.sleep(15)
        for n, vid in list(pending.items()):
            g = requests.get("%s/%s" % (BASE, vid), headers={"api-key": key}, timeout=60)
            st = g.json().get("status")
            print("    %5.0fs %-8s %s" % (time.time() - t0, n, st), flush=True)
            if st == "completed":
                c = requests.get("%s/%s/content" % (BASE, vid),
                                 headers={"api-key": key}, timeout=600)
                out = OUT / (n + ".mp4")
                io.open(out, "wb").write(c.content)
                print("    saved %s  %.0f KB" % (out, len(c.content) / 1024))
                del pending[n]
            elif st in ("failed", "cancelled"):
                print("    %s: %s" % (st, json.dumps(g.json())[:400]))
                del pending[n]
    if pending:
        print("  timed out on %s" % list(pending))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    key = azure_key()
    jobs = load_jobs()
    if sys.argv[1:] == ["resume"]:
        poll(key, jobs); sys.exit()
    kind = sys.argv[1] if sys.argv[1:] else "reveal"
    n_takes = int(sys.argv[2]) if sys.argv[2:] else 2
    prefix = "take" if kind == "reveal" else kind
    start = len([j for j in jobs if j.startswith(prefix)]) + 1
    for i in range(start, start + n_takes):
        name = "%s%d" % (prefix, i)
        vid = create(key, name, kind)
        if vid:
            jobs[name] = vid; save_jobs(jobs)
    poll(key, jobs)
