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


class contest:
  def __init__(self, contestId: int) -> None:
    self._id = contestId
    check_contest_id(contestId)
    self._content = self.__content_contest()
  

  def __content_contest(self):
    response = get(f"https://codeforces.com/contest/{self._id}")
    response.raise_for_status()
    s = response.text
    s = s[s.find('<td class="id">') + 16:]
    return s[:s.find('</table>')].split("\n")


  def create_problems_files(self, ext: str, path: Directory = None, addProblemNameToFileName: bool = False):
    if path == None: path = os.getcwd()
    else: check_path_existence(path, 'd')
    os.chdir(path)
    S = set()
    N = []
    ok = 0
    for line in self._content:
      p = line.find('<a href="/contest/')
      p1 = line.find('!--')
      p2 = line.find("    -->")
      if p != -1 and p1 == -1 and line.find('<img src="') == -1:
        S.add(line[p+19:])
      if ok % 2 == 1:
        name = f"<!-- {line[p2+4:]} -->"
        name = BeautifulSoup(name, "html.parser").stripped_strings
        N.append(next(name))
        ok += 1
      if p1 != -1 and p2 == -1:
        ok += 1
    
    if os.path.basename(path) != self._id:
      os.mkdir(f"{self._id}")
    os.chdir(f"{self._id}")
    S = sorted(S)
    for i, code in enumerate(S):
      letter = code[code.find('/problem/')+9:code.find('"')]
      if addProblemNameToFileName:
        aux = file_name(self, N[i], f"{letter}_") + f".{ext}"
      else:
        aux = letter
      # if ext == "py":
      #   with open(aux, 'a') as file:
      #     with open(os.path.join(os.path.dirname(__file__), "templates", ""), f"{os.path.dirname(__file__)}{}python_template.py", 'r') as ff:
      #       file.write(ff.read())
      # else: open(aux, 'x').close()



class problem:

  def __init__(self, problem_code: ProblemCodeOrFile = sys.argv[0]) -> None:
    self._letter_index = None
    self._index_note = None
    self._example_index = None
    self._path = None
    self._code = self.__check_entry(problem_code)
    self._response = self.__content()
    self.name = self._response[0]
    self.time_limit = self._response[2]
    self.memory_limit = self._response[4]
    self._data_path = None
    self._expected_output_list = None
    self._samples_list = None
    self._fwrong = None
    self._tfwrong = None


  def _check_problem_code(self, code, err=False):
    if re.search(problem_code_pattern + r'$', code) != None:
      p = len(code) - 1 if code[-1].isalpha() and len(re.findall(r"[A-z]", code)) == 1 else len(code) - 2
      check_contest_id(int(code[:p]))      
      response = get(f"https://codeforces.com/contest/{code[:p]}/problem/{code[p:]}")
      response.raise_for_status()
      if response.text.find('<div class="problem-statement">') == -1:
        if err:
          raise SyntaxError
        print(f"invalid problem code '{code}")
        sys.exit(1)
      self._letter_index = p


  def __check_entry(self, problem_code):

    def enter_code():
      self._code = input("Please enter the problem code: ")
      self._check_problem_code(self._code)

    is_file = os.path.isfile(problem_code)
    if not is_file:
      self._check_problem_code(problem_code)
      return problem_code

    else:
      # Searching for the problem code in path
      base_name = os.path.basename(problem_code)
      aux = re.search(problem_code_pattern, base_name[:re.search(r"\W", base_name).start()])

      if aux != None: # if the file name contain the problem code
        try:
          aux = aux.group()
          self._check_problem_code(aux, err=True)
          code = aux
          self._path = problem_code
        except SyntaxError:
          print("Problem code couldn't be recognized from the given path")
          code = enter_code()

      else: # contestId/problem_index -> 1234/a.py
        dir_name = os.path.dirname(problem_code)
        if dir_name.isdigit():
          try:
            check_contest_id(int(dir_name))
            self._check_problem_code(dir_name + base_name[0])
            self._path = problem_code
            return dir_name + base_name[0]
          except SyntaxError:
            pass
        print("Problem code couldn't be recognized from the given path")
        code = enter_code()
     
      return code


  def __content(self):

    # Problem statement
    response = get(f"https://codeforces.com/problemset/problem/{self._code[:self._letter_index]}/{self._code[self._letter_index:]}")
    response.raise_for_status()
    s = response.text
    s = s[s.find('class="problem-statement"') + 26:]
    p = s.find("</p></div></div>") # Note section tag
    if p != -1:
      aux = [string for string in BeautifulSoup(s[:p], "html.parser").stripped_strings]
      self._index_note = aux.index("Note")
   
    else:
      aux = [string for string in BeautifulSoup(s[:s.find("</pre></div></div></div>")], "html.parser").stripped_strings]
   
    try:
      self._example_index = aux.index("Example")
   
    except ValueError:
   
      try:
        self._example_index = aux.index("Examples")
   
      except ValueError:
        self._example_index = aux.index("Example(s)")
   
    return aux


  def create_problem_file(self, ext: str, addProblemNameToFileName: bool = False, path: Directory = os.getcwd()):
    # if 
    file_name(self.name[2:], self._code)
