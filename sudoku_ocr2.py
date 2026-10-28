import cv2
import numpy as np
import os

CELL = 50
PAD = 8
EMPTY_STD = 20
TEMPLATE = 28

_LIB_CACHE = None


def _warp(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    best_quad, best_area = None, 0
    for c in contours:
        area = cv2.contourArea(c)
        if area <= best_area:
            continue
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            best_quad, best_area = approx, area

    if best_quad is None:
        return cv2.resize(img, (450, 450))

    pts = best_quad.reshape(4, 2).astype(np.float32)
    s, d = pts.sum(axis=1), np.diff(pts, axis=1)
    ordered = np.array([pts[np.argmin(s)], pts[np.argmin(d)],
                        pts[np.argmax(s)], pts[np.argmax(d)]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(ordered,
        np.array([[0, 0], [449, 0], [449, 449], [0, 449]], dtype=np.float32))
    return cv2.warpPerspective(img, M, (450, 450))


def _normalize(cell):
    gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
    _, binimg = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if np.mean(binimg) > 127:
        binimg = cv2.bitwise_not(binimg)

    contours, _ = cv2.findContours(binimg, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    x, y, w, h = cv2.boundingRect(np.vstack([c.reshape(-1, 2) for c in contours]))
    if not (w and h):
        return None

    scale = 20.0 / max(w, h)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    digit = cv2.resize(binimg[y:y+h, x:x+w], (nw, nh), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((TEMPLATE, TEMPLATE), dtype=np.uint8)
    xo, yo = (TEMPLATE - nw) // 2, (TEMPLATE - nh) // 2
    canvas[yo:yo+nh, xo:xo+nw] = digit
    return cv2.GaussianBlur(canvas, (3, 3), 0)


def _load_library(lib_dir):
    lib = {}
    for d in range(1, 10):
        folder = os.path.join(lib_dir, str(d))
        if os.path.isdir(folder):
            lib[d] = [t for f in os.listdir(folder)
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))
                      for t in [_normalize(cv2.imread(os.path.join(folder, f)))]
                      if t is not None]
    return lib


def _classify(cell, lib):
    norm = _normalize(cell)
    if norm is None:
        return 0
    best_d, best_s = 0, float('inf')
    for d, samples in lib.items():
        for s in samples:
            score = float(np.mean(cv2.absdiff(norm, s)))
            if score < best_s:
                best_s, best_d = score, d
    return best_d


def get_board(image_path, lib_dir="library"):
    """Return 9x9 list-of-lists of ints (0 = empty) read from image_path."""
    global _LIB_CACHE
    if _LIB_CACHE is None:
        _LIB_CACHE = _load_library(lib_dir)
        if not any(_LIB_CACHE.values()):
            raise RuntimeError(f"No samples in {lib_dir!r}. Run extract.py first.")
    warped = _warp(image_path)
    board = [[0] * 9 for _ in range(9)]
    for r in range(9):
        for c in range(9):
            tile = warped[r*CELL:(r+1)*CELL, c*CELL:(c+1)*CELL]
            tile = tile[PAD:-PAD, PAD:-PAD]
            _, std = cv2.meanStdDev(cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY))
            if std[0][0] < EMPTY_STD:
                continue
            board[r][c] = _classify(tile, _LIB_CACHE)
    return board