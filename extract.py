import cv2
import numpy as np
import os

def load_and_warp(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Cannot read {path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    best, best_area = None, 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > best_area:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                best_area = area
                best = approx
    if best is None:
        print("  WARNING: grid not found, using full image resized.")
        return cv2.resize(img, (450, 450))
    pts = best.reshape(4, 2).astype(np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    ordered = np.zeros((4, 2), dtype=np.float32)
    ordered[0] = pts[np.argmin(s)]
    ordered[2] = pts[np.argmax(s)]
    ordered[1] = pts[np.argmin(diff)]
    ordered[3] = pts[np.argmax(diff)]
    dst = np.array([[0, 0], [449, 0], [449, 449], [0, 449]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(ordered, dst)
    return cv2.warpPerspective(img, M, (450, 450))


def extract_cells(image_path, out_dir="extracted"):
    os.makedirs(out_dir, exist_ok=True)
    warped = load_and_warp(image_path)
    cv2.imwrite("warped_debug.png", warped)

    cell_size = 450 // 9
    saved = 0
    for r in range(9):
        for c in range(9):
            y1, y2 = r * cell_size, (r + 1) * cell_size
            x1, x2 = c * cell_size, (c + 1) * cell_size
            tile = warped[y1:y2, x1:x2]
            pad = 8
            tile = tile[pad:-pad, pad:-pad]
            gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)
            _, std = cv2.meanStdDev(gray)
            if std[0][0] < 20:      # skip blank cells
                continue
            # unique filename so you don't overwrite between runs
            base = os.path.splitext(os.path.basename(image_path))[0]
            fn = os.path.join(out_dir, f"{base}_r{r}_c{c}.png")
            cv2.imwrite(fn, tile)
            saved += 1

    print(f"  saved {saved} non-empty cells → {out_dir}/")


if __name__ == "__main__":
    import sys
    image = sys.argv[1] if len(sys.argv) > 1 else "sudoku.png"
    print(f"Extracting from {image}...")
    extract_cells(image)
    print()
    print("Now:")
    print("  1. Open the 'extracted' folder")
    print("  2. Drag each PNG into library/<digit>/ (1 through 9)")
    print("  3. Repeat with more images to grow the library")