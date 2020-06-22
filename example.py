from suSel import *

# file showing example usage of sudoku solver.
# context manager ensures there are no processes left running after calling sudoku()

# solve an easy sudoku
sudoku("easy")

# solve a medium sudoku with the quiet setting (dramatically speeds performance)
sudoku("medium",True)
