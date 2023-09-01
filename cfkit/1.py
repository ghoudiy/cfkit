import sys
import os
from io import StringIO
from re import search
from inspect import currentframe
from shutil import rmtree
from typing import TypeAlias


from cfkit.__main__ import Problem
from cfkit.util.util import check_path_existence, english_ending, read_text_from_file, is_number
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
        execute_file("cfkit_module_user_code.py", input_sample, output_path, self.memory_limit_bytes, f"test {i + 1}")
        os.remove("cfkit_module_user_code.py")

      else:
        execute_file(self._path, input_sample, output_path, self.memory_limit_bytes, f"test {i + 1}")

      expected = read_text_from_file(self._expected_output_list[i])
      observed = read_text_from_file(output_path)
      if expected == observed:
        verdict[i] = (f"test case {i+1}", "OK")
        accepeted = accepeted and True

      else:
        # In case of results are floating point numbers
        expected = expected.split("\n")[:-1]
        expected_val_length = len(expected)
        expected_floating_pt_numbers_values = [[] for _ in range(expected_val_length)]
        expected_string_integers_values = [[] for _ in range(expected_val_length)]

        for l, expected_values in enumerate(expected):
          line = expected_values.split(' ')

          for j, column in enumerate(line):
            p = column.find(".")
            if p != -1 and (column[:p] + column[p+1:]).isdigit():
              expected_floating_pt_numbers_values[l].append((j, column))

            else:
              expected_string_integers_values[l].append((j, column))
        print(f"{expected_floating_pt_numbers_values = }")
        print(f"{expected_string_integers_values = }")
        print('=' * 50)
        def check_presentation_error(observed_values, empty_list_for_observed_values, expected_values):
          try:
            if any(expected_values) != any(observed_values):
              raise IndexError
            else:
              for m, line in enumerate(expected_values):
                R = observed_values[m].split(" ")
                if len(R) == len(line):
                  for column in line:
                    empty_list_for_observed_values[m].append(R[column[0]])
                else:
                  raise IndexError
              return empty_list_for_observed_values

          except IndexError:
            verdict[i] = (f"test case {i+1}", "Presentation error")

        def compare_lists(observed_values, expected_values, func, t=""):
          '''
          Compare expected values and observed values
          '''
          def wrong_answer_verdict(line, column, x):
            '''
            verdict wrong answer message
            '''
            return f"Wrong answer: {line}{english_ending(line)} line {column}{english_ending(column)} {x} differ - expected: '{a}', found: '{b}'"

          line_number = 0
          ok = True
          while ok and line_number < len(expected_values):

            column_number = 0 # Columns
            while ok and column_number < len(expected_values[line_number]):

              a = expected_values[line_number][column_number][1]
              b = observed_values[line_number][column_number]

              if is_number(a) and is_number(b) or t == "f":
                ok = func(float(a), float(b))
                if not ok and self._tfwrong is None:
                  self._tfwrong = wrong_answer_verdict(line_number+1, column_number+1, "numbers")

              else:
                ok = func(a, b)

                if not ok and self._tfwrong is None:
                  self._tfwrong = wrong_answer_verdict(line_number+1, column_number+1, "words")

              column_number += 1
            line_number += 1
          return ok

        def check_verdict():
          if verdict[i][1] == "Presentation error":
            raise InterruptedError
       
        observed = observed.split("\n")[:-1]
        observed_strings_integers_values = check_presentation_error(observed, [[] for _ in range(len(expected_string_integers_values))], expected_string_integers_values)
        try:
          check_verdict()
        except InterruptedError:
          print(verdict)
          continue
        ok = compare_lists(observed_strings_integers_values, expected_string_integers_values, lambda a, b: a == b)
        floating_pt_numbers_values_list_length = len(expected_floating_pt_numbers_values)

        if ok and floating_pt_numbers_values_list_length:
          observed_floating_pt_numbers = check_presentation_error(observed, [[] for _ in range(floating_pt_numbers_values_list_length)], expected_floating_pt_numbers_values)
          try:
            check_verdict()
          except InterruptedError:
            continue
          ok = compare_lists(observed_floating_pt_numbers, expected_floating_pt_numbers_values, lambda a, b: abs(a - b) <= max((1.5E-5 + 1E-15) * max(abs(a), abs(b)), 0), 'f')
          print(f"{observed_floating_pt_numbers = }")
          print(f"{ok = }")

        if ok:
          verdict[i] = (f"test case {i+1}", "OK")
          accepeted = accepeted and True
        else:
          accepeted = False
          verdict[i] = (f"test case {i+1}", "Wrong answer")
          if self._fwrong is None:
            self._fwrong = i + 1
    exit()
    # Remove samples if accepeted
    if accepeted:
      print("Demo Accepeted")
      l = len(self._input_samples)
      print(os.listdir())
      if len(os.listdir()) == len(self._input_samples) * 3:
        rmtree(os.getcwd())
      else:
        def remove_files(file_list):
          for file in file_list:
            os.remove(file)

        remove_files(self._input_samples)
        remove_files(self._expected_output_list)
        remove_files([f"{self._code}_test_case{i}.out" for i in range(1, l+1)])
    else:
      print(f"Wrong answer on test {self._fwrong}")
      print(f"Checker log:\n{self._tfwrong}")
      for v in verdict:
        print(f"{v[0]} => {v[1]}")

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