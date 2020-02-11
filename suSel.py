from selenium import webdriver
import time
import sys

# solves and fills in nytimes sudoku
# possible command line arguments:
#   -easy           solve easy nytimes sudoku
#   -medium         solve medium difficulty nytimes sudoku
#   -hard           solve hard nytimes sudoku

if len(sys.argv) == 1:
    url = r"https://www.nytimes.com/puzzles/sudoku/easy"
else:
    diff = sys.argv[1]
    while not diff in ["-easy","-medium","-hard"]:
        diff = input("Specify either '-easy', '-medium' or '-hard'")
    url = r"https://www.nytimes.com/puzzles/sudoku/" + diff[1:]

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(r"C:\Users\sam\Documents\sudokuProj\chromedriver.exe", options = options)
driver.get(url)
delete = driver.find_element_by_css_selector(r"div.su-keyboard div.su-keyboard__delete")

class SudokuNYT:
    def __init__(self):
        self.nyt = [[]]
        self.sudoku = [[]]
        self.knowns = []
        self.unknowns = []
        self.keys = []
        # configure chromedriver


        # open chromedriver and navigate to nytimes sudoku
        driver.implicitly_wait(5)
        # get the keypad and put into keys list
        keypad = driver.find_element_by_css_selector(r"div.su-keyboard")
        cssString = "div.su-keyboard__number"
        for nums in range(0,9):
            self.keys.append(keypad.find_element_by_css_selector(cssString))
            cssString += "+div"
        # time to make the board
        board = driver.find_element_by_css_selector(r"div.su-board")
        cssString = "div"
        for row in range(0,9):
            for col in range(0,9):
                currentCell = board.find_element_by_css_selector(cssString)
                currentVal = currentCell.get_attribute("aria-label")
                if currentVal == "empty":
                    self.sudoku[row].append(0)
                    self.nyt[row].append(currentCell)
                    self.unknowns.append((row,col))
                else:
                    self.nyt[row].append(currentCell)
                    self.sudoku[row].append(int(currentVal))
                    self.knowns.append((row,col))
                cssString += "+div"
            if row == 8:
                break
            self.sudoku.append([])
            self.nyt.append([])


    def _nextNum(self,ind):
        """finds the next valid number for index \'ind\' of the unknown squares"""
        r = self.unknowns[ind][0]
        c = self.unknowns[ind][1]
        #if current cell is already 9 and nextNum was called,
        #there's no other number that will work
        if self.sudoku[r][c] == 9:
            self.sudoku[r][c] = 0
            self.delNum(ind)
            return False
        #important to exclude current index from col (python makes shallow copy)
        col = [self.sudoku[x][c] for x in range(0,9) if x != r]
        row = self.sudoku[r][0:c] + self.sudoku[r][c+1:9]
        #use floor division to find appropriate block
        rowBlock = range(3*(r//3),3*(r//3 + 1))
        colBlock = range(3*(c//3),3*(c//3 + 1))
        block = [self.sudoku[ii][jj] for ii in rowBlock for jj in colBlock if ii != r or jj != c]

        self.sudoku[r][c] += 1
        while self.sudoku[r][c] <= 9:
            #check if current index is in current block, row and col
            #if so, increase sudoku[r][c] and repeat until suitable number found
            #or no number found
            if self.sudoku[r][c] in block:
                self.sudoku[r][c] += 1
            elif self.sudoku[r][c] in row:
                self.sudoku[r][c] += 1
            elif self.sudoku[r][c] in col:
                self.sudoku[r][c] += 1
            else:
                break
        #this means no number satisfying constraints has been found - return False
        if self.sudoku[r][c] == 10:
            self.sudoku[r][c] = 0
            self.delNum(ind)
            return False
        #otherwise, return true
        else:
            self.fillNum(ind,self.sudoku[r][c])
            return True

    def _guess(self,it):
        """recursively solves the sudoku by backtracking."""
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

    def solve(self):
        """driver for guess method"""
        endVal = self._guess(0)
        if endVal:
            time.sleep(2)
            # print("Sudoku solved!")
        else:
            print("Sudoku not solved.")

    def printSudoku(self):
        for row in range(0,9):
            for col in range(0,9):
                if (row,col) in self.unknowns and self.sudoku[row][col] != 0:
                    print(self.sudoku[row][col], end = '* ')
                else:
                    print(self.sudoku[row][col], end='  ')
            print("\n")
        print('\n' * 3)

    def fillNum(self, ind, num):
        driver.implicitly_wait(0.1)
        row = self.unknowns[ind][0]
        col = self.unknowns[ind][1]
        if not ind == 0:
            self.nyt[row][col].click()
        driver.implicitly_wait(0.1)
        self.keys[num-1].click()

    def delNum(self, ind):
        row = self.unknowns[ind][0]
        col = self.unknowns[ind][1]
        driver.implicitly_wait(0.1)
        self.nyt[row][col].click()
        delete.click()

    # def fillSudoku(self):
    #     for ind in self.unknowns:
    #         r = ind[0]
    #         c = ind[1]
    #         self.fillNum(r,c,self.sudoku[r][c])
    #     time.sleep(2)

s = SudokuNYT()
s.solve()
driver.quit()
