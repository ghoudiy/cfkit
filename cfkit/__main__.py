import sys
import os
from re import search, findall
from typing import TypeAlias
from bs4 import BeautifulSoup
from shutil import rmtree

from cfkit.util.util import check_url, check_path_existence, path_exist_error, file_name, problem_code_pattern


Directory: TypeAlias = str
FileOrDirectory: TypeAlias = str
ProblemCodeOrFile: TypeAlias = str
File: TypeAlias = str


class Contest:
  def __init__(self, contestId: int) -> None:
    self._id = contestId
    self._content = self.__contest_content()


  def __contest_content(self):
    if isinstance(self._id, str) and self._id.isdigit():
      self._id = int(self._id)

    if isinstance(self._id, int):
      response = check_url(f"https://codeforces.com/contests/{self._id}", "contests", self._id)
      s = response.text
      s = s[s.find('<td class="id">') + 16:]
      return s[:s.find('</table>')].split("\n")

    print("Contest ID must be an integer")
    sys.exit(1)


  def create_problems_files(self, ext: str, path: Directory = None, addProblemNameToFileName: bool = False) -> None:
    if path is None: path = os.getcwd()
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



class Problem:

  def __init__(self, problem_code: ProblemCodeOrFile = sys.argv[0]) -> None:
    self._letter_index = None
    self._note_index = None
    self._example_index = None
    self._path = None
    self._code = self.__check_entry(problem_code)
    # self._response = self._content()

    # self.name = self._response[0]
    # self.time_limit_s = self._response[2]
    # self.memory_limit_bytes = self.__convert_to_bytes(self._response[4])
    self.memory_limit_bytes = 256000000

    self._data_path = None
    self._expected_output_list = None
    self._input_samples = None
    self._fwrong = None
    self._tfwrong = None


  def _check_problem_code(self, code, err=False):
    if search(problem_code_pattern + r'$', code) is not None:
      p = len(code) - 1 if code[-1].isalpha() and len(findall(r"[A-z]", code)) == 1 else len(code) - 2
      self._response = check_url(f"https://codeforces.com/contest/{code[:p]}/problem/{code[p:]}", "problem code", code, err)
      self._letter_index = p


  def __check_entry(self, problem_code):
    '''
    Check if the problem code is available
    '''

    def enter_code():
      '''If the problem code couldn't be recognized from the given path'''
      self._code = input("Please enter the problem code: ")
      self._check_problem_code(self._code)

    is_file = os.path.isfile(problem_code)
    if not is_file:
      if os.path.isdir(problem_code):
        print("You should enter a problem code or a file not a directory")
        sys.exit(1)

      # self._check_problem_code(problem_code)
      return problem_code

    # Searching for the problem code in path
    base_name = os.path.basename(problem_code)
    problem_code_recognized_from_path = search(problem_code_pattern, base_name[:search(r"\W", base_name).start()])

    if problem_code_recognized_from_path is not None: # if the file name contain the problem code
      try:
        problem_code_recognized_from_path = problem_code_recognized_from_path.group()
        self._check_problem_code(problem_code_recognized_from_path, err=True)
        self._path = problem_code
        return problem_code_recognized_from_path
      
      except SyntaxError:
        pass

    else: # contestId/problem_index -> 1234/a.py
      dir_name = os.path.dirname(problem_code)
      if dir_name.isdigit():
        try:
          self._check_problem_code(dir_name + base_name[0], err=True)
          self._path = problem_code
          return dir_name + base_name[0]
        except SyntaxError:
          pass

    print("Problem code couldn't be recognized from the given path")
    code = enter_code()

    return code


  def _content(self):

    # Problem statement
    s = self._response.text
    s = s[s.find('class="problem-statement"') + 26:]
    p = s.find("</p></div></div>") # Note section tag
    if p != -1:
      problem_statement = list(string for string in BeautifulSoup(s[:p], "html.parser").stripped_strings)
      self._note_index = problem_statement.index("Note")

    else:
      problem_statement = list(string for string in BeautifulSoup(s[:s.find("</pre></div></div></div>")], "html.parser").stripped_strings)

    # Searching for Example section to fetch samples later
    try:
      self._example_index = problem_statement.index("Example")

    except ValueError:

      try:
        print(problem_statement)
        self._example_index = problem_statement.index("Examples")

      except ValueError:
        self._example_index = problem_statement.index("Example(s)")

    return problem_statement

  @staticmethod
  def __convert_to_bytes(memory):
    if not memory.isdigit():
      space = memory.rfind(" ")
      unit = memory[space+1:].lower()
      conversion_factors = {
        "gigabytes": 1E+9,
        "megabytes": 1E+6,
        "kilobytes": 1000,
        "bytes": 1
      }
      if unit in conversion_factors:
        return float(memory[:space]) * conversion_factors[unit]
      else:
        print("Couldn't recognize the memory size")
        sys.exit(1)
    return float(memory)


  def create_problem_file(self, ext: str, addProblemNameToFileName: bool = False, path: Directory = os.getcwd()) -> None:
    file_name(self.name[2:], self._code)


  def parse(self, path: Directory = None, CreateTestsDir: bool = True, __check_path: bool = True) -> None:

    if path is None:
      path = os.getcwd()

    elif path is not None and __check_path:
      check_path_existence(path, 'd')

    os.chdir(path)

    if CreateTestsDir:

      def create_new_dir(x):
        os.mkdir(x)
        return f"{x}"

      if os.path.exists("tests"):
        L = os.listdir("tests")
        self._expected_output_list = sorted([file for file in L if search(rf"{self._code}_\d.out", file) is not None])
        self._input_samples = sorted([file for file in L if search(rf"{self._code}_\d.in", file) is not None])
        print(self._expected_output_list)
        print(L)
        if len(self._expected_output_list) * 2 != len(L):

          c = input("Another folder with the same name already exists\n[W]rite in the same folder or [R]eplace the folder or [C]reate a new one with another name? ").lower()
          while c not in ('w', 'r', 'c'):
            c = input("[W]rite/[R]eplace/[C]reate]").lower()

          if c == 'r':
            rmtree(os.path.join(path, "tests"))
            self._data_path = create_new_dir("tests")

          elif c == 'c':
            name = input("Folder name: ")
            path_exist_error(name, "d")
            self._data_path = create_new_dir(name)

          else: self._data_path = "tests"

        else: self._data_path = "tests"

      else: self._data_path = create_new_dir("tests")

    else: self._data_path = path
    
    # R = self._response[self._example_index+1:] if self._note_index is None else self._response[self._example_index+1:self._note_index]
    # nr = R.count("Input")
    # aux = nr
    # while nr > 0:

    #   def in_out_files(nr1, nr2, ext, start, end):
    #     sample = os.path.join(self._data_path, f"{self._code}_{nr1 - nr2 + 1}.{ext}")
    #     if not os.path.exists(sample):
    #       with open(sample, 'w', encoding="UTF-8") as ff:
    #         for data in R[start+1:end]:
    #           ff.write(f"{data}\n")

    #   pi = R.index("Input")
    #   po = R.index("Output")
    #   in_out_files(aux, nr, "in", pi, po)
    #   R[pi] = "input-done"
    #   pi = R.index("Input") if "Input" in R else len(R)
    #   in_out_files(aux, nr, "out", po, pi)
    #   R[po] = "output-done"
    #   nr -= 1

# Problem("1846D").parse("/home/ghoudiy/Downloads/")