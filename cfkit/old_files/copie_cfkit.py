import sys
import os
import re

from shutil import rmtree
from inspect import currentframe
from requests import get
from bs4 import BeautifulSoup
from typing import TypeAlias
from util.util import *




def print_function_name(func):
  def wrapper(*args, **kwargs):
    print("Executing function:", func.__name__)
    return func(*args, **kwargs)
  return wrapper



if __name__ == "__main__":
  # one = problem("50A")
  # one.run_demo("/home/ghoudiy/Documents/Programming/Python/Competitive_Programming/CodeForces/A_Problems/Optimization/50A_Domino_piling.py")
  # one = contest(1844)
  # one.create_problems_files(os.getcwd(), True)
  # print(problem("1857G").problem_statement())
  pass
