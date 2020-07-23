import json
import os.path

def get_all(fileName):
    sudokus = []
    with open(fileName+".txt", "r") as f:
        for cnt, line in enumerate(f):
            curSudoku = [[]]
            for num, char in enumerate(line):
                if char == '.':
                    curSudoku[num//9].append(0)
                elif char != '\n':
                    curSudoku[num//9].append(int(char))
                if num%9 == 0 and num != 81:
                    curSudoku.append([])

            curSudoku.pop()
            sudokus.append(curSudoku)
    return sudokus

def convToJSON(fileName):
    if os.path.isfile('./'+fileName+'.json'):
        print("JSON file already exists")
        return

    sudokus = get_all(fileName)
    with open(fileName+".json", "w") as write_file:
        json.dump(sudokus, write_file)

def loadFromJSON(fileName):
    if not os.path.isfile('./'+fileName+'.json'):
        print("JSON file doesn't exist")
        return
    with open(fileName+".json","r") as read_file:
        sudokus = json.load(read_file)

    return sudokus
