from src.Sudoku1 import *
from src.Sudoku2 import *

def sudoku(diff="easy",headless=False,strategy="backtrack"):
    while(not diff in ["easy","medium","hard"]):
        diff = input("Enter a difficulty ('easy','medium', or 'hard')")

    if (strategy=="backtrack"):
        sudoku = Sudoku1(diff,headless)
    else:
        sudoku = Sudoku2(diff,headless)

    with sudoku as su:
        su.solve()
