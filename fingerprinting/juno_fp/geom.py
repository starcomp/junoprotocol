"""
Geometric verification (ORB + RANSAC) — the uncorrelated precision lever (JIP-2).

Optional: requires OpenCV (opencv-python-headless). Imported lazily so the pure
core works without it. Returns a match.GeomResult, or None if not enough features.
"""
from typing import Optional

from .match import GeomResult


def _require_cv2():
    try:
        import cv2  # noqa
        return cv2
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "geometric verification needs OpenCV: pip install -r requirements.txt"
        ) from e


def orb_ransac(path_a: str, path_b: str, nfeatures: int = 1000) -> Optional[GeomResult]:
    """
    Detect ORB keypoints in both images, match descriptors, and run RANSAC on a
    homography fit. Returns inlier count + inlier ratio (a robust 'same scene'
    signal whose failure mode is NOT correlated with global pHash/PDQ/CLIP).
    """
    cv2 = _require_cv2()
    a = cv2.imread(path_a, cv2.IMREAD_GRAYSCALE)
    b = cv2.imread(path_b, cv2.IMREAD_GRAYSCALE)
    if a is None or b is None:
        return None

    orb = cv2.ORB_create(nfeatures=nfeatures)
    ka, da = orb.detectAndCompute(a, None)
    kb, db = orb.detectAndCompute(b, None)
    if da is None or db is None or len(ka) < 8 or len(kb) < 8:
        return None

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(da, db)
    if len(matches) < 8:
        return GeomResult(inliers=len(matches), inlier_ratio=0.0)

    import numpy as np
    src = np.float32([ka[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst = np.float32([kb[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    _, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    if mask is None:
        return GeomResult(inliers=0, inlier_ratio=0.0)
    inliers = int(mask.sum())
    return GeomResult(inliers=inliers, inlier_ratio=inliers / len(matches))
