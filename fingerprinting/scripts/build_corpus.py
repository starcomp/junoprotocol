#!/usr/bin/env python3
"""
Build the S1 evaluation corpus.

Inputs:
  --originals DIR   images we treat as "previously attested" (organize in
                    subfolders by content type; the subfolder name = cluster).
  --negatives DIR   HARD negatives: visually-similar-but-distinct REAL media
                    (stock near-dups, meme/UI templates, same-product shots).
                    Subfolder name = cluster. Optionally a top-level `clean/` or
                    `current/` folder sets the haystack split.
  --out DIR         output corpus (writes variants/ + manifest.json).

For each original it emits the transform-matrix variants (recompression / format /
crop / resize) and records, in manifest.json, which origin + cluster + transform
each variant came from. The manifest is what scripts/run_s1.py consumes.

Requires Pillow (see requirements.txt).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from juno_fp import transforms  # noqa: E402

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def _list_images(root):
    for dirpath, _, files in os.walk(root):
        for f in files:
            if os.path.splitext(f)[1].lower() in IMG_EXT:
                yield os.path.join(dirpath, f)


def _cluster_and_split(path, root):
    rel = os.path.relpath(path, root)
    parts = rel.split(os.sep)
    split = "current"
    if parts and parts[0] in ("clean", "current"):
        split = parts[0]
        parts = parts[1:]
    cluster = parts[0] if len(parts) > 1 else "default"
    return cluster, split


def main():
    ap = argparse.ArgumentParser(description="Build the S1 precision corpus.")
    ap.add_argument("--originals", required=True)
    ap.add_argument("--negatives", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    var_dir = os.path.join(args.out, "variants")
    os.makedirs(var_dir, exist_ok=True)

    manifest = {"originals": [], "variants": [], "negatives": []}

    for orig in _list_images(args.originals):
        cluster, split = _cluster_and_split(orig, args.originals)
        manifest["originals"].append({"path": orig, "cluster": cluster, "split": split})
        stem = os.path.splitext(os.path.basename(orig))[0]
        for name, family in transforms.iter_transforms():
            ext = ".webp" if name == "to_webp" else (".png" if name == "to_png" else ".jpg")
            out_path = os.path.join(var_dir, f"{cluster}__{stem}__{name}{ext}")
            try:
                transforms.apply_transform(orig, name, out_path)
            except Exception as e:  # keep going; log
                print(f"  skip {orig} [{name}]: {e}", file=sys.stderr)
                continue
            manifest["variants"].append({
                "path": out_path, "origin": orig, "transform": name,
                "family": family, "cluster": cluster, "split": split,
            })

    for neg in _list_images(args.negatives):
        cluster, split = _cluster_and_split(neg, args.negatives)
        manifest["negatives"].append({"path": neg, "cluster": cluster, "split": split})

    with open(os.path.join(args.out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"originals={len(manifest['originals'])} "
          f"variants={len(manifest['variants'])} "
          f"negatives={len(manifest['negatives'])} -> {args.out}/manifest.json")


if __name__ == "__main__":
    main()
