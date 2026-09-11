"""Optimize site images: resize oversized files and convert photos to JPEG.

- Photos are downscaled to a max side length per directory and saved as
  progressive JPEG (quality 85); transparent PNGs are flattened onto white.
- Files that would change extension (.png -> .jpg) are renamed and the old
  file is removed; the rename mapping is printed for updating references.
- SVG/AI/AVIF files and already-small images are left untouched.

Usage: python3 scripts/optimize_images.py
"""

import os
from PIL import Image, ImageOps

# directory -> max side length in pixels
RULES = {
    "assets/images/committee": 800,
    "assets/images/keynotes": 800,
    "assets/images/participants": 1200,
    "assets/images/macau": 2400,
    "assets/images/logo": 512,
}
SKIP_EXTS = {".svg", ".ai", ".avif"}
MIN_BYTES = 200 * 1024  # leave files smaller than this untouched


def has_real_alpha(img):
    if img.mode in ("RGBA", "LA"):
        alpha = img.getchannel("A")
        return alpha.getextrema()[0] < 255
    return False


def process(path, max_side):
    size_before = os.path.getsize(path)
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)

    if max(img.size) > max_side:
        img.thumbnail((max_side, max_side), Image.LANCZOS)

    root, ext = os.path.splitext(path)
    ext = ext.lower()
    out_path = path

    if ext == ".png" and not has_real_alpha(img):
        out_path = root + ".jpg"

    if out_path.lower().endswith((".jpg", ".jpeg")):
        img.convert("RGB").save(out_path, "JPEG", quality=85,
                               optimize=True, progressive=True)
    else:
        img.save(out_path, "PNG", optimize=True)

    if out_path != path:
        os.remove(path)

    size_after = os.path.getsize(out_path)
    return out_path, size_before, size_after


def main():
    total_before = total_after = 0
    for directory, max_side in RULES.items():
        for name in sorted(os.listdir(directory)):
            path = os.path.join(directory, name)
            if not os.path.isfile(path):
                continue
            if os.path.splitext(name)[1].lower() in SKIP_EXTS:
                continue
            if os.path.getsize(path) < MIN_BYTES and \
                    max(Image.open(path).size) <= max_side:
                continue
            try:
                out_path, before, after = process(path, max_side)
            except Exception as e:
                print(f"SKIP {path}: {e}")
                continue
            total_before += before
            total_after += after
            note = "" if out_path == path else "  [renamed]"
            print(f"{before/1024:9.0f}K -> {after/1024:6.0f}K  {out_path}{note}")
    print(f"\nTotal: {total_before/1024/1024:.1f} MB -> "
          f"{total_after/1024/1024:.1f} MB")


if __name__ == "__main__":
    main()
