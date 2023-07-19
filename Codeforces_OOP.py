import sys
import os
import re
from shutil import rmtree
from inspect import currentframe
from requests import get
from bs4 import BeautifulSoup
from typing import TypeAlias
File: TypeAlias = str
Directory: TypeAlias = str
FileOrDirectory: TypeAlias = str
ProblemCodeOrFile: TypeAlias = str


class contest:
  def __init__(self, contestId: int) -> None:
    self._id = contestId
    self._check_contest_id(contestId)
    self._content = self.__content_contest()
  

  def __content_contest(self):
    response = get(f"https://codeforces.com/contest/{self._id}")
    response.raise_for_status()
    s = response.text
    s = s[s.find('<td class="id">') + 16:]
    return s[:s.find('</table>')].split("\n")

  @staticmethod
  def _check_contest_id(contestId: int):
    if type(contestId) == int:
      response = get(f"https://codeforces.com/problemset/")
      response.raise_for_status()
      ub = response.text   
      ub = ub[ub.find('<a href="/problemset/problem/') + 29:]
      ub = BeautifulSoup(ub[:ub.find('/')], "html.parser") # Or to the last <script> tag
      if not 1 <= contestId <= int(str(ub)):
        raise SyntaxError(f"invalid contestId '{contestId}'")
    else:
      raise ValueError("contestId must be an integer")

  @staticmethod
  def _define_slash():
    if sys.platform == "win32":
      return "\\"
    else:
      return "/"
  

  @staticmethod
  def _check_path_existence(path, fileOrDir):
    if not os.path.exists(path):
      raise FileNotFoundError(f"No such file: '{path}'" if fileOrDir == "f" else f"No such directory '{path}'")
  
  
  @staticmethod
  def _path_exist_error(path, fileorDir):
    if os.path.exists(path):
      raise FileExistsError(f"File exists '{path}'" if fileorDir == "f" else f"Directory exists '{path}'")

  def create_problems_files(self, path: Directory = os.getcwd(), addProblemNameToFileName: bool = False):
    self._check_path_existence(path, 'd')
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
    self._path_exist_error(f"{self._id}", "d")
    slash = self._define_slash()
    if os.path.basename(path) != self._id:
      os.mkdir(f"{self._id}")
    os.chdir(f"{self._id}")
    S = sorted(S)
    lang = input("Which language you want to code with? ")
    for i, code in enumerate(S):
      letter = code[code.find('/problem/')+9:code.find('"')]
      if addProblemNameToFileName:
        aux = problem._file_name(self, N[i], f"{letter}_") + f".{lang}"
      else:
        aux = letter
      if lang == "py":
        with open(aux, 'a') as file:
          with open(f"{os.path.dirname(__file__)}{slash}python_template.py", 'r') as ff:
            file.write(ff.read())
      else: open(aux, 'x').close()


