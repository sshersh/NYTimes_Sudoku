from .SudokuBase import *

class Sudoku1(SudokuBase):
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
