from inspect import currentframe
from shutil import rmtree
from typing import TypeAlias
from util.util import *
from cfkit.__main__ import problem
from commands import execute_file
File: TypeAlias = str


class test(problem):

  def run_demo(self):
    def read_file(x):
      with open(x, 'r') as file:
        y = file.read()
      return y
    
    def __tmp(x):
      check_path_existence(x, 'f')
      while os.path.isdir(x):
        x = input("The file path you provided is a directory.\nPlease provide the path to a file instead: ")
      return x

    from io import StringIO
    _argv = False
    if path == None and self._path == None: # When the user enter 234A
      self._path = sys.argv[0]
      if not self._path:
        self._path = __tmp(input("Path of the problem file: "))
      else:
        _argv = True

    elif path != None and self._path == None: # When the user enter the path e.g. problems/1234A.py in run_demo function
      self._path = __tmp(path)
    
    elif path == None and self._path != None: # When the user enter the path in test or __init__ functions or leave it empty and the working file is the problem file
      _argv = True

    del path
    dir_name = os.path.dirname(self._path)
    if dir_name == "":
      dir_name = os.getcwd()
      self._path = os.path.join(dir_name, self._path)

    if self._data_path == None: self.extract(dir_name, True, False)
    os.chdir(os.path.join(dir_name, self._data_path))

    L = os.listdir()
    if self._samples_list == None:
      self._samples_list = sorted([file for file in L if re.search(rf"{self._code}_\d.in", file) != None])
      self._expected_output_list = sorted([file for file in L if re.search(rf"{self._code}_\d.out", file) != None])
    verdict = [(None, None)] * len(self._samples_list)
    accepeted = True

    for i in range(len(self._samples_list)):
      test_case = f"{self._code}_test_case{i+1}"

      if _argv: # If working with the solution file itself and it's a python file
        if currentframe().f_back.f_code.co_name == "test":
          line_number = currentframe().f_back.f_back.f_lineno
      
        elif currentframe().f_back.f_code.co_name == "<module>":
          line_number = currentframe().f_back.f_lineno

        with open(self._path) as file:
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
                  
        with open("cfkit_module_user_code.py", 'w') as file:
          file.write("".join(code[:line_number-1] + code[line_number:]))
        execute_file("cfkit_module_user_code.py", self._samples_list[i], test_case)
        os.remove("cfkit_module_user_code.py")         

      else: execute_file(os.path.join(dir_name, self._path), self._path[self._path.rfind(".")+1:]) if self._path.find(system_slash) == -1 else command(self._path, os.path.basename(self._path))

      if False: # Python might not be added to the PATH, or the user may be using an editor or IDE capable of running Python without needing a system-wide installation, such as Thonny.
        input_file = read_file(self._samples_list[i]).strip()

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


      expected = read_file(self._expected_output_list[i])
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

        def tmp(X, Y, Z):
          try:
            for m in range(len(Z)):
              for v in Z[m][1:]:
                Y[m] = float(X[Z[m][0]].split(" ")[v[0]])
            return Y
          except IndexError:
            pass
        def Compare_lists(Y, Z, aux, t=""):
          p = 0 # lines
          ok = True
          while ok and p < l:
            aux = lambda p, j, x: f"wrong answer in {english_ending(p)} line {english_ending(j)} {x} differ - expected: '{a}', found: '{b}'"
            j = 1 # Columns
            while ok and j < len(Z[p]):
              a = Z[p][j][1]
              b = Y[p]
              if a.isdigit() and b.isdigit() or t == "f":
                ok = aux(float(a), float(b))
                if not ok and self._tfwrong == None:
                  self._tfwrong = aux(p, j, "numbers")
              else:
                ok = aux(a, b)
                if not ok and self._tfwrong == None:
                  self._tfwrong = aux(p, j, "words")
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
          if self._fwrong == None: self._fwrong = i + 1

    # Remove samples if accepeted

    if accepeted:
      print("Demo Accepeted")
      l = len(self._samples_list)
      if len(os.listdir()) == len(self._samples_list) * 3:
        rmtree(os.getcwd())
      else:
        def remove_files(file_list):
          for file in file_list:
            os.remove(file)
      
        remove_files(self._samples_list)
        remove_files(self._expected_output_list)
        remove_files([f"{self._code}_test_case{i}.out" for i in range(1, l+1)])
    else:
      print(f"Wrong answer on test {self._fwrong}")
      print(f"Checker log:\n{self._tfwrong}")
      for v in verdict:
        print(f"{v[0]} => {v[1]}")
    
    if _argv and any(code[line_number:]):

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

print(test("4A"))