"""
The transform matrix — generates the near-duplicate variants whose attestations
the registry must still surface (JIP-2 persistence). Optional: requires Pillow.

Two families:
  - INVARIANCE transforms (Tier A+ targets): same pixels, different bytes —
    recompression at several qualities, format changes, metadata strip. These
    SHOULD still match at A+.
  - DEGRADING transforms (Tier B targets / boundary): resize, crop. These are
    near-dups that should match only advisorily.

NOT included on purpose: regeneration / img2img / style-transfer. Those are the
declared laundering boundary and are measured as the *adversarial-evasion* set,
not as persistence positives.
"""
from typing import Iterator, Tuple


def _require_pil():
    try:
        from PIL import Image  # noqa
        return Image
    except ImportError as e:  # pragma: no cover
        raise ImportError("transforms need Pillow: pip install -r requirements.txt") from e


# (name, family) — family in {"invariance", "degrading"}
TRANSFORMS = [
    ("jpeg_q90", "invariance"),
    ("jpeg_q75", "invariance"),
    ("jpeg_q60", "invariance"),
    ("jpeg_q40", "invariance"),
    ("to_png", "invariance"),
    ("to_webp", "invariance"),
    ("strip_metadata", "invariance"),
    ("resize_75", "degrading"),
    ("resize_50", "degrading"),
    ("crop_5", "degrading"),
    ("crop_10", "degrading"),
]


def apply_transform(src_path: str, name: str, out_path: str) -> str:
    """Apply a single named transform, write to out_path, return out_path."""
    Image = _require_pil()
    img = Image.open(src_path).convert("RGB")
    w, h = img.size

    if name.startswith("jpeg_q"):
        q = int(name.split("q")[1])
        img.save(out_path, "JPEG", quality=q)
    elif name == "to_png":
        img.save(out_path, "PNG")
    elif name == "to_webp":
        img.save(out_path, "WEBP", quality=90)
    elif name == "strip_metadata":
        clean = Image.new("RGB", img.size)
        clean.putdata(list(img.getdata()))
        clean.save(out_path, "JPEG", quality=95)
    elif name.startswith("resize_"):
        f = int(name.split("_")[1]) / 100.0
        img.resize((max(1, int(w * f)), max(1, int(h * f)))).save(out_path, "JPEG", quality=92)
    elif name.startswith("crop_"):
        p = int(name.split("_")[1]) / 100.0
        dx, dy = int(w * p), int(h * p)
        img.crop((dx, dy, w - dx, h - dy)).save(out_path, "JPEG", quality=92)
    else:
        raise ValueError(f"unknown transform {name!r}")
    return out_path


def iter_transforms() -> Iterator[Tuple[str, str]]:
    yield from TRANSFORMS
