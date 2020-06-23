from selenium import webdriver
from selenium.common.exceptions import *
from copy import deepcopy
from contextlib import contextmanager
from time import sleep
import sys, traceback

# class to solve and fill in New York Times sudokus
# scrolling or moving mouse excessively can through the solver off track
# must have matching versions of selenium, chromedriver and chrome/chromium installed
# for medium or hard sudokus, initalialize sudoku with "medium" or "hard"
# to turn off solving visualization (much faster), call solve() with quiet=True

options = webdriver.ChromeOptions()
options.add_argument('log-level=3')

#options.binary_location = "C:/Program Files (x86)/Google/Chrome Beta/Application"
PATH_TO_CHROMEDRIVER = "C:/Users/sam/Anaconda3/pkgs/chromedriver_win32/chromedriver.exe"
IGNORED_EXCEPTIONS = (KeyboardInterrupt, NoSuchWindowException, ConnectionResetError, SystemExit)

class SudokuNYT:
    def __init__(self,diff,headless):
        """navigates to easy, medium or hard nytimes sudoku and extracts knowns and keypad"""
        self.nyt = [[]]
        self.sudoku = [[]]
        self.unknowns = []
        self.knowns = []
        self.keys = []
        self.cands = [[]]
        self.diff = diff
        self.headless = headless
        if headless==True:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

    def _fromFile(self):
        self.driver.get("file:///%USERPROFILE%/Anaconda3/NYTimes_Sudoku/Sudoku_6-23/easy.html")

    def _fromWeb(self):
        self.driver.get(r"https://www.nytimes.com/puzzles/sudoku/" + self.diff)
        self.delete = self.driver.find_element_by_css_selector(r"div.su-keyboard div.su-keyboard__delete")
        # open chromedriver and navigate to nytimes sudoku
        self.driver.implicitly_wait(0.1)
        # get the keypad and put into keys list
        self.keypad = self.driver.find_element_by_css_selector(r"div.su-keyboard__container")
        for nums in range(1,10):
            self.keys.append(self.keypad.find_element_by_xpath("div[{}]".format(nums)))
        self.board = self.driver.find_element_by_css_selector(r"div.su-board")

    def __enter__(self):
        # configure chromedriver
        self.driver = webdriver.Chrome(PATH_TO_CHROMEDRIVER, options = options)

        self._fromWeb()

        for row in range(0,9):
            for col in range(0,9):
                cur = row*9 + col + 1
                currentCell = self.board.find_element_by_xpath("div[{}]".format(cur))
                currentVal = currentCell.get_attribute("aria-label")
                if currentVal == "empty":
                    self.sudoku[row].append(0)
                    self.nyt[row].append(currentCell)
                    self.unknowns.append((row,col))
                else:
                    self.nyt[row].append(currentCell)
                    self.sudoku[row].append(int(currentVal))
                    self.knowns.append((row,col))
            #janky trick to center the grid on the page
            if row == 8:
                currentCell.click()
                break
            self.sudoku.append([])
            self.nyt.append([])

        self.numUnknowns = len(self.unknowns)
        self.numKnowns = len(self.knowns)
        # return reference to self for the context manager
        return self

    def __exit__(self, exc_type, exc_val, tb):
        if exc_type in IGNORED_EXCEPTIONS:
            print("Manual Override Detected, Closing Processes")
        self.driver.quit()
        # self.printSudoku()
        return isinstance(exc_val, IGNORED_EXCEPTIONS)

    def _findGroup(self, row, col):
        """returns list of indices of cells in same row, column and/or block"""
        #important to exclude current index from col (python makes shallow copy)
        #sameRow and sameCol exclude elements in same block to avoid duplicates
        sameRow = [(row,jj) for jj in range(0,3*(col//3))] + [(row,jj) for jj in range(3*(col//3 + 1),9)]
        sameCol = [(ii,col) for ii in range(0,3*(row//3))] + [(ii,col) for ii in range(3*(row//3 + 1),9)]
        sameBlock = [(ii,jj) for ii in range(3*(row//3),3*(row//3 + 1)) \
            for jj in range(3*(col//3),3*(col//3 + 1)) if ii != row or jj != col]

        return sameRow + sameCol + sameBlock

    def _isConflict(self,row,col,num):
        """determines if a value in sudoku[row][col] is allowed"""
        vals = [self.sudoku[ii][jj] for (ii,jj) in self._findGroup(row,col)]
        # if num in sameRow or num in sameCol or num in sameBlock:
        if num in vals:
            return True
        else:
            return False

    def solve(self):
        """High level program flow method"""
        endVal = self._guessDriver()
        if endVal:
            if self.headless:
                self.printSudoku()
            print("Sudoku solved!")
            self.solved = True
            #need enough time to hear the victory music
            sleep(4)
        else:
            print("Sudoku not solved.")
            self.printSudoku()

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

    def _fillNum(self, ind):
        """fill in a number in cell specified by ind"""
        if not self.headless:
            self.driver.implicitly_wait(0.01)
            row = self.unknowns[ind][0]
            col = self.unknowns[ind][1]
            self.nyt[row][col].click()
            self.keys[self.sudoku[row][col]-1].click()

    def _delNum(self, ind):
        """delete a number in cell specified by ind"""
        if not self.headless:
            self.driver.implicitly_wait(0.01)
            row = self.unknowns[ind][0]
            col = self.unknowns[ind][1]
            self.nyt[row][col].click()
            self.delete.click()

    # def _fillSudoku(self):
    #     """fill in whole sudoku (for quiet mode)"""
    #     for ind in range(0, len(self.unknowns)):
    #         self._fillNum(ind)

class Sudoku1(SudokuNYT):
    def _nextNum(self,ind):
        """finds the next valid number for index 'ind' of the unknown squares."""
        r = self.unknowns[ind][0]
        c = self.unknowns[ind][1]

        tempGuess = self.sudoku[r][c]
        #if current cell is already 9 and nextNum was called,
        #there's no other number that will work
        if tempGuess == 9:
            self.sudoku[r][c] = 0
            self._delNum(ind)
            return False

        tempGuess += 1
        while tempGuess <= 9:
            if self._isConflict(r, c, tempGuess):
                tempGuess += 1
            else:
                break
        #this means no number satisfying constraints has been found - return False
        if tempGuess == 10:
            #keep with the "0 = unknown" convention
            self.sudoku[r][c] = 0
            self._delNum(ind)
            return False
        #otherwise, fill in sudoku[r][c] and return true
        else:
            self.sudoku[r][c] = tempGuess
            self._fillNum(ind)
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

    def _guessDriver(self):
        """driver for guess method"""
        return self._guess(0)

class Sudoku2(SudokuNYT):
    def __init__(self, diff, headless):
        super().__init__(diff, headless)
        self.cands = [[]]
        self.numGuesses = 0

    def __enter__(self):
        super().__enter__()
        fullList = [i for i in range(1,10)]

        ind = self.knowns[0]
        start = 0
        for row in range(0,9):
            for col in range(0,9):
                if (row, col) != ind:
                    self.cands[row].append(deepcopy(fullList))
                else:
                    start += 1
                    if start < self.numKnowns:
                        ind = self.knowns[start]
                    self.cands[row].append([0])
            if row != 8:
                self.cands.append([])


        for ii in range(0, self.numKnowns):
            self._updateCands(self.cands,(self.knowns[ii][0],self.knowns[ii][1]))

        return self

    def _updateCands(self,cands,ind):
        """Updates the local candidate list for each cell and returns
        the cell with shortest list.
        Input argument is the index the cell (row, col)"""

        r, c = ind
        num = self.sudoku[r][c]
        #shortest candidate list
        min = 9
        #index of shortest candidate list
        minInd = (9,9)
        for (ii, jj) in self._findGroup(r, c):
            #Since this is a deep inner loop, handling the "ValueError" produced
            #by remove() when num isn't in a list should be quicker than
            #checking for num before deleting it
            try:
                cands[ii][jj].remove(num)
            except ValueError:
                pass

            l = len(cands[ii][jj])

            #If l == 0 then backtrack, if 1st element is 0 then it is known
            if l != 0:
                if cands[ii][jj][0] != 0 and l < min:
                    min = l
                    minInd = (ii, jj)
            else:
                #return impossible index so caller knows to backtrack
                return (9,9)

        #Update the candidate list for the chosen cell
        return minInd

    def _guess(self,cands,ind=(0,0)):
        """Recursive guesser method. Input args are a (deep) copy of candidate
        list and index of last guess."""
        if self.numGuesses == self.numUnknowns:
            return True
        #set the candidate list of last guess to 0
        cands[ind[0]][ind[1]] = [0]
        #find the cell with shortest candidate list
        minInd = self._updateCands(cands,ind)
        if minInd == (9,9):
            return False
        r, c = minInd
        for curGuess in cands[r][c]:
            self.sudoku[r][c] = curGuess
            self.numGuesses += 1
            if self._guess(deepcopy(cands), minInd):
                return True
            self.numGuesses -= 1
        self.sudoku[r][c] = 0
        return False

    def _guessDriver(self):
        return self._guess(self.cands)

def sudoku(diff="easy",headless=False,strategy="backtrack"):
    while(not diff in ["easy","medium","hard"]):
        diff = input("Enter a difficulty ('easy','medium', or 'hard')")

    if (strategy=="backtrack"):
        sudoku = Sudoku1(diff,headless)
    else:
        sudoku = Sudoku2(diff,headless)

    with sudoku as su:
        su.solve()
