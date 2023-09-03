import sys
import os
from math import isclose
from io import StringIO
from re import search
from inspect import currentframe
from shutil import rmtree
from typing import TypeAlias


from cfkit.__main__ import Problem
from cfkit.util.util import check_path_existence, english_ending, read_text_from_file, is_number, yesOrNo
from cfkit.commands import execute_file

File: TypeAlias = str


class Test(Problem):


  def run_demo(self, file_path: str = None):

    def __tmp(x):
      check_path_existence(x, 'f')
      while not os.path.isfile(x):
        x = input("The path you provided is not a file path.\nPlease provide an existing file path instead: ")
        check_path_existence(x, 'f')
      return x

    _argv = False

    if (file_path is None) and (self._path is None): # When the user enter 234A
      self._path = sys.argv[0]
      if not self._path:
        self._path = __tmp(input("Path of the problem file: "))

      else:
        # Need to add some features here
        # Search for the problem file cwd
        _argv = True

    elif (file_path is not None) and (self._path is None): # When the user enter a path e.g. 1234A.py
      self._path = __tmp(file_path)

    elif (file_path is None) and (self._path is not None):
      # Need to be fix it
      if currentframe().f_back.f_code.co_filename != os.path.join(os.path.dirname(__file__), "cli.py"):
        _argv = True

    del file_path

    dir_name = os.path.dirname(self._path)
    if dir_name == "":
      dir_name = os.getcwd()
      self._path = os.path.join(dir_name, self._path)

    if self._data_path is None:
      self.parse(dir_name, True, False)
    os.chdir(os.path.join(dir_name, self._data_path))

    L = os.listdir()
    if self._input_samples is None:
      self._input_samples = sorted([file for file in L if search(rf"{self._code}_\d.in", file) is not None])
      self._expected_output_list = sorted([file for file in L if search(rf"{self._code}_\d.out", file) is not None])

    verdict = [(None, None)] * len(self._input_samples)
    accepeted = True
    for i, input_sample in enumerate(self._input_samples):
      output_path = f"{self._code}_test_case{i+1}.out"

      if _argv: # If working with the solution file itself and it's a python file
        if currentframe().f_back.f_code.co_name == "test":
          line_number = currentframe().f_back.f_back.f_lineno

        elif currentframe().f_back.f_code.co_name == "<module>":
          line_number = currentframe().f_back.f_lineno

        with open(self._path, 'r', encoding="UTF-8") as file:
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

        with open("cfkit_module_user_code.py", 'w', encoding="UTF-8") as file:
          file.write("".join(code[:line_number-1] + code[line_number:]))
        execute_file("cfkit_module_user_code.py", input_sample, output_path, self.memory_limit_bytes)
        os.remove("cfkit_module_user_code.py")

      else:
        execute_file(self._path, input_sample, output_path, self.memory_limit_bytes)

      terminal_columns = os.get_terminal_size().columns
      observed = read_text_from_file(output_path)
      memory_usage_execution_time_or_error = read_text_from_file(output_path[:-4] + "_memory.out")

      def checker_log(error):
        if memory_usage_execution_time_or_error == error:
          verdict[i] = (f"Test case {i+1}", error)
          if self._tfwrong is None:
            self._tfwrong = f"{error} on test {i + 1}"
          print('-' * terminal_columns)
          if error == "Compilation error":
            print(f"Can't compile file on test {i+1}:\n{observed}\n")
          elif error == "Runtime error":
            print(f"Can't finish executing file on test {i+1}:\n{observed}\n")
          raise InterruptedError

      try:
        checker_log("Compilation error")
        checker_log("Runtime error")
        checker_log("Memory limit exceeded")

      except InterruptedError:
        accepeted = False
        continue

      else:
        expected = read_text_from_file(self._expected_output_list[i])
        if expected == observed:
          verdict[i] = (f"Test case {i+1}", "OK")
          accepeted = accepeted and True

        else:
          # In case of results are floating point numbers
          expected = expected.split("\n")[:-1]
          observed = observed.split("\n")[:-1]
          def check_length(x, y):
            if len(x) != len(y):
              raise InterruptedError

          if True is False: # Option in the terminal to check presentation
            check_length(expected, observed)
          try:
            def wrong_answer_verdict(line, column, x, a, b):
              '''
              verdict wrong answer message
              '''
              return f"Wrong answer: {line}{english_ending(line)} line {column}{english_ending(column)} {x} differ - expected: '{a}', found: '{b}'" + (f" error = '{(abs(a - b) / a):.3f}'" if x == "numbers" and int(a) == a and int(b) == b else '')

            ok = True
            def compare_values(a, b, line, column):
              if is_number(a) and is_number(b):
                a = float(a)
                b = float(b)
                ok = isclose(a, b, rel_tol=(1.5E-5 + 1E-15))
                t = 'numbers'
              else:
                ok = a == b
                t = 'words'

              if not ok:
                self._tfwrong = wrong_answer_verdict(line+1, column+1, t, a, b)
                return False
              return True

            data = [[], []] if True else None

            for l, values in enumerate(zip(expected, observed)):
              expected_line = values[0].split(' ')
              observed_line = values[1].split(' ')
              if True is False: # Option in the terminal that choose between checking presentation or not
                check_length(expected_line, observed_line)
                for j, column in enumerate(zip(expected_line, observed_line)):
                  ok = compare_values(column[0], column[1], l, j)
                  if not ok:
                    break

                if not ok:
                  break
              else:
                data[0].extend(expected_line)
                data[1].extend(observed_line)

            if True:
              for column, output in enumerate(zip(data[0], data[1])):
                ok = compare_values(output[0], output[1], 0, column)
                if not ok:
                  self._tfwrong = self._tfwrong[:14] + self._tfwrong[23:] # check
                  print(self._tfwrong, 123)
                  break

          except InterruptedError:
            verdict[i] = (f"Test case {i+1}", "Presentation error")

          if ok:
            verdict[i] = (f"Test case {i+1}", "OK")
            accepeted = accepeted and True
          else:
            accepeted = False
            verdict[i] = (f"Test case {i+1}", "Wrong answer")
            if self._fwrong is None:
              self._fwrong = i + 1

    # Remove samples if accepeted
    def print_results(verdict, memory_usage_execution_time_or_error):
      memory_usage_execution_time_or_error = memory_usage_execution_time_or_error.split("\n")
      for v in verdict:
        if memory_usage_execution_time_or_error[0] != "Compilation error":
          print(f"{v[0]}, time: {memory_usage_execution_time_or_error[0]}, memory: {memory_usage_execution_time_or_error[1]}, verdict: {v[1]}")
        else:
          print(f"{v[0]}, time: 0s, memory: 0B, verdict: Compilation error")
      print('')
    if accepeted:
      print("Demo Accepeted")
      print_results(verdict, memory_usage_execution_time_or_error)
      l = len(self._input_samples)
      rm = None
      if len(os.listdir()) == len(self._input_samples) * 4:
        c = yesOrNo(f"Do you want to remove this directory {os.getcwd()}")
        if c == True:
          rmtree(os.getcwd())
        else:
          rm = yesOrNo(f"Remove samples and output files")
      
      if rm:
        def remove_files(file_list):
          for file in file_list:
            if isinstance(file, tuple):
              os.remove(file[0])
              os.remove(file[1])
            else:
              os.remove(file)

        remove_files(self._input_samples)
        remove_files(self._expected_output_list)
        remove_files([(f"{self._code}_test_case{i}.out", f"{self._code}_test_case{i}_memory.out") for i in range(1, l+1)])
     
    else:
      print(f"Checker log:\n{self._tfwrong}\n")
      print_results(verdict, memory_usage_execution_time_or_error)


    # Ask the user if he wants to finish the program or not
    # If working in the solution file itself
    if _argv and any(code[line_number:]):

      def finish_program():
        sys.stdout = saved_stdout
        sys.stdin = saved_stdin
        c = input("Finish executing the program? [N/y] ").lower()
        if c in ('', 'n'):
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
          finish_program()
      except EOFError:
        finish_program()

# Test("200B").run_demo("/home/ghoudiy/Documents/Programming/Python/CP/Codeforces/B_Problems/200B_Drinks.py")
# Test("1846D").run_demo("/home/ghoudiy/Downloads/code.py")
