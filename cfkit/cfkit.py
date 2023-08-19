import sys
import os
import re

from shutil import rmtree
from inspect import currentframe
from requests import get
from bs4 import BeautifulSoup
from typing import TypeAlias

import commands
# import util


File: TypeAlias = str
Directory: TypeAlias = str
FileOrDirectory: TypeAlias = str
ProblemCodeOrFile: TypeAlias = str


def test(path: File = sys.argv[0]):
  if path == "":
    path = input("Problem path: ")
    contest._check_path_existence(path, 'f')
  if os.path.samefile(sys.argv[0], path):
    problem(path).run_demo()
  else:
    contest._check_path_existence(path, 'f')
    problem(path).run_demo()


def print_function_name(func):
  def wrapper(*args, **kwargs):
    print("Executing function:", func.__name__)
    return func(*args, **kwargs)
  return wrapper


class contest:
  @print_function_name
  def __init__(self, contestId: int) -> None:
    self._id = contestId
    self._check_contest_id(contestId)
    self._content = self.__content_contest()
  

  @print_function_name
  def __content_contest(self):
    response = get(f"https://codeforces.com/contest/{self._id}")
    response.raise_for_status()
    s = response.text
    s = s[s.find('<td class="id">') + 16:]
    return s[:s.find('</table>')].split("\n")

  @staticmethod
  @print_function_name
  def _check_contest_id(contestId: int):    
    ok = isinstance(contestId, int)
    if isinstance(contestId, str) and not ok  and contestId.isdigit():
      contestId = int(contestId)
    if ok:
      response = get(f"https://codeforces.com/problemset/")
      response.raise_for_status()
      ub = response.text   
      ub = ub[ub.find('<a href="/problemset/problem/') + 29:]
      ub = BeautifulSoup(ub[:ub.find('/')], "html.parser") # Or to the last <script> tag
      if not 1 <= contestId <= int(str(ub)):
        # raise SyntaxError(f"invalid contestId '{contestId}'")
        print(f"Invalid contestId '{contestId}'")
        sys.exit(1)
    else: 
      # raise ValueError("contestId must be an integer")
        print(f"Contest ID must be an integer")
        sys.exit()
  @staticmethod
  @print_function_name
  def _define_slash():
    if sys.platform == "win32":
      return "\\"
    else:
      return "/"
  

  @staticmethod
  @print_function_name
  def _check_path_existence(path, fileOrDir):
    if not os.path.exists(path):
      # raise FileNotFoundError(f"No such file: '{path}'" if fileOrDir == "f" else f"No such directory '{path}'")
      print(f"No such file: '{path}'" if fileOrDir == 'f' else f"No such directory '{path}'")
      sys.exit(1)
  
  @staticmethod
  @print_function_name
  def _path_exist_error(path, fileorDir):
    if os.path.exists(path):
      # raise FileExistsError(f"File exists '{path}'" if fileorDir == "f" else f"Directory exists '{path}'")
      print(f"File exists '{path}'" if fileorDir == 'f' else f"Directory exists '{path}'")

  @print_function_name
  def create_problems_files(self, ext: str, path: Directory = None, addProblemNameToFileName: bool = False):
    if path == None: path = os.getcwd()
    else: self._check_path_existence(path, 'd')
    os.chdir(path)
    slash = self._define_slash()
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
        aux = problem._file_name(self, N[i], f"{letter}_") + f".{ext}"
      else:
        aux = letter
      if ext == "py":
        with open(aux, 'a') as file:
          with open(f"{os.path.dirname(__file__)}{slash}python_template.py", 'r') as ff:
            file.write(ff.read())
      else: open(aux, 'x').close()


