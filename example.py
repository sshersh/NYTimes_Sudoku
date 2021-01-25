from src import *
# file showing example usage of sudoku solver.
# context manager ensures there are no processes left running after calling sudoku()

# solve an easy sudoku
# sudoku("hard",headless=True,strategy=2)
# sudokus = loadFromJSON("ksudoku16")
# numPuzzles = 5

sudoku('easy',headless=False,strategy=2)

# if checkSoln():
#     print("Soln correct")
# else:
#     print("Soln incorrect")
# solve a medium sudoku with the quiet setting (dramatically speeds performance)
# sudoku("medium",True)
