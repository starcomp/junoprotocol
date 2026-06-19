"""
Content hashing — pure stdlib.

  chash : SHA-256 of canonical bytes (exact identity, Tier A primary key).
  phash : 64-bit DCT perceptual hash (near-duplicate identity), algorithm-compatible
          with the standard pHash / imagehash recipe: grayscale -> 32x32 -> 2D DCT-II
          -> top-left 8x8 low-frequency block -> median threshold -> 64 bits.

No numpy. The DCT is the textbook separable DCT-II; for 32x32 inputs this is fast
enough for a harness and keeps the core dependency-free and testable everywhere.
Real-image loading lives in phash_from_image() behind an optional Pillow import.
"""
import hashlib
import math
from functools import lru_cache

# --------------------------------------------------------------------------- #
# chash
# --------------------------------------------------------------------------- #

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def chash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------- #
# phash (DCT)
# --------------------------------------------------------------------------- #

_PH_SIZE = 32   # DCT input size
_HASH_BITS = 8  # 8x8 low-freq block -> 64-bit hash


@lru_cache(maxsize=8)
def _dct_basis(n: int):
    """Cosine basis: basis[k][i] = cos(pi/n * (i + 0.5) * k)."""
    return tuple(
        tuple(math.cos((math.pi / n) * (i + 0.5) * k) for i in range(n))
        for k in range(n)
    )


def _dct_1d(vec):
    n = len(vec)
    basis = _dct_basis(n)
    return [sum(vec[i] * basis[k][i] for i in range(n)) for k in range(n)]


def _dct_2d(mat):
    # rows then columns (separable DCT-II)
    rows = [_dct_1d(r) for r in mat]
    n = len(rows)
    m = len(rows[0])
    out = [[0.0] * m for _ in range(n)]
    for j in range(m):
        col = _dct_1d([rows[i][j] for i in range(n)])
        for i in range(n):
            out[i][j] = col[i]
    return out


def _resize_nn(gray, h, w):
    """Nearest-neighbor resize of a 2D list to h x w."""
    sh, sw = len(gray), len(gray[0])
    return [[gray[(i * sh) // h][(j * sw) // w] for j in range(w)] for i in range(h)]


def _median(values):
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0


def dct_phash(gray) -> int:
    """64-bit DCT pHash from a 2D grayscale matrix (list of lists, any size)."""
    resized = _resize_nn(gray, _PH_SIZE, _PH_SIZE)
    dct = _dct_2d(resized)
    block = [dct[i][j] for i in range(_HASH_BITS) for j in range(_HASH_BITS)]
    med = _median(block)
    bits = 0
    for v in block:
        bits = (bits << 1) | (1 if v > med else 0)
    return bits


def hamming64(a: int, b: int) -> int:
    return (a ^ b).bit_count()


# --------------------------------------------------------------------------- #
# optional real-image loader (Pillow)
# --------------------------------------------------------------------------- #

def phash_from_image(path: str) -> int:
    """DCT pHash of a real image file. Requires Pillow (see requirements.txt)."""
    try:
        from PIL import Image
    except ImportError as e:  # pragma: no cover
        raise ImportError("phash_from_image needs Pillow: pip install -r requirements.txt") from e
    img = Image.open(path).convert("L").resize((_PH_SIZE, _PH_SIZE))
    px = list(img.getdata())
    gray = [px[r * _PH_SIZE:(r + 1) * _PH_SIZE] for r in range(_PH_SIZE)]
    return dct_phash(gray)
