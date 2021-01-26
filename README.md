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

By default, this strategy is used. It's a simple backtracking algorithm where the squares are guessed linearly in row-major order. This algorithm might take too long to run on medium or hard sudokus since it's the brute force approach. 

![alt text](https://github.com/sshersh/SudokuSolver/blob/master/sudoku2.gif)

Strategy \#1 is implemented in the Sudoku1 class in src/Sudoku1.py.

### Strategy \#2

This algorithm runs when `strategy=2` is input as an argument to the `sudoku` function. Instead of making guesses linearly, the Minimum Remaining Value heuristic was used to decide which square to guess on each iteration. In English, this means that the square with the least number of possible candidates is guessed. This greatly speeds up the solver and allows medium and hard sudokus to be solved quickly (you might have to set `headless=True` because of the lag introduced by the visual feature).  
 
![alt text](https://github.com/sshersh/SudokuSolver/blob/master/sudoku1.gif)

Notice how the solver guesses squares in a nonlinear order but backtracks fewer times. 

There are plenty of faster and more advanced algorithms out there. Feel free to fork this repo and implement one yourself!