class problem:
  
  @print_function_name
  def __init__(self, problem_code: ProblemCodeOrFile = sys.argv[0]) -> None:
    self.__slash = contest._define_slash()
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


  @print_function_name
  def _check_problem_code(self, code):
    if re.search(r"\A[1-9]{1}\d{,3}[A-z]\d?$", code) != None:
      p = len(code) - 1 if code[-1].isalpha() and len(re.findall(r"[A-z]", code)) == 1 else len(code) - 2
      contest._check_contest_id(int(code[:p]))      
      response = get(f"https://codeforces.com/problemset/problem/{code[:p]}/{code[p:]}")
      response.raise_for_status()
      if response.text.find('<div class="problem-statement">') == -1:
        # raise SyntaxError(f"invalid problem code '{code}")
        print(f"Invalid problem code '{code}'")
        sys.exit(1)
      self.__letter_index = p


  @print_function_name
  def __check_entry(self, problem_code):
    
    @print_function_name
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
          contest._check_contest_id(int(dir_name))
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


  @print_function_name
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


  @print_function_name
  @staticmethod
  def __english_ending(x):
    x %= 100
    if x // 10 == 1:
        return "th"
    if x % 10 == 1:
        return "st"
    if x % 10 == 2:
        return "nd"
    if x % 10 == 3:
        return "rd"
    return "th"


  @print_function_name
  def _file_name(self, name="", code=""):
    if name == "":
      name = self.name[2:]
      code = self._code
    name = re.sub("[A-z]'(s|S)", "s", name)
    name = re.sub(r"\W", "_", name)
    name = re.sub(r"(___|__)", "_", name)
    name = f"{code}{name[:-1]}" if name[-1] == "_" else f"{code}{name}"
    return name


  @print_function_name
  def extract(self, path: Directory = None, CreateTestsDir: bool = True, __check_path: bool = True):

    if path == None: path = os.getcwd()
    elif path != None and __check_path: 
      contest._check_path_existence(path, 'd')

    os.chdir(path)
    
    if CreateTestsDir:
  
      @print_function_name
      def tmp(x): os.mkdir(x); return f"{x}"
      
      if os.path.exists("tests"):
        L = os.listdir("tests")
        self.__Lo = sorted([file for file in L if re.search(rf"{self._code}_\d.out", file) != None])
        self.__Li = sorted([file for file in L if re.search(rf"{self._code}_\d.in", file) != None])
        if len(self.__Lo) != len(self.__Li):
        
          c = input("Another folder with the same name already exists\n\[W]rite in the same folder or [R]eplace the folder or [C]reate a new one with another name? ").lower()
          while c != 'r' and c != 'c' and c != "w":
            c = input("[W/r/c]")
        
          if c == 'r':
            rmtree(f"{path}{self.__slash}tests")
            self.__data_path = tmp("tests")
        
          elif c == 'c':
            name = input("Folder name: ")
            contest._path_exist_error(name, "d")
            self.__data_path = tmp(name)
        
          else: self.__data_path = "tests"
        
        else: self.__data_path = "tests"
      
      else: self.__data_path = tmp("tests")
    
    else: self.__data_path = path

    R = self._content[self.__pex+1:] if self.__pn == None else self._content[self.__pex+1:self.__pn]
    nr = R.count("Input")
    aux = nr
    while nr > 0:
  
      @print_function_name
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


  # @print_function_name
  def run_demo(self, path: File = None):
   
    # @print_function_name
    def read_file(x):
      with open(x, 'r') as file:
        y = file.read()
      return y
    
    # @print_function_name
    def __tmp(x):
      contest._check_path_existence(x, 'f')
      while os.path.isdir(x):
        x = input("The file path you provided is a directory.\nPlease provide the path to a file instead: ")
      return x
  
    from io import StringIO
    _argv = False
    if path == None and self.__path == None: # When the user enter 234A
      self.__path = sys.argv[0]
      if not self.__path:
        self.__path = __tmp(input("Path of the problem file: "))
      else:
        _argv = True
 
    elif path != None and self.__path == None: # When the user enter the path e.g. problems/1234A.py in run_demo function
      self.__path = __tmp(path)
    
    elif path == None and self.__path != None: # When the user enter the path in test or __init__ functions or leave it empty and the working file is the problem file
      _argv = True

    del path
    dir_name = os.path.dirname(self.__path)
    if dir_name == "":
      dir_name = os.getcwd()
      self.__path = f"{dir_name}{self.__slash}{self.__path}"

    if self.__data_path == None: self.extract(dir_name, True, False)
    os.chdir(f"{dir_name}{self.__slash}{self.__data_path}")

    L = os.listdir()
    if self.__Li == None:
      self.__Li = sorted([file for file in L if re.search(rf"{self._code}_\d.in", file) != None])
      self.__Lo = sorted([file for file in L if re.search(rf"{self._code}_\d.out", file) != None])
    verdict = [(None, None)] * len(self.__Li)
    accepeted = True

    for i in range(len(self.__Li)):
      test_case = f"{self._code}_test_case{i+1}.out"

      if _argv: # If working with the solution file itself and it's a python file
        if currentframe().f_back.f_code.co_name == "test":
          line_number = currentframe().f_back.f_back.f_lineno
      
        elif currentframe().f_back.f_code.co_name == "<module>":
          line_number = currentframe().f_back.f_lineno

        with open(self.__path) as file:
          code = file.readlines()
        for j in range(len(code[:line_number-1])):
          pc = code[j].find("cfkit")
          if pc != -1:
            p = code[j].find("import")
            p1 = code[j].find(",")
            if (p != -1 and p1 == -1 or code[j].find("from") != -1):
              code[j] = f"# {code[j]}\n"
            elif p != -1 and p1 != -1: # import math, cfkit
              code[j] = code[j].split(",")
              if code[j][0].find("cfkit") != -1:
                if len(code[j][1:]) > 1:
                  code[j] = f"import {', '.join(code[j][1:])}\n"
                else:
                  code[j] = f"import {code[j][1]}\n"
              else:
                code[j] = list(map(lambda x: x.replace("cfkit", "").strip(), code[j]))
                code[j] = ", ".join(list(filter(lambda x: bool(x), code[j]))) + "\n"
                  
        with open("codeforces_module_user_code.py", 'w') as file:
          file.write("".join(code[:line_number-1] + code[line_number:]))
        executing_command("codeforces_module_user_code.py")
        os.remove("codeforces_module_user_code.py")         

      else: command(f"{dir_name}{self.__slash}{self.__path}", self.__path[self.__path.rfind(".")+1:]) if self.__path.find(self.__slash) == -1 else command(self.__path, os.path.basename(self.__path))

      # if k == -1: # Python might not be added to the PATH, or the user may be using an editor or IDE capable of running Python without needing a system-wide installation, such as Thonny.
      if False: # Python might not be added to the PATH, or the user may be using an editor or IDE capable of running Python without needing a system-wide installation, such as Thonny.
        input_file = read_file(self.__Li[i]).strip()

        # Store the original stdin and stdout
        original_stdin = sys.stdin

        saved_stdout = sys.stdout

        # Create a file-like object from the input string
        input_stream = StringIO(input_file)

        # Replace stdin with the input stream
        sys.stdin = input_stream
        
        # Create a new stream for capturing the output
        output_stream = sys.stdout = StringIO()

        exec(code)

        # Restore stdin and stdout to their original values
        sys.stdin = original_stdin

        # Restore the original stdout
        sys.stdout = saved_stdout

        # Write the captured output to .out file
        with open(test_case, 'w') as file:
          file.write(output_stream.getvalue())

      expected = read_file(self.__Lo[i])
      observed = read_file(test_case)
      if expected == observed:
        verdict[i] = (f"test case {i+1}", "OK")
        accepeted = accepeted and True

      else:
        # In case of results are floating point numbers
        K = expected.split("\n")[:-1]
        tmp = len(K)
        V = [[None, None, None]] * tmp # Float numbers
        F = [[None, None, None]] * tmp # All data except float
        for l in range(len(K)):
          T = K[l].split(' ')
          V[l] = [l]
          F[l] = [l]
          for j in range(len(T)):
            p = T[j].find(".")
            V[l].append((j, T[j])) if p != -1 and (T[j][:p] + T[j][p+1:]).isdigit() else F[l].append((j, T[j]))

        # @print_function_name
        def tmp(X, Y, Z):
          try:
            for m in range(len(Z)):
              for v in Z[m][1:]:
                Y[m] = float(X[Z[m][0]].split(" ")[v[0]])
            return Y
          except IndexError:
            pass
        # @print_function_name
        def Compare_lists(Y, Z, aux, t=""):
          p = 0 # lines
          ok = True
          while ok and p < l:
            aux = lambda p, j, x: f"wrong answer in {self.__english_ending(p)} line {self.__english_ending(j)} {x} differ - expected: '{a}', found: '{b}'"
            j = 1 # Columns
            while ok and j < len(Z[p]):
              a = Z[p][j][1]
              b = Y[p]
              if a.isdigit() and b.isdigit() or t == "f":
                ok = aux(float(a), float(b))
                if not ok and self.__tfwrong == None:
                  self.__tfwrong = aux(p, j, "numbers")
              else:
                ok = aux(a, b)
                if not ok and self.__tfwrong == None:
                  self.__tfwrong = aux(p, j, "words")
              j += 1
            p += 1
          return ok
        K = observed.split("\n")[:-1]
        print(F, "F", "\n", K, "K")
        E = tmp(K, [None] * len(F), F)
        ok = Compare_lists(E, F, lambda a, b: a == b)
        l = len(V)

        if ok and l:
          X = [None] * l
          X = tmp(K, X, V)
          ok = Compare_lists(X, V, lambda a, b: abs(a, b) <= max((1.5E-5 + 1E-15) * max(abs(a), abs(b)), 0), 'f')

        if ok:
          verdict[i] = (f"test case {i+1}", "OK")
          accepeted = accepeted and True
        else:
          accepeted = False
          verdict[i] = (f"test case {i+1}", "Wrong answer")
          if self.__fwrong == None: self.__fwrong = i + 1

    # Remove samples if accepeted
  
    if accepeted:
      print("Demo Accepeted")
      l = len(self.__Li)
      if len(os.listdir()) == len(self.__Li) * 3:
        rmtree(os.getcwd())
      else:
        # @print_function_name
        def remove_files(file_list):
          for file in file_list:
            os.remove(file)
      
        remove_files(self.__Li)
        remove_files(self.__Lo)
        remove_files([f"{self._code}_test_case{i}.out" for i in range(1, l+1)])
    else:
      print(f"Wrong answer on test {self.__fwrong}")
      print(f"Checker log:\n{self.__tfwrong}")
      for v in verdict:
        print(f"{v[0]} => {v[1]}")
    
    if _argv and any(code[line_number:]):

      # @print_function_name
      def tmp():
        sys.stdout = saved_stdout
        sys.stdin = saved_stdin
        c = input("Finish executing the program? [N/y] ").lower()
        if c == "" or c == "n":
          sys.exit(1)
        elif c != "y":
          print("Abort.")
          sys.exit(1)

      try:
        saved_stdin = sys.stdin
        input_stream = sys.stdin = StringIO(None)
        saved_stdout = sys.stdout
        output_stream = sys.stdout = StringIO()
        exec("".join(code[line_number:]))
        if output_stream.getvalue():
          tmp()          
      except EOFError:
        tmp()

  
  # @print_function_name
  def create_problem_file(self, ext: str, addProblemNameToFileName: bool = False, path: Directory = os.getcwd()):
    pass


if __name__ == "__main__":
  # one = problem("50A")
  # one.run_demo("/home/ghoudiy/Documents/Programming/Python/Competitive_Programming/CodeForces/A_Problems/Optimization/50A_Domino_piling.py")
  # one = contest(1844)
  # one.create_problems_files(os.getcwd(), True)
  # print(problem("1857G").problem_statement())
  pass
