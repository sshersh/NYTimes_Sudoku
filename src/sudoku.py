from .Sudoku1 import *
from .Sudoku2 import *

def sudoku(diff="easy",input_sudoku=False,headless=False,strategy=1):
    if not input_sudoku:
        while(not diff in ["easy","medium","hard"]):
            diff = input("Enter a difficulty ('easy','medium', or 'hard')")

    strats = {1:Sudoku1, 2:Sudoku2}
    sudoku = strats[strategy]

    with sudoku(diff, input_sudoku, headless) as su:
        su.solve()
