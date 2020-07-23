from src import *
# file showing example usage of sudoku solver.
# context manager ensures there are no processes left running after calling sudoku()

# solve an easy sudoku
# sudoku("hard",headless=True,strategy=2)
sudokus = loadFromJSON("top1465")

sudoku(input_sudoku=sudokus[0], strategy=1)
# solve a medium sudoku with the quiet setting (dramatically speeds performance)
# sudoku("medium",True)
