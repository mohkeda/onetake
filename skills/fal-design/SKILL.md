---
name: fal-design
description: "Design guideline for films and stills built from fal-generated media — GPT Image 2.5 (flare / sunburst) plates and edits, Seedance 2.5 motion (text-, image-, reference-to-video) — composed in HyperFrames, plain HTML/GSAP or Three.js. Its main job is the type: generated media looks rich and the words on top look like a default template, so this skill splits every frame into a generated plate and set typography, plans the type system and the empty space before prompting, and checks that a plate can carry text before anything is animated. Use when output from fal looks 'blah', 'generic', 'AI-looking', when titles or captions over generated video look flat, when a poster or thumbnail needs real text, when prompting GPT Image 2.5 or Seedance 2.5 for a composition that will carry type, or when staging fal media in HyperFrames / Three.js."
---

# fal-design

Generated pixels and set type are two different crafts. Models are good at light, material, depth and motion.
They are bad at being *told where to leave room*, and they render letters as texture. Most "blah" text design
in fal-based work comes from one of two habits:

1. **The words were generated.** A slogan typed into the image or video prompt comes back legible-ish, in a face
   nobody chose, at a size nobody chose, sometimes misspelt, and it cannot be animated or retimed.
2. **The words were dropped on afterwards.** A default sans, centred, white with a drop shadow, over the busiest
   part of a plate that was never composed for it.

The fix is a split: **the plate is generated, the type is set, and the plate is composed for the type.**
Decide the type first, prompt the plate to leave its space, check the space, then animate.

## When this skill, and when not

- Titles, captions, kinetic type, lower thirds, end cards over fal stills or video — **yes**.
- Posters, thumbnails, packaging, signage where the text is part of the picture — **yes**, §6 (diegetic text).
- A launch film built from real UI with no generated plates — use `onetake` (the root `SKILL.md`).
- Pure image generation with no words anywhere — the model guides in `references/prompts.md` still apply,
  the type rules don't.

## 1 · Type system before any prompt (hard rule)

Pick the look before generating anything, because the look decides what the plate must leave room for.
Reuse a look from `looks/looks.json` (eight colours, three OFL faces in `looks/fonts`) or write one with
the same shape. A type system is:

| Role | Rule |
|---|---|
| **display** | one face, set big. Display size is **≥ 5× text size** on a 1080-tall frame (e.g. 140 px vs 28 px). Tracking tightens as size grows: −0.01 to −0.04 em. |
| **text** | one face for everything that is read rather than seen. 26–34 px at 1080p, 1.25–1.4 line height, ≤ 32 characters per line in video. |
| **utility** | optional mono or condensed for labels, numbers, timecodes. Uppercase gets +0.06 to +0.12 em tracking. |
| **colour** | type in `ink` or `ground` only; **one** `accent`, used on one word or one rule per frame. |

Two faces per frame, three per film. Weight contrast (300 vs 800) or style contrast (serif display, sans text)
does the work that colour and effects are usually asked to do. No outlines, no glow, no default drop shadow:
if type needs a shadow to read, the plate is wrong (§3).

## 2 · Lay out the frame, then reserve the space

Draw the frame on a grid before prompting: 12 columns, margins at 6–8 % of width, the safe area for the
platform (9:16 social: nothing in the top 12 % or the bottom 20 %). Mark the **type zone** — the rectangle the
words will occupy — and give it a side: top third, left two columns, lower band. Centred type is a choice,
not a default; most strong frames put the words on a grid line and the subject on the opposite third.

Write the zone down as numbers (`x, y, w, h` in px). The plate prompt and the check both use it.

## 3 · Prompt plates that leave room

The plate prompt says where the subject is, where the calm is, and that there is no text:

- name the composition: *"subject on the right third, lower half; the left 45 % is open sky, soft gradient,
  no detail"*;
- name the tone under the type zone: dark under light type, light under dark type, and low texture;
- say **"no text, no letters, no logos, no signage"** — and for scenes that would naturally carry signs,
  *"signage with no readable letters"*;
- choose `image_size` for the final frame at prompt time (custom sizes: both edges ÷ 16, long edge ≤ 3840).

