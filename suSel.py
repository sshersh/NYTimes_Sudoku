from selenium import webdriver
import time

# class to extract, solve and fill in nytimes sudoku
# scrolling or moving mouse excessively may interfere with solving process
# must have matching versions of selenium, chromedriver and chrome/chromium installed
# for medium or hard sudokus, initalialize sudoku with "medium" or "hard"
# to mute display of solving process (much faster), call solve() with quiet=True
# to overwrite wrong values instead of deleting them, call solve() with noDelete=True

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

class SudokuNYT:
    def __init__(self, diff="easy"):
        """navigates to easy, medium or hard nytimes sudoku and extracts knowns and keypad"""
        self.nyt = [[]]
        self.sudoku = [[]]
        self.knowns = []
        self.unknowns = []
        self.keys = []
        self.cands = [[]]
        # configure chromedriver

        self.driver = webdriver.Chrome(r"C:\Users\sam\Documents\sudokuProj\chromedriver.exe", options = options)
        self.driver.get(r"https://www.nytimes.com/puzzles/sudoku/" + diff)
        self.delete = self.driver.find_element_by_css_selector(r"div.su-keyboard div.su-keyboard__delete")
        # open chromedriver and navigate to nytimes sudoku
        self.driver.implicitly_wait(5)
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
                    self.knowns.append((row,col))
            if row == 8:
                currentCell.click()
                break
            self.sudoku.append([])
            self.nyt.append([])

    def _isConflict(self,row,col,num):
        """determines if a value is impossible"""
        #important to exclude current index from col (python makes shallow copy)
        sameCol = [self.sudoku[x][col] for x in range(0,9) if x != row]
        sameRow = self.sudoku[row][0:col] + self.sudoku[row][col+1:9]
        #use floor division to find appropriate block
        rowBlock = range(3*(row//3),3*(row//3 + 1))
        colBlock = range(3*(col//3),3*(col//3 + 1))
        block = [self.sudoku[ii][jj] for ii in rowBlock for jj in colBlock if ii != row or jj != col]

        if num in sameRow or num in sameCol or num in block:
            return True
        else:
            return False

    def _nextNum(self,ind):
        """finds the next valid number for index \'ind\' of the unknown squares"""
        r = self.unknowns[ind][0]
        c = self.unknowns[ind][1]
        #if current cell is already 9 and nextNum was called,
        #there's no other number that will work
        if self.sudoku[r][c] == 9:
            self.sudoku[r][c] = 0
            if not self.quiet and not self.noDelete:
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
            self.sudoku[r][c] = 0
            if not self.quiet and not self.noDelete:
                self._delNum(ind)
            return False
        #otherwise, return true
        else:
            if not self.quiet:
                self._fillNum(ind,self.sudoku[r][c])
            return True

    def _guess(self,it):
        """solves the sudoku by recursively backtracking."""
        #in this case the sudoku has been solved
        if it == len(self.unknowns):
           return True
        flag = False
        #guess(n) is called every time guess(n+1) has returned false
        #and _nextNum() can still find numbers that satisfy constraints
        #at index unknowns[n]. Otherwise, guess(n) returns false
        #and program backtracks to guess(n-1)
        while (not flag) and self._nextNum(it):
            flag = self._guess(it+1)
        return flag

    def solve(self, quiet=False, noDelete=False):
        """driver for guess method"""
        self.quiet = quiet
        self.noDelete = noDelete
        endVal = self._guess(0)
        if endVal:
            if self.quiet:
                self._fillSudoku()
            time.sleep(2)
            self.driver.quit()
            # print("Sudoku solved!")
        else:
            print("Sudoku not solved.")

    def printSudoku(self):
        """simple method for printing list to command line (fastest)"""
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
        row = self.unknowns[ind][0]
        col = self.unknowns[ind][1]
        self.nyt[row][col].click()
        self.keys[num-1].click()

    def _delNum(self, ind):
        """delete a number in cell specified by ind"""
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
