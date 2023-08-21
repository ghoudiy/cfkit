import sys
import os
import re

from requests import get
from bs4 import BeautifulSoup
from typing import TypeAlias
from util.util import *
Directory: TypeAlias = str
FileOrDirectory: TypeAlias = str
ProblemCodeOrFile: TypeAlias = str
File: TypeAlias = str


class problem:
  
  def __init__(self, problem_code: ProblemCodeOrFile = sys.argv[0]) -> None:
    self.__letter_index = None
    self.__pn = None
    self.__pex = None
    self.__path = None
    self._code = self.__check_entry(problem_code)
    self._content = self.__content()
    self.name = self._content[0]
    self.__data_path = None
    self.__Lo = None
    self.__Li = None
    self.__fwrong = None
    self.__tfwrong = None


  def _check_problem_code(self, code):
    if re.search(r"\A[1-9]{1}\d{,3}[A-z]\d?$", code) != None:
      p = len(code) - 1 if code[-1].isalpha() and len(re.findall(r"[A-z]", code)) == 1 else len(code) - 2
      check_contest_id(int(code[:p]))      
      response = get(f"https://codeforces.com/contest/{code[:p]}/problem/{code[p:]}")
      response.raise_for_status()
      if response.text.find('<div class="problem-statement">') == -1:
        # raise SyntaxError(f"invalid problem code '{code}")
        print(f"Invalid problem code '{code}'")
        sys.exit(1)
      self.__letter_index = p


  def __check_entry(self, problem_code):
    
    def enter_code():
      self._code = input("Please enter the problem code: ")
      self._check_problem_code(self._code)

    # def expected(aux): # Need to be updated
    #   c = input(f"'{aux}' Is this the desired problem code? [Y/n] ")
    #   if c == "" or c == "y": 
    #     return aux
    #   elif c == "n":
    #     return enter_code()

    is_file = os.path.isfile(problem_code)
 
    if not is_file:
      self._check_problem_code(problem_code)
      return problem_code
 
    elif is_file:
      base_name = os.path.basename(problem_code)
      # Searching for problem code in path
      aux = re.search(r"\A[1-9]{1}\d{,3}[A-z]\d?", base_name[:re.search(r"\W", base_name).start()])
 
      if aux != None: # if the file name contain the problem code
        try:
          aux = aux.group()
          self._check_problem_code(aux)
          # code = expected(aux)
          code = aux
          self.__path = problem_code

        except SyntaxError:
          print("Problem code couldn't be recognized from the given path")
          code = enter_code()
      else:
        dir_name = os.path.dirname(problem_code) # 1234/a.py
        if dir_name.isdigit():
          check_contest_id(int(dir_name))
          # code = expected(dir_name + base_name[0])
          code = dir_name + base_name[0]
          self._check_problem_code(code)
          self.__path = problem_code
        else:
          print("Problem code couldn't be recognized from the given path")
          code = enter_code()
      return code
 
    else: 
      # raise ValueError("Please enter the problem code or the problem file correctly")
      print("Please enter the problem code or the problem file correctly")
    sys.exit(1)


  def __content(self):

    # Problem statement
    response = get(f"https://codeforces.com/problemset/problem/{self._code[:self.__letter_index]}/{self._code[self.__letter_index:]}")
    response.raise_for_status()
    s = response.text
    s = s[s.find('class="problem-statement"') + 26:]    
    p = s.find("</p></div></div>") # Note section tag
    if p != -1:
      aux = [string for string in BeautifulSoup(s[:p], "html.parser").stripped_strings]
      self.__pn = aux.index("Note")
    else:
      aux = [string for string in BeautifulSoup(s[:s.find("</pre></div></div></div>")], "html.parser").stripped_strings]
    try:
      self.__pex = aux.index("Examples")
    except ValueError:
      self.__pex = aux.index("Example")
    return aux



  
  def create_problem_file(self, ext: str, addProblemNameToFileName: bool = False, path: Directory = os.getcwd()):
    self._file_name(self.name[2:], self._code)

