from selenium import webdriver
from contextlib import contextmanager
import time

# class to solve and fill in New York Times sudokus
# scrolling or moving mouse excessively can through the solver off track
# must have matching versions of selenium, chromedriver and chrome/chromium installed
# for medium or hard sudokus, initalialize sudoku with "medium" or "hard"
# to turn off solving visualization (much faster), call solve() with quiet=True

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
#options.binary_location = "C:/Program Files (x86)/Google/Chrome Beta/Application"
PATH_TO_CHROMEDRIVER = "C:/Users/sam/Anaconda3/pkgs/chromedriver_win32/chromedriver.exe"

class SudokuNYT:
    def __init__(self,diff):
        """navigates to easy, medium or hard nytimes sudoku and extracts knowns and keypad"""
        self.nyt = [[]]
        self.sudoku = [[]]
        self.unknowns = []
        self.keys = []
        self.cands = [[]]
        self.diff = diff
        # configure chromedriver

    def __enter__(self):
        self.driver = webdriver.Chrome(PATH_TO_CHROMEDRIVER, options = options)
        self.driver.get(r"https://www.nytimes.com/puzzles/sudoku/" + self.diff)

        self.delete = self.driver.find_element_by_css_selector(r"div.su-keyboard div.su-keyboard__delete")
        # open chromedriver and navigate to nytimes sudoku
        self.driver.implicitly_wait(0.1)
        # get the keypad and put into keys list
        keypad = self.driver.find_element_by_css_selector(r"div.su-keyboard__container")
        for nums in range(1,10):
            self.keys.append(keypad.find_element_by_xpath("div[{}]".format(nums)))
        # time to make the board
        board = self.driver.find_element_by_css_selector(r"div.su-board")
        for row in range(0,9):
            for col in range(0,9):
                cur = row*9 + col + 1
                currentCell = board.find_element_by_xpath("div[{}]".format(cur))
                currentVal = currentCell.get_attribute("aria-label")
                if currentVal == "empty":
                    self.sudoku[row].append(0)
                    self.nyt[row].append(currentCell)
                    self.unknowns.append((row,col))
                else:
                    self.nyt[row].append(currentCell)
                    self.sudoku[row].append(int(currentVal))
            if row == 8:
                currentCell.click()
                break
            self.sudoku.append([])
            self.nyt.append([])

        self.numUnknowns = len(self.unknowns)
        # return reference to self for the context manager
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.driver.quit()

    def _isConflict(self,row,col,num):
        """determines if a value is impossible"""
        #important to exclude current index from col (python makes shallow copy)
        sameCol = [self.sudoku[x][col] for x in range(0,9) if x != row]
        sameRow = self.sudoku[row][0:col] + self.sudoku[row][col+1:9]
        #use floor division to find appropriate block
        rowBlock = range(3*(row//3),3*(row//3 + 1))
        colBlock = range(3*(col//3),3*(col//3 + 1))
        sameBlock = [self.sudoku[ii][jj] for ii in rowBlock for jj in colBlock if ii != row or jj != col]

        if num in sameRow or num in sameCol or num in sameBlock:
            return True
        else:
            return False


    def solve(self, quiet=False):
        """driver for guess method"""
        self.quiet = quiet
        endVal = self._guess(0)
        if endVal:
            if self.quiet:
                self._fillSudoku()
            print("Sudoku solved!")
            self.solved = True
        else:
            print("Sudoku not solved.")

    def printSudoku(self):
        """simple utility for printing list to command line.
        Unknowns are marked with an asterisk *"""
        for row in range(0,9):
            for col in range(0,9):
                if (row,col) in self.unknowns and self.sudoku[row][col] != 0:
                    print(self.sudoku[row][col], end = '* ')
                else:
                    print(self.sudoku[row][col], end='  ')
            print("\n")
        print('\n' * 3)

    def _fillNum(self, ind, num):
        """fill in a number in cell specified by ind"""
        self.driver.implicitly_wait(0.01)
        row = self.unknowns[ind][0]
        col = self.unknowns[ind][1]
        self.nyt[row][col].click()
        self.keys[num-1].click()

    def _delNum(self, ind):
        """delete a number in cell specified by ind"""
        if not self.quiet:
            self.driver.implicitly_wait(0.01)
            row = self.unknowns[ind][0]
            col = self.unknowns[ind][1]
            self.nyt[row][col].click()
            self.delete.click()

    def _fillSudoku(self):
        """fill in whole sudoku (for quiet mode)"""
        for ind in range(0, len(self.unknowns)):
            r = self.unknowns[ind][0]
            c = self.unknowns[ind][1]
            self._fillNum(ind, self.sudoku[r][c])
        time.sleep(2)

class SudokuBacktrack(SudokuNYT):
    def _nextNum(self,ind):
        """finds the next valid number for index 'ind' of the unknown squares."""
        r = self.unknowns[ind][0]
        c = self.unknowns[ind][1]
        #if current cell is already 9 and nextNum was called,
        #there's no other number that will work
        if self.sudoku[r][c] == 9:
            self.sudoku[r][c] = 0
            self._delNum(ind)
            return False

        self.sudoku[r][c] += 1
        while self.sudoku[r][c] <= 9:
            if self._isConflict(r, c, self.sudoku[r][c]):
                self.sudoku[r][c] += 1
            else:
                break
        #this means no number satisfying constraints has been found - return False
        if self.sudoku[r][c] == 10:
            #keep with the "0 = unknown" convention, doesn't take much extra time
            self.sudoku[r][c] = 0
            self._delNum(ind)
            return False
        #otherwise, return true
        else:
            if not self.quiet:
                self._fillNum(ind,self.sudoku[r][c])
            return True

    def _guess(self,it):
        """solves the sudoku by backtracking."""
        #in this case the sudoku has been solved
        if it == self.numUnknowns:
           return True
        flag = False
        #guess(n) is called every time guess(n+1) has returned false
        #and _nextNum() can still find numbers that satisfy constraints
        #at index unknowns[n]. If _nextNum(it) returns false, guess(n)
        #returns false and program backtracks to guess(n-1)
        while (not flag) and self._nextNum(it):
            flag = self._guess(it+1)
        return flag

class SudokuHuman(SudokuNYT):
    def __init__(self, diff):
        super().__init__(diff)

    def _nextNum(self):
        pass

    def _guess(self):
        pass

def sudoku(diff="easy",q=False,mode="Backtrack"):
    while(not diff in ["easy","medium","hard"]):
        diff = input("Enter a difficulty ('easy','medium', or 'hard')")

    if (mode=="Backtrack"):
        with SudokuBacktrack(diff) as su:
            su.solve(quiet=q)
    else:
        with SudokuHuman(diff) as su:
            su.solve(quiet=q)