Then check the zone before spending anything on motion:

```bash
python3 skills/fal-design/scripts/text_zone.py plate.png --zone 96,140,780,420 --ink "#f8f8f6"
```

It reports the zone's mean luminance, the WCAG contrast of the planned type colour against it (worst 5 % of
pixels, not the average) and how busy the zone is. **PASS** needs contrast ≥ 4.5 for text sizes, ≥ 3 for
display only, and low busyness. A FAIL means re-prompt or edit the plate (one change per edit pass), or move
the zone. A scrim is the last resort, and then a soft gradient over the whole side, never a box behind the words.

## 4 · Motion plates (Seedance 2.5)

Animate the approved still with `bytedance/seedance-2.5/image-to-video`. The prompt has two halves:
**motion** (what moves, the camera, in staged beats) and **protection** (what the still already got right and
must hold, including the empty type zone).

- If type sits on the plate the whole time, lock the camera or move it slowly *away* from the zone:
  *"camera locked; only the clouds drift; the left half stays empty and soft"*.
- If the type should be revealed by the move, write the move to end on the composed still: build the end frame
  by **editing** the first frame with GPT Image 2.5 and pass it as `end_image_url`.
- **"No on-screen text, no subtitles."** in every video prompt. Dialogue goes in double quotes only when you
  want lip-synced speech.
- Draft at 480p (`draft: true`), check the zone on a few frames, finish at 1080p from the `draft_id`.

Run `text_zone.py` on frames grabbed across the clip (`ffmpeg -i clip.mp4 -vf fps=2 f_%03d.png`); the zone has to
pass on every frame the type is on screen.

## 5 · Set and move the type (HyperFrames / HTML / Three.js)

Type lives in HTML over the plate, in the real font files, so it can be retimed, translated and fixed without
regenerating anything. `templates/title-over-plate.html` is a HyperFrames composition that does this.

Kinetic rules that separate designed type from template type:

- **Reveal by line or word, not by letter**, with a mask (clip-path / overflow) rather than a fade; stagger
  60–120 ms; ease out with a slight settle (e.g. `power3.out` or a spring), never linear.
- **Hold long enough to read**: on-screen time ≥ 0.5 s + words ÷ 3.5 s. A six-word line holds ≥ 2.2 s
  after it lands.
- **Move with the plate, not against it**: if the camera pushes in, the type drifts 1–2 % the same way, or
  stays locked to the grid; it never floats independently.
- **One thing moves at a time** in the type zone. A title animating while a caption animates reads as noise.
- Exits are shorter than entrances (≈ 60 %).

Three.js: keep words as an HTML layer over the canvas, or use SDF text (`troika-three-text`) loaded from the
same font file. Never put generated letters on a texture.

## 6 · Diegetic text: when the words are part of the picture

A poster in a scene, a label on a bottle, a thumbnail whose type is part of the illustration. Use GPT Image 2.5
and treat the copy as fixed data:

- quote the exact copy in the prompt, say how many times it appears, where it sits and how it is set
  (*"the word "NORTHWIND" once, centred on the label, condensed sans, all caps, letterspaced, ink black"*);
- spell invented brand names letter by letter if they come back wrong;
- end with **"no other text"**;
- use `quality: "high"` or above whenever there is small type or more than one typeface; `sunburst` when the
  frame will be enlarged or inspected;
- read every word in the output. Legible and correct are different properties.

If the copy will change, or must be pixel-exact, generate the object blank and composite the type yourself.

## 7 · Check before showing anyone

- every zone passes `text_zone.py` on the still and on frames across each clip;
- the type reads on a phone: export a frame at 360 px wide and look at it;
- no more than two faces per frame, one accent per frame;
- no generated letters anywhere unless §6 put them there on purpose, and those are spelled right;
- type holds meet the reading-time rule.

## Files

- `references/prompts.md` — endpoints, parameters and prompt shapes for GPT Image 2.5 and Seedance 2.5,
  plus a symptom → fix table for type that looks generic.
- `scripts/text_zone.py` — contrast and busyness check for a type zone on a plate or frame.
- `templates/title-over-plate.html` — HyperFrames composition: video plate + masked line reveal in the look's faces.
