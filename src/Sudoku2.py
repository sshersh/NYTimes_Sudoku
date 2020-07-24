from .SudokuBase import *

class Sudoku2(SudokuBase):
    def __init__(self, diff="easy", input_sudoku=[[]], headless=True):
        super().__init__(diff, input_sudoku, headless)
        self.cands = [[]]
        self.numGuesses = 0

    def __enter__(self):
        super().__enter__()
        fullList = [i for i in range(1,self.size+1)]

        ind = self.knowns[0]
        start = 0
        for row in range(0,self.size):
            for col in range(0,self.size):
                if (row, col) != ind:
                    self.cands[row].append(deepcopy(fullList))
                else:
                    start += 1
                    if start < self.numKnowns:
                        ind = self.knowns[start]
                    self.cands[row].append([0])
            if row != self.size-1:
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
        group = self._findGroup(r, c)

        for (row, col) in group:
            #Since this is a deep inner loop, handling the "ValueError" produced
            #by remove() when num isn't in a list should be quicker than
            #checking for num before deleting it
            try:
                cands[row][col].remove(num)
            except ValueError:
                pass

        #shortest candidate list
        min = self.size
        #index of shortest candidate list
        minInd = (self.size,self.size)
        for (row, col) in group:
                l = len(cands[row][col])
                #If l == 0 then backtrack, if 1st element is 0 then it is known
                if cands[row][col] != [0]:
                    if l == 1:
                        minInd = (row, col)
                        return minInd
                    if l == 0:
                        #return impossible index so caller knows to backtrack
                        return (self.size,self.size)
                    else:
                        if l < min:
                            min = l
                            minInd = (row, col)

        #case in which all cells in group are known but there is another minimum
        if minInd == (self.size,self.size):
            allInds = [(ii,jj) for ii in range(0,self.size) for jj in range(0,self.size)]
            #later make more efficient: possible only have to check for 1 item
            for (ii,jj) in allInds:
                if cands[ii][jj] != [0] and l < min:
                    min = l
                    minInd = (ii, jj)
        #Update the candidate list for the chosen cell
        return minInd

    def _guess(self,cands,ind):
        """Recursive guesser method. Input args are a (deep) copy of candidate
        list and index of last guess."""
        if self.numGuesses == self.numUnknowns:
            return True
        #set the candidate list of last guess to 0
        cands[ind[0]][ind[1]] = [0]
        #find the cell with shortest candidate list
        minInd = self._updateCands(cands,ind)
        # print(f"minInd: {minInd}", end = "\n")
        # print(cands)
        if minInd == (self.size,self.size):
            return False
        r, c = minInd
        for curGuess in cands[r][c]:
            self.sudoku[r][c] = curGuess
            self._fillNum(minInd)
            self.numGuesses += 1
            if self._guess(deepcopy(cands), minInd):
                return True
            self.numGuesses -= 1
        self.sudoku[r][c] = 0
        self._delNum(minInd)
        return False

    def _guessDriver(self):
        # firstInd = self.knowns[0]
        # return self._guess(self.cands, firstInd)
        #
        minInd = self.unknowns[0]
        minLen = 10
        for (row, col) in self.unknowns:
            if len(self.cands[row][col]) == 1:
                minInd = (row, col)
                break
            if len(self.cands[row][col]) < minLen:
                minInd = (row, col)

        r, c = minInd
        for curGuess in self.cands[r][c]:
            self.sudoku[r][c] = curGuess
            self._fillNum(minInd)
            self.numGuesses += 1
            if self._guess(deepcopy(self.cands), minInd):
                return True
            self.numGuesses -= 1
        self.sudoku[r][c] = 0
        self._delNum(minInd)
        return False


    def _fillNum(self, ind):
        """fill in a number in cell specified by ind"""
        if not self.headless:
            self.driver.implicitly_wait(0.01)
            row, col = ind
            self.nyt[row][col].click()
            self.keys[self.sudoku[row][col]-1].click()

    def _delNum(self, ind):
        """delete a number in cell specified by ind"""
        if not self.headless:
            self.driver.implicitly_wait(0.01)
            row, col = ind
            self.nyt[row][col].click()
            self.delete.click()
