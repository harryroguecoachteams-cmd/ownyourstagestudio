# The brand film

> **STALE AS OF SEPTEMBER 2026.** This renders the OLD identity: Crimson
> Pro and Work Sans, Authority Navy and Spotlight Gold. The brand sheet that
> replaced them is Montserrat and Lato on Charcoal with Signature Red, and
> the site has been rebuilt to it. The film is not shipped on the site, so
> nothing live is out of date, but re-render this only after porting the
> palette and the two fonts. See the top of DELIVERY.md for the mapping.

`render_film.py` renders `assets/media/oyss-how-it-works.mp4`: 1600x900, 25
seconds, silent, about 940KB.

It is a script and not a video file on purpose. The copy, the timing and the
stage are all data at the top of the file, so a line can be rewritten and the
film re-rendered in about two minutes instead of being re-shot.

## Running it

Needs Pillow and ffmpeg on PATH, plus the two brand fonts in `fonts/`:

    Crimson Pro   https://fonts.google.com/specimen/Crimson+Pro
    Work Sans     https://fonts.google.com/specimen/Work+Sans

both as the variable `[wght]` TTFs, named exactly as the file expects.

    python render_film.py oyss-how-it-works.mp4

Then copy the result to `assets/media/` and cut a new poster:

    ffmpeg -y -i oyss-how-it-works.mp4 -ss 6.4 -frames:v 1 -q:v 3 \
      ../assets/media/oyss-how-it-works-poster.jpg

## What to change

- `COPY` is the five beats: eyebrow, headline, subline.
- `BEAT` is the timeline in seconds. Every animation reads its window from
  here, so retiming a beat retimes everything inside it.
- `CX`, `GY`, `HOSTY`, `ROWY`, `STRIPY` are the stage. Move them together.

The film renders straight into ffmpeg over a pipe, so there are no frame files
to clean up.
