#!/usr/bin/env python3
"""Check whether a rectangle of a plate or video frame can carry type.

    python3 text_zone.py plate.png --zone x,y,w,h --ink "#f8f8f6" [--display-only]
    python3 text_zone.py frames/*.png --zone 96,140,780,420 --ink "#161616"

For each image it reports the zone's mean luminance, the WCAG contrast between the planned type colour and
the zone (taken at the zone's worst 5 % of pixels, so a bright cloud under white type counts), and how busy
the zone is (mean gradient magnitude, 0-255 scale). Exit code 1 if any image fails.
"""
import argparse
import sys

import numpy as np
from PIL import Image

BUSY_LIMIT = 6.0  # mean |gradient| above this reads as texture behind small type


def srgb_to_linear(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def rel_luminance(rgb):
    lin = srgb_to_linear(rgb.astype(np.float64))
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def contrast(l1, l2):
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def parse_hex(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def check(path, zone, ink_lum, display_only):
    im = np.asarray(Image.open(path).convert("RGB"))
    x, y, w, h = zone
    H, W = im.shape[:2]
    if x < 0 or y < 0 or x + w > W or y + h > H:
        raise SystemExit(f"{path}: zone {zone} is outside the {W}x{H} image")
    region = im[y:y + h, x:x + w]
    lum = rel_luminance(region)
    # worst case for the planned ink: the pixels closest to it in luminance
    worst = np.percentile(lum, 95) if ink_lum > lum.mean() else np.percentile(lum, 5)
    ratio = contrast(ink_lum, worst)
    gray = region.mean(axis=2)
    busy = float(np.hypot(*np.gradient(gray)).mean())
    need = 3.0 if display_only else 4.5
    ok = ratio >= need and (display_only or busy <= BUSY_LIMIT)
    return ok, lum.mean(), ratio, busy, need


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+")
    ap.add_argument("--zone", required=True, help="x,y,w,h in pixels of the image")
    ap.add_argument("--ink", required=True, help="planned type colour, e.g. #f8f8f6")
    ap.add_argument("--display-only", action="store_true", help="zone holds only display-size type (3:1 is enough, texture allowed)")
    a = ap.parse_args()
    zone = tuple(int(v) for v in a.zone.split(","))
    if len(zone) != 4:
        raise SystemExit("--zone needs x,y,w,h")
    ink_lum = float(rel_luminance(parse_hex(a.ink)[None, None, :])[0, 0])
    failed = 0
    for p in a.images:
        ok, mean, ratio, busy, need = check(p, zone, ink_lum, a.display_only)
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {p}  luminance {mean:.3f}  contrast {ratio:.2f} (need {need})  busy {busy:.1f} (limit {BUSY_LIMIT})")
    if len(a.images) > 1:
        print(f"{len(a.images) - failed}/{len(a.images)} pass")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
