from selenium import webdriver
from contextlib import contextmanager
import time

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

PATH_TO_CHROMEDRIVER = "C:/Users/sam/Anaconda3/pkgs/chromedriver_win32 (1)/chromedriver.exe"

class Kenken:
    def __init__(self):
        self.nyt = [[]]
        self.sudoku = [[]]
        self.knowns = []
        self.unknowns = []
