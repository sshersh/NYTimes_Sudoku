from selenium import webdriver
import chromedriver_binary
from selenium.common.exceptions import *
from copy import deepcopy
from contextlib import contextmanager
from time import sleep
import sys, traceback
from math import sqrt
import json

# class to solve and fill in New York Times sudokus
# scrolling or moving mouse excessively can throw solver off track
# must have matching versions of selenium, chromedriver and chrome/chromium installed
# for medium or hard sudokus, initalialize sudoku with "medium" or "hard"
# to turn off solving visualization (much faster), call solve() with quiet=True
options = webdriver.ChromeOptions()
options.add_argument('log-level=3')
options.add_argument("start-maximized")

#options.binary_location = "C:/Program Files (x86)/Google/Chrome Beta/Application"
#PATH_TO_CHROMEDRIVER = "C:/Users/sam/Anaconda3/pkgs/chromedriver_win32/chromedriver.exe"
IGNORED_EXCEPTIONS = (KeyboardInterrupt, NoSuchWindowException, ConnectionResetError, SystemExit)

class SudokuBase:
    def __init__(self,diff="easy",input_sudoku=False,headless=True):
        """navigates to easy, medium or hard nytimes sudoku and extracts knowns and keypad"""
        self.nyt = [[]]
        self.unknowns = []
        self.knowns = []
        self.keys = []
        self.from_web = not input_sudoku
        if self.from_web:
            self.sudoku = [[]]
            self.size = 9
        else:
            self.sudoku = input_sudoku
            self.size = len(input_sudoku)
        self.cands = [[]]
        self.diff = diff
        self.headless = headless

        if headless==True and self.from_web:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

    def _fromList(self):
        for row in range(0,self.size):
            for col in range(0,self.size):
                try:
                    if self.sudoku[row][col] == 0:
                        self.unknowns.append((row, col))
                    else:
                        self.knowns.append((row, col))
                except IndexError:
                    print(row," ", col)
                    raise

    def _fromWeb(self):
        self.driver.get(r"https://www.nytimes.com/puzzles/sudoku/" + self.diff)
        self.delete = self.driver.find_element_by_css_selector(r"div.su-keyboard div.su-keyboard__delete")
        # open chromedriver and navigate to nytimes sudoku
        self.driver.implicitly_wait(0.1)
        # get the keypad and put into keys list
        self.keypad = self.driver.find_element_by_css_selector(r"div.su-keyboard__container")
        for nums in range(1,self.size+1):
            self.keys.append(self.keypad.find_element_by_xpath("div[{}]".format(nums)))
        self.board = self.driver.find_element_by_css_selector(r"div.su-board")

        for row in range(0,self.size):
            for col in range(0,self.size):
                cur = row*self.size + col + 1
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
            if row == self.size-1:
                currentCell.click()
                break
            self.sudoku.append([])
            self.nyt.append([])

    def __enter__(self):
        # configure chromedriver
        if self.from_web:
            self.driver = webdriver.Chrome(options = options)
            self._fromWeb()
        else:
            self._fromList()

        self.numUnknowns = len(self.unknowns)
        self.numKnowns = len(self.knowns)
        # return reference to self for the context manager
        return self

    def __exit__(self, exc_type, exc_val, tb):
        if exc_type in IGNORED_EXCEPTIONS:
            print("Manual Override Detected, Closing Processes")
        if self.from_web:
            self.driver.quit()
        # self.printSudoku()
        return isinstance(exc_val, IGNORED_EXCEPTIONS)

    def _findGroup(self, row, col):
        """returns list of indices of cells in same row, column and/or block"""
        #important to exclude current index from col (python makes shallow copy)
        #sameRow and sameCol exclude elements in same block to avoid duplicates
        root = int(sqrt(self.size))
        sameRow = [(row,jj) for jj in range(0,root*(col//root))] + [(row,jj) for jj in range(root*(col//root + 1),self.size)]
        sameCol = [(ii,col) for ii in range(0,root*(row//root))] + [(ii,col) for ii in range(root*(row//root + 1),self.size)]
        sameBlock = [(ii,jj) for ii in range(root*(row//root),root*(row//root + 1)) \
            for jj in range(root*(col//root),root*(col//root + 1)) if ii != row or jj != col]

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
            if self.headless or not self.from_web:
                self.printSudoku()
            else:
                sleep(4)
            print("Sudoku solved!")
            self.solved = True
            #need enough time to hear the victory music
        else:
            print("Sudoku not solved.")
            self.printSudoku()

    def printSudoku(self):
        """simple utility for printing list to command line.
        Unknowns are marked with an asterisk *"""
        with open('soln.json','w') as write_file:
            json.dump(self.sudoku, write_file)

        for row in range(0,self.size):
            for col in range(0,self.size):
                if (row,col) in self.unknowns and self.sudoku[row][col] != 0:
                    print(self.sudoku[row][col], end = '* ')
                else:
                    print(self.sudoku[row][col], end='  ')
            print("\n")
        print('\n' * 3)

    def _fillNum(self, ind):
        """fill in a number in cell specified by ind"""
        if self.from_web and not self.headless:
            self.driver.implicitly_wait(0.01)
            row = self.unknowns[ind][0]
            col = self.unknowns[ind][1]
            self.nyt[row][col].click()
            self.keys[self.sudoku[row][col]-1].click()

    def _delNum(self, ind):
        """delete a number in cell specified by ind"""
        if self.from_web and not self.headless:
            self.driver.implicitly_wait(0.01)
            row = self.unknowns[ind][0]
            col = self.unknowns[ind][1]
            self.nyt[row][col].click()
            self.delete.click()

    # def _fillSudoku(self):
    #     """fill in whole sudoku (for quiet mode)"""
    #     for ind in range(0, len(self.unknowns)):
    #         self._fillNum(ind)
