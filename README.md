# NYTimes_Sudoku

Solving the New York Times Sudoku with Python and Selenium.

## Installation and Usage

Installation is easiest through Anaconda. Uncomment the commented lines in the .yml file if using Windows. Use the following commands:

```console
git clone git@github.com:sshersh/SudokuSolver.git
cd SudokuSolver
conda create env -f sudoku-env.yml
conda activate sudoku-env
```

The visual feature will only work on Chrome. To test functionality in IPython, run: 
```python
from src.sudoku import sudoku
sudoku()
```

A Chrome window should pop up and the program should navigate to the New York Times Sudoku and start filling in squares after a few seconds. The solver can also solve the medium and hard sudokus. The medium sudoku would be solved like so: 
```python
sudoku('hard')
```

If you want to solve without showing steps (much faster) and using the fastest strategy, run:
```python
sudoku('hard', headLess=True, strategy=2)
```

## Strategies

### Strategy \#1

![alt text](https://github.com/sshersh/SudokuSolver/blob/master/sudoku1.gif)

### Strategy \#2

![alt text](https://github.com/sshersh/SudokuSolver/blob/master/sudoku2.gif)
