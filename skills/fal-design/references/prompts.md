# fal models — endpoints, parameters, prompt shapes

Checked against fal's model pages and guides in October 2026. Endpoints change; confirm the schema on the
model's `llms.txt` (`https://fal.ai/models/<id>/llms.txt`) before relying on an enum.

## GPT Image 2.5

| Endpoint | Use |
|---|---|
| `openai/gpt-image-2.5/flare/text-to-image` | plates, drafts, batches — faster |
| `openai/gpt-image-2.5/flare/edit` | edits to an approved plate |
| `openai/gpt-image-2.5/sunburst/text-to-image` | frames that will be enlarged or inspected; small diegetic type |
| `openai/gpt-image-2.5/sunburst/edit` | fine edits on those frames |

Parameters (shared): `prompt`; `image_size` (`square_hd`, `square`, `portrait_4_3`, `portrait_16_9`,
`landscape_4_3`, `landscape_16_9`, `auto`, or `{width, height}` with both edges ÷ 16, long edge ≤ 3840,
ratio ≤ 3:1, 655,360–8,294,400 px); `quality` (`auto`, `low`, `medium`, `high` default, `xhigh`, `max`);
`background` (`auto`, `transparent`, `opaque` — transparent needs png/webp); `num_images`; `output_format`
(`png` default, `jpeg`, `webp`); `output_compression`. Edit adds `image_urls` (up to 16 references) and
`mask_url`.

Habits:
- `medium` for composition drafts, `high`+ once anything carries small type.
- One change per edit pass, and restate what must stay every pass.
- For transparency, check the alpha channel of the file; a painted checkerboard has none.
- Number references (`image 1`, `image 2`) and give each a role.

## Seedance 2.5

| Endpoint | Input |
|---|---|
| `bytedance/seedance-2.5/text-to-video` | prompt only |
| `bytedance/seedance-2.5/image-to-video` | `image_url` (first frame), optional `end_image_url` |
| `bytedance/seedance-2.5/reference-to-video` | `image_urls`, `video_urls`, `audio_urls` — addressed as `@Image1`, `@Video1`, `@Audio1` in list order; also edits and extends |

Image-to-video parameters: `prompt`; `resolution` (`480p`, `720p` default, `1080p`); `draft` (480p preview,
returns `draft_id` to finish at 1080p within seven days); `duration` (`auto` or `"4"`…`"30"`);
`aspect_ratio` (`auto` for i2v); `generate_audio` (default `true`); `bitrate_mode` (`standard`, `high`);
`codec` (`auto`, `H264`, `H265`).

Habits:
- Name lens height and movement explicitly; say "no camera movement" when the type zone must hold.
- Multi-beat shots as staged beats: one primary change per stage, and what is on screen when the stage ends.
- Timestamps are consecutive, non-overlapping ranges; they set proportion, not exact frames.
- Build an end frame by editing the first frame, never by a fresh text-to-image prompt.
- Trim reference video before sending it; input seconds are billed.

## Prompt shapes

**Plate with a reserved type zone (GPT Image 2.5)**

```
Frame: 1920×1080, wide, eye level.
Subject: a single ceramic lamp on a walnut desk, right third, lower half, warm practical light.
Type zone: the left 45 % of the frame is a plain plaster wall in soft shadow, even tone, no objects,
no texture changes. It stays darker than the subject.
Light: late afternoon, low sun from the right, long soft falloff to the left.
No text, no letters, no logos, no signage.
```

**Edit for an end frame**

```
Image 1 is the approved plate. Change one thing: the lamp is switched on and the wall on the left
catches its glow. Keep the composition, the camera, the desk, and the left 45 % free of objects.
No text.
```

**Motion with protection (Seedance image-to-video)**

```
Motion: camera locked at desk height for the whole clip. The lamp switches on at about 1 s; warm light
blooms across the wall, then settles. Dust drifts slowly through the beam.
Protect: the composition, the lamp's shape and the empty left half of the frame stay as in the image;
nothing enters the left half.
No on-screen text, no subtitles.
```

**Diegetic copy (GPT Image 2.5, sunburst, quality high)**

```
A kraft paper coffee bag standing on concrete, studio light from above left.
Label: the word "NORTHWIND" once, centred on the front label, condensed sans serif, all caps,
wide letterspacing, black ink. Below it, "SINGLE ORIGIN · 250 G" once, small, same face.
No other text anywhere in the image.
```

## Symptom → fix

| What it looks like | Why | Fix |
|---|---|---|
| Title fights the background | plate never composed for type | reserve a zone in the prompt (§3), check with `text_zone.py` |
| White text with a drop shadow | contrast patched after the fact | change the plate or the zone; type colour from the look |
| Everything the same size | no scale contrast | display ≥ 5× text; one display line per frame |
| Looks like a template | centred, default sans, fade-in | grid-aligned, chosen faces, masked line reveal with a settle |
| Words wobble / morph in video | text was generated in the video | "No on-screen text" in the prompt; set type in HTML |
| Misspelt brand on product | copy not locked | exact quotes, letter-by-letter spelling, "no other text", or composite it yourself |
| Type and camera disagree | type animated on its own | lock type to the grid or drift it with the camera |
| Caption unreadable on phone | too small, too long | ≥ 26 px at 1080p, ≤ 32 characters per line, check at 360 px wide |
