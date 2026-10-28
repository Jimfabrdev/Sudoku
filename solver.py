import pyautogui
import time
from sudoku_ocr2 import get_board

pyautogui.PAUSE = 0.001
delay = int(input("Give delay time:"))
time.sleep(delay)



def is_valid(A):

    def has_dupes(lst1, BLANK = 0):
        sublist = [v for v in lst1 if v != BLANK]
        if len(sublist) != len(set(sublist)):
            return True
        return False

    if any(has_dupes(row) for row in A):
        return False
    if any(has_dupes(col) for col in zip(*A)):
        return False

    subgrid = [[] for _ in range(9)]
    for i in range(9):
        for j in range(9):
            idx = (i // 3)* 3 + (j // 3)
            subgrid[idx].append(A[i][j])
    if any(has_dupes(sg) for sg in subgrid):
        return False

    return True

A = get_board("sudoku.png")  

PREV = []
B = []

for i in range(9):
    for j in range(9):
        if A[i][j] == 0:
            B.append((i,j))
            PREV.append(0)

n = len(PREV)
i = 0
while 0 <= i < n:
    x,y = B[i]
    A[x][y] = 0
    backtrack = True
    for j in range(PREV[i]+1,10):
        A[x][y] = j
        if is_valid(A):
            PREV[i] = j
            i += 1
            backtrack = False
            break
    if backtrack:
        PREV[i] = 0
        A[x][y] = 0
        i -= 1



sudoku_str = ""
for i,row in enumerate(A):
    if i % 2 != 0:
        row = row[::-1]
    for ch in row:
        sudoku_str += str(ch)

idx = 0
for i in range(9):
    direction = 'right' if i % 2 == 0 else 'left'
    for j in range(9):
        pyautogui.write(sudoku_str[idx],interval=0)
        idx += 1
        if j<8:
            pyautogui.press(direction)
    pyautogui.press('down')




