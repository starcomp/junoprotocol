"""
Synthetic corpus generator (pure stdlib) — for an ILLUSTRATIVE end-to-end S1 run
before a real ≥1M haystack exists. No Pillow/OpenCV/numpy.

Generates synthetic grayscale "images" as 2D int matrices, the transform matrix
(invariance vs degrading), hard + confusable negatives, and a pure-python
*stand-in* for geometric verification (pixel correlation between scaled matrices).

⚠️ DEMO ONLY. The stand-in geometric check is NOT ORB/RANSAC, the images are not
real, and the numbers are NOT publishable. Its sole purpose is to exercise the
full match→eval pipeline and show the report's shape. The real harness
(scripts/run_s1.py + geom.py) uses real images and ORB/RANSAC.
"""
import math
import random

from .hashing import dct_phash, sha256_hex, hamming64
from .match import Feature, GeomResult


def _clamp(v):
    return 0 if v < 0 else (255 if v > 255 else int(v))


# --------------------------------------------------------------------------- #
# image generators
# --------------------------------------------------------------------------- #

def make_image(kind: str, n: int = 64, seed: int = 0, **kw):
    rnd = random.Random(seed)
    img = [[0] * n for _ in range(n)]
    if kind == "grad_h":
        slope = kw.get("slope", 1.0)
        for i in range(n):
            for j in range(n):
                img[i][j] = _clamp(j * 255.0 / (n - 1) * slope)
    elif kind == "grad_v":
        for i in range(n):
            for j in range(n):
                img[i][j] = _clamp(i * 255.0 / (n - 1))
    elif kind == "grad_diag":
        for i in range(n):
            for j in range(n):
                img[i][j] = _clamp((i + j) * 255.0 / (2 * (n - 1)))
    elif kind == "radial":
        c = (n - 1) / 2.0
        for i in range(n):
            for j in range(n):
                img[i][j] = _clamp(((i - c) ** 2 + (j - c) ** 2) ** 0.5 * (255.0 / (c * 1.41)))
    elif kind == "sine":
        fx, fy = kw.get("fx", 2), kw.get("fy", 1)
        ph = kw.get("phase", 0.0)
        for i in range(n):
            for j in range(n):
                img[i][j] = _clamp(127 + 127 * math.sin(2 * math.pi * (fx * j + fy * i) / n + ph))
    elif kind == "blobs":
        centers = [(rnd.randint(0, n - 1), rnd.randint(0, n - 1)) for _ in range(kw.get("k", 4))]
        for i in range(n):
            for j in range(n):
                v = 0.0
                for (ci, cj) in centers:
                    d2 = (i - ci) ** 2 + (j - cj) ** 2
                    v += 255 * math.exp(-d2 / (2 * (n / 6) ** 2))
                img[i][j] = _clamp(v)
    else:
        raise ValueError(f"unknown kind {kind!r}")
    return img


def to_bytes(mat):
    return bytes(_clamp(v) for row in mat for v in row)


def chash_of(mat):
    return sha256_hex(to_bytes(mat))


def feature_of(mat, ref):
    return Feature(chash=chash_of(mat), phash=dct_phash(mat), ref=ref)


# --------------------------------------------------------------------------- #
# transforms
# --------------------------------------------------------------------------- #

def quantize(mat, step=16):                 # recompression-like (invariance)
    return [[(_clamp(v) // step) * step for v in row] for row in mat]


def jitter(mat, amp=4, seed=1):             # mild noise (invariance)
    rnd = random.Random(seed)
    return [[_clamp(v + rnd.randint(-amp, amp)) for v in row] for row in mat]


def crop(mat, frac=0.1):                     # degrading (Tier B)
    n = len(mat)
    d = max(1, int(n * frac))
    return [row[d:n - d] for row in mat[d:n - d]]


def resize_half(mat):                        # degrading (Tier B)
    n = len(mat)
    m = n // 2
    return [[mat[2 * i][2 * j] for j in range(m)] for i in range(m)]


def occlude(mat, frac=0.45, seed=7):         # CONFUSABLE: keeps some global structure, changes content
    rnd = random.Random(seed)
    n = len(mat)
    out = [row[:] for row in mat]
    bw = int(n * frac)
    oi, oj = rnd.randint(0, n - bw), rnd.randint(0, n - bw)
    fill = rnd.randint(0, 255)
    for i in range(oi, oi + bw):
        for j in range(oj, oj + bw):
            out[i][j] = fill
    return out


# --------------------------------------------------------------------------- #
# geometric-verification STAND-IN (demo only) — pixel correlation
# --------------------------------------------------------------------------- #

def _resize(mat, size=16):
    sh, sw = len(mat), len(mat[0])
    return [[mat[(i * sh) // size][(j * sw) // size] for j in range(size)] for i in range(size)]


def scene_similarity(a, b, size=16):
    ra = [v for row in _resize(a, size) for v in row]
    rb = [v for row in _resize(b, size) for v in row]
    n = len(ra)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((ra[k] - ma) * (rb[k] - mb) for k in range(n))
    va = sum((x - ma) ** 2 for x in ra) ** 0.5
    vb = sum((x - mb) ** 2 for x in rb) ** 0.5
    if va == 0 or vb == 0:
        return 0.0
    return cov / (va * vb)   # Pearson r in [-1, 1]


def synthetic_geom(a, b):
    """Stand-in for ORB/RANSAC: maps pixel correlation to a GeomResult."""
    r = scene_similarity(a, b)
    inliers = int(max(0.0, r) * 50)
    return GeomResult(inliers=inliers, inlier_ratio=max(0.0, r))


__all__ = ["make_image", "to_bytes", "chash_of", "feature_of", "quantize", "jitter",
           "crop", "resize_half", "occlude", "scene_similarity", "synthetic_geom", "hamming64"]
