import json
import os.path

def get_all(fileName):
    sudokus = []
    if fileName=="ksudoku16":
        size = 16
    elif fileName =="ksudoku25":
        size = 25
    else:
        size = 9

    with open("TestSudokuFiles/"+fileName+".txt", "r") as f:
            if size > 9:
                for cnt, line in enumerate(f):
                    curSudoku = [[]]
                    buffer = ''
                    curNum = 0
                    prevNum = 0
                    for char in line:
                        if char.isnumeric():
                            buffer += char
                        elif char == '.':
                            curSudoku[curNum//size].append(0)
                        elif char == ',':
                            if buffer:
                                curSudoku[curNum//size].append(int(buffer))
                                buffer = ''
                            curNum += 1
                        if curNum != 0 and curNum != prevNum and curNum%size == 0 and curNum != size**2:
                            curSudoku.append([])
                        prevNum = curNum
                    sudokus.append(curSudoku)
            else:
                for cnt, line in enumerate(f):
                    curSudoku = [[]]
                    for num, char in enumerate(line):
                        if char == '.':
                            curSudoku[num//size].append(0)
                        elif char != '\n':
                            curSudoku[num//size].append(int(char))
                        if num != 0 and num%size == 0 and num != size**2:
                            curSudoku.append([])

                    sudokus.append(curSudoku)
    return sudokus

def convToJSON(fileName):
    if os.path.isfile("TestSudokuFiles/"+fileName+'.json'):
        print("JSON file already exists")
        return

    sudokus = get_all(fileName)
    with open("TestSudokuFiles/"+fileName+".json", "w") as write_file:
        json.dump(sudokus, write_file)

def loadFromJSON(fileName):
    if not os.path.isfile("TestSudokuFiles/"+fileName+'.json'):
        print("JSON file doesn't exist")
        return
    with open("TestSudokuFiles/"+fileName+".json","r") as read_file:
        sudokus = json.load(read_file)

    return sudokus

def checkSoln():
    with open('soln.json','r') as read_file:
        soln = json.load(read_file)

    size = len(soln)
    correctSet = set(range(0, size))
    for row in soln:
        if set(row) != correctSet:
            return False

    for col in range(0, size):
        tempCol = []
        for row in range(0, size):
            tempCol.append(soln[row][col])
        if set(tempCol) != correctSet:
            return False

    return True