class problem:
  
  def __init__(self, problem_code: ProblemCodeOrFile) -> None:
    self.__letter_index = None
    self._code = self.__check_entry(problem_code.upper())
    self._content = self.__content()
    self.__pex = self.__search_examples_tag()
    self.__pn = None
    self.name = self._content[0]
    self.__slash = contest._define_slash()
    self.__data_path = None


  def __check_entry(self, problem_code):
    

    def enter_code():
      self._code = input("Please enter the problem code: ")
      self._check_problem_code()


    def __desired(aux):
      c = input(f"'{aux}' Is this the desired problem code? [Y/n]")
      if c == "y" or c == "": return aux
      else: return enter_code()

    is_file = os.path.isfile(problem_code)
    if not is_file:
      self._code = problem_code
      self._check_problem_code()
      return self._code
    elif is_file:
      base_name = os.path.basename(problem_code)
      # Searching for problem code in path
      aux = re.search(r"\A\d{1,4}[A-z]", base_name[:re.search(r"\W", base_name).start()])
      if aux != None: # if the file name contain the problem code
        try:
          aux = aux.group()
          self._check_problem_code(aux)
          code = __desired(aux)
        except SyntaxError:
          print("Problem code couldn't be recognized from the given path")
          code = enter_code()
      else:
        print("Problem code couldn't be recognized from the given path")
        code = enter_code()
      return code
    else:
      raise ValueError("The input is not valid")


  def _check_problem_code(self):
    p = len(self._code) - 1 if self._code[-1].isalpha() and len(re.findall(r"[A-z]", self._code)) == 1 else len(self._code) - 2
    contest._check_contest_id(int(self._code[:p]))      
    response = get(f"https://codeforces.com/problemset/problem/{self._code[:p]}/{self._code[p:]}")
    response.raise_for_status()
    if response.text.find('<div class="problem-statement">') == -1:
      raise SyntaxError(f"invalid problem code '{self._code}")
    self.__letter_index = p


  def __content(self):

    # Problem statement
    response = get(f"https://codeforces.com/problemset/problem/{self._code[:self.__letter_index]}/{self._code[self.__letter_index:]}")
    response.raise_for_status()
    # s = response.text
    s = response.text
    s = s[s.find('class="problem-statement"') + 26:]
    
    p = s.find("</p></div></div>")
    if p != -1: # Note tag
      return [string for string in BeautifulSoup(s[:p], "html.parser").stripped_strings]
    else:
      return [string for string in BeautifulSoup(s[:s.find("</pre></div></div></div>")], "html.parser").stripped_strings]


  def __search_examples_tag(self):
    try:
      return self._content.index("Examples")
    except ValueError:
      return self._content.index("Example")


  def problem_statement(self, saveInFile: bool = False, note: bool = False, examples: bool = False, time_limit: bool = False, memory_limit: bool = False, input_type: bool = False, output_type: bool = False) -> str:
    tmp = lambda x: print(f"{self._content[x]}: {self._content[x+1]}")
      
    if time_limit: tmp(1)
    if memory_limit: tmp(3)
    if input_type: tmp(5)
    if output_type: tmp(7)

    L = self._content[9:]
    # Printing the note and examples
    note_test = True
    if note:
      try:
        self.__pn = self._content.index("Note")
      
        if examples:
          L[self.__pex-9] = "\n\nExamples"
          L[self.__pex-8] = "\nInput\n"
          L[L[self.__pex-8:].index("Output") + (self.__pex - 8)] = "\n\nOutput\n"
          L[self.__pn-9] = "\n\nNote\n"

        elif not examples:
          L[self.__pn-9] = "\n\nNote\n"
          L = L[:self.__pex-9] + L[self.__pn-9:]
      except ValueError:
        note_test = False
    
    elif not note and examples:
      try:
        L = self._content[9:self._content.index("Note")]
      except ValueError:
        L = self._content[9:]
    else:
      L = self._content[9:self.__pex]

    L[L.index("Input")] = "\n\nInput\n"
    L[L.index("Output")] = "\n\nOutput\n"
    L[0] = "\n" + L[0]
    if not note_test:
      L.append("Note section is not available")
    
    if saveInFile:
      path = input("Path to save problem statement text in: ")
      if path == "":
        path = os.getcwd()
      contest._check_path_existence(path, 'd')
      with open(f"{path}{self.__slash}{self._code}.txt", 'w') as file:
        file.write(" ".join(" ".join(L).split("$$$")))
      return f"Problem statement saved in {path}{self.__slash}{self._code}.txt"
    else:
      return " ".join(" ".join(L).split("$$$"))


  def problem_statement_WithDetails(self):
    return self.problem_statement(True, True, True, True, True, True)


  def extract(self, path: Directory = None, CreateTestsDir: bool = True):
    
    if path == None: 
      path = os.getcwd()
    else: 
      contest._check_path_existence(path, 'd')
    
    os.chdir(path)
    
    if self.__pn == None: R = self._content[self.__pex+1:]
    else: R = self._content[self.__pex+1:self.__pn]
    
    nr = R.count("Input")
    aux = nr
    if CreateTestsDir:
  
      def tmp(x): os.mkdir(x); return f"{x}"
      if os.path.exists("tests"):
        Lo = [file for file in os.listdir() if re.search(rf"{self._code}_\d.out", file) != None]
        Li = [file for file in os.listdir() if re.search(rf"{self._code}_\d.in", file) != None]
        if len(Lo) != len(Li):
          c = input("Another folder with the same name already exists\n[W]rite in the same folder or [R]eplace or [C]reate a new one with another name? ").lower()
          while c != 'r' and c != 'c' and c != "w":
            c = input("[W/r/c]")
          if c == 'r' or c == "replace":
            rmtree(f"{path}{self.__slash}tests")
            self.__data_path = tmp("tests")
          elif c == 'c' or c == "create":
            name = input("Folder name: ")
            contest._path_exist_error(name, "d")
            self.__data_path = tmp(name)
          else: self.__data_path = "tests"
        else: self.__data_path = "tests"
      else: self.__data_path = tmp("tests")
    else: self.__data_path = path
    
    while nr > 0:
  
      def in_out_files(nr1, nr2, ext, start, end):
        if not os.path.exists(f"{self.__data_path}{self.__slash}{self._code}_{nr1 - nr2 + 1}.{ext}"):
          with open(f"{self.__data_path}{self.__slash}{self._code}_{nr1 - nr2 + 1}.{ext}", 'w') as ff:
            for data in R[start+1:end]:
              ff.write(f"{data}\n")

      pi = R.index("Input")
      po = R.index("Output")
      in_out_files(aux, nr, "in", pi, po) # in
      R[pi] = "input-done"
      pi = R.index("Input") if "Input" in R else len(R)
      in_out_files(aux, nr, "out", po, pi) # out
      R[po] = "output-done"
      nr -= 1


  def run_demo(self, path: File = sys.argv[0]):
    contest._check_path_existence(path, 'f')

    from io import StringIO
    dir_name = os.path.dirname(path)
    if self.__data_path == None: self.extract(dir_name, True)
    os.chdir(f"{dir_name}{self.__slash}{self.__data_path}")

    Lo = [file for file in os.listdir() if re.search(rf"{self._code}_\d.out", file) != None]
    Li = [file for file in os.listdir() if re.search(rf"{self._code}_\d.in", file) != None]
    verdict = []
    for i in range(len(Li)):
      with open(Li[i], 'r') as file:
        input_file = file.read().strip()

      # Store the original stdin and stdout
      original_stdin = sys.stdin

      saved_stdout = sys.stdout

      try:
        # Create a file-like object from the input string
        input_stream = StringIO(input_file)

        # Replace stdin with the input stream
        sys.stdin = input_stream

        # Create a new stream for capturing the output
        output_stream = sys.stdout = StringIO()

        code = open(path).readlines()[currentframe().f_back.f_lineno:]
        exec("".join(code))
      finally:
          # Restore stdin and stdout to their original values
          sys.stdin = original_stdin

          # Restore the original stdout
          sys.stdout = saved_stdout

      # Write the captured output to .out file
      test_case = f"{self._code}_test_case{i+1}.out"
      with open(test_case, 'w') as file:
        file.write(output_stream.getvalue())

      if open(test_case, 'r').read() == open(Lo[i], 'r').read():
        verdict.append((f"test case {i+1}", "OK"))

      else:
        verdict.append((f"test case {i+1}", "Wrong answer"))

    # Remove samples if all tests passed
    i = 0
    ok = True
    while ok and i < len(verdict):
      ok = verdict[i][1] == "OK"
      i += 1
    if ok:
      print("Demo Accepeted")
      l = len(Li)
      if len(os.listdir()) == len(Li) * 4:
        rmtree(os.getcwd())
      else:
        [os.remove(x) for x in Li]
        [os.remove(x) for x in [f"{self._code}_test_case{i}.in" for i in range(1, l)]]
        [os.remove(x) for x in Lo]
        [os.remove(x) for x in [f"{self._code}_test_case{i}.out" for i in range(1, l)]]
    else:
      print(f"Wrong answer on test {i}")
      for v in verdict:
        print(f"{v[0]} => {v[1]}")
    exit()

  def _file_name(self, name="", code=""):
    if name == "":
      name = self.name[2:]
      code = self._code
    name = re.sub("[A-z]'(s|S)", "s", name)
    name = re.sub(r"\W", "_", name)
    name = re.sub(r"(___|__)", "_", name)
    name = f"{code}{name[:-1]}" if name[-1] == "_" else f"{code}{name}"
    return name

  
  def create_problem_file(self):
    pass


if __name__ == "__main__":
  # one = problem("50A")
  # one.run_demo("/home/ghoudiy/Documents/Programming/Python/Competitive_Programming/CodeForces/A_Problems/Optimization/50A_Domino_piling.py")
  # one = contest(1844)
  # one.create_problems_files(os.getcwd(), True)
  pass
