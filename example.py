import suSel as su

# file showing example usage of sudoku solver.
# context manager ensures there are no processes left running after calling sudoku()

# solve an easy sudoku
su.sudoku("easy",True)

# solve a medium sudoku with the quiet setting (dramatically speeds performance)
su.sudoku("medium",True)
