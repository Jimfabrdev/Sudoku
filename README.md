# Sudoku Solver — Screen OCR + Backtracking

Read a Sudoku board from an image, solve it with backtracking, and type the
solution automatically into a Sudoku web page.

Built as a teaching project: computer vision (OpenCV) + classic backtracking + GUI automation.

## How it works

1. **`extract.py`** — detects the Sudoku grid in an image, warps it to 450×450,
   splits it into 81 cells and saves the non-empty ones as PNGs. You then sort
   those PNGs into `library/<digit>/` (1–9) to build a template library.
2. **`sudoku_ocr2.py`** — reads a board image, classifies each cell by comparing
   it against the templates in `library/` (normalized to 28×28, mean absolute
   difference), and returns a 9×9 grid of ints (`0` = empty).
3. **`solver.py`** — solves the grid with backtracking and types the solution
   into the focused window using `pyautogui`, following a serpentine path.

## Requirements

```bash
pip install -r requirements.txt

requirements.txt:

text
opencv-python
numpy
pyautogui

Usage
1. Build the template library (once)
bash
python extract.py path/to/sudoku.png
This creates extracted/ with one PNG per non-empty cell. Move each PNG into
library/<digit>/ (e.g. library/7/). Repeat with more images to grow the
library — 5–6 samples per digit is usually enough.

2. Solve and auto-type
bash
python solver.py
You will be asked for a delay. During the delay, switch to the Sudoku page and
click the first cell. The script then types the solution.

⚠️ Move the mouse to a screen corner to abort (pyautogui failsafe).

Notes & limitations
Works best with clean, straight, high-contrast board images and a consistent
digit font. Handwritten or heavily rotated boards are not supported.

The OCR uses template matching, so accuracy depends on the quality of
library/. Add more samples if a digit is misread.

library/ contains isolated digit thumbnails only (no grid, no background),
produced with extract.py from publicly available Sudoku puzzles.

Automation is for educational/demo purposes. Check the terms of service of any
site you use it on.

