"""
Documentation
"""
import sys
import os
from math import isclose
from io import StringIO
from re import search
from inspect import currentframe
from shutil import rmtree
from typing import TypeAlias


from cfkit.problem import Problem
from cfkit.util.util import (
  check_path_existence,
  wrong_answer_verdict,
  read_text_from_file,
  is_number,
  yes_or_no,
  colored_text
)
from util.commands import execute_file
File: TypeAlias = str


class Test(Problem):

  def run_demo(self, file_path: str = None):
    """
    Codeforces Sample Tester: Test a participant's solution against Codeforces problem samples.
    """
    def __tmp(file_path):
      check_path_existence(file_path, 'f')
      while not os.path.isfile(file_path):
        file_path = colored_text(
          "The path you provided is not a file path" +
          "\nPlease provide <user_input_errors>an existing file path</f> instead: ",
          False, False, True
        )
        check_path_existence(file_path, 'f')
      return file_path

    _argv = False

    if (file_path is None) and (self._path is None): # When the user enter 234A
      self._path = sys.argv[0]
      if not self._path:
        self._path = __tmp(input("Path of the problem file: ").strip())

      else:
        # Need to add some features here
        # Search for the problem file in cwd
        _argv = True

    # When the user enter a path (e.g. 1234A.py)
    elif (file_path is not None) and (self._path is None):
      self._path = __tmp(file_path)

    elif (file_path is None) and (self._path is not None):
      # Need to be fix it
      if currentframe().f_back.f_code.co_filename != os.path.join(
        os.path.dirname(__file__), "cli.py"):
        _argv = True

    del file_path

    dir_name = os.path.dirname(self._path)
    if dir_name == "":
      dir_name = os.getcwd()
      self._path = os.path.join(dir_name, self._path)
    del dir_name

    if self._data_path is None:
      self.parse(dir_name, True, False)
    os.chdir(os.path.join(dir_name, self._data_path))

    list_of_files = os.listdir()
    if self._input_samples is None:
      self._input_samples = sorted(
        [file for file in list_of_files if search(rf"{self.code}_\d.in", file) is not None])
      self._expected_output_list = sorted(
        [file for file in list_of_files if search(rf"{self.code}_\d.out", file) is not None])

    number_of_tests = len(self._input_samples)
    verdict = [(None, None)] * number_of_tests
    accepeted = True
    # Loop through samples
    for i, input_sample in enumerate(self._input_samples):
      output_path = f"{self.code}_test_case{i+1}.out"

      if _argv: # If working with the solution file itself and it's a python file
        if currentframe().f_back.f_code.co_name == "test": # Need to be fix it
          line_number = currentframe().f_back.f_back.f_lineno

        elif currentframe().f_back.f_code.co_name == "<module>":
          line_number = currentframe().f_back.f_lineno

        with open(self._path, 'r', encoding="UTF-8") as file:
          code = file.readlines()

        # Change the participant code by remove importing cfkit package line from the code
        for j in range(len(code[:line_number-1])):
          module_position = code[j].find("cfkit")

          if module_position != -1:
            import_keyword_position = code[j].find("import")
            comma_position = code[j].find(",")
            from_keyword_position = code[j].find("from")
            if (import_keyword_position != -1 and import_keyword_position < module_position) and (
              comma_position == -1 or (from_keyword_position != -1 and
                                        from_keyword_position < module_position)):
              code[j] = f"# {code[j]}\n"

            elif import_keyword_position != -1 and comma_position != -1: # import math, cfkit
              code[j] = code[j].split(",")

              if code[j][0].find("cfkit") != -1:

                if len(code[j][1:]) > 1:
                  code[j] = f"import {', '.join(code[j][1:])}\n"

                else:
                  code[j] = f"import {code[j][1]}\n"

              else:
                code[j] = list(map(lambda x: x.replace("cfkit", "").strip(), code[j]))
                code[j] = ", ".join(list(filter(bool, code[j]))) + "\n"

        with open("cfkit_module_user_code.py", 'w', encoding="UTF-8") as file:
          file.write("".join(code[:line_number-1] + code[line_number:]))
        execute_file(
          "cfkit_module_user_code.py",
          input_sample,
          output_path,
          self.memory_limit_bytes
        )
        os.remove("cfkit_module_user_code.py")

      else:
        execute_file(self._path, input_sample, output_path, self.memory_limit_bytes)

      def checker_log(error, err_num, solution_resources, terminal_columns, observed, i):
        if solution_resources == error:
          verdict[i] = (f"Test case {i+1}", colored_text(error, err_num))
          if self._tfwrong is None:
            self._tfwrong = f"{error} on test {i+1}"
          print('-' * terminal_columns)
          if error == "Compilation error":
            print(f"Can't compile file on test {i+1}:\n{observed}\n")
          elif error == "Runtime error":
            print(f"Can't finish executing file on test {i+1}:\n{observed}\n")
          raise InterruptedError

      try:
        terminal_columns = os.get_terminal_size().columns
        observed = read_text_from_file(output_path)
        solution_resources = read_text_from_file(output_path[:-4] + "_memory.out")
        checker_log(
          "Compilation error", "error_1",
          solution_resources,
          terminal_columns,
          observed,
          i
        )
        checker_log(
          "Runtime error",
          "error_2",
          solution_resources,
          terminal_columns,
          observed,
          i
        )
        checker_log(
          "Memory limit exceeded",
          "error_3",
          solution_resources,
          terminal_columns,
          observed,
          i
        )

      except InterruptedError:
        accepeted = False
        continue

      else:
        expected = read_text_from_file(self._expected_output_list[i])
        if expected == observed:
          verdict[i] = (f"Test case {i+1}", colored_text("OK", "correct"))
          accepeted = accepeted and True

        else:
          # In case of results are floating point numbers
          expected = expected.split("\n")[:-1]
          observed = observed.split("\n")[:-1]
          def check_length(line1, line2):
            if len(line1) != len(line2):
              raise InterruptedError

          if True is False: # Option in the terminal to check presentation
            check_length(expected, observed)

          try:
            def compare_values(expected_value, observed_value, line, column):
              if is_number(expected_value) and is_number(observed_value):
                expected_value = float(expected_value)
                observed_value = float(observed_value)
                equal = isclose(expected_value, observed_value, rel_tol=1.5E-5 + 1E-15)
                numbers_or_words = 'numbers'
              else:
                equal = expected_value == observed_value
                numbers_or_words = 'words'

              if not equal:
                self._tfwrong = wrong_answer_verdict(
                  line+1,
                  column+1,
                  numbers_or_words,
                  expected_value,
                  observed_value
                )
                return False
              return True

            data = [[], []] if True else None # Option in the terminal
            equal = False
            for line_number, line_values in enumerate(zip(expected, observed)):
              expected_line = line_values[0].split(' ')
              observed_line = line_values[1].split(' ')
              # Option in the terminal that choose between checking presentation or not
              if True is False:
                check_length(expected_line, observed_line)
                for column_number, column_value in enumerate(zip(expected_line, observed_line)):
                  # column_value[0] is the exepected value and column_value[1] is the observed value
                  equal = compare_values(
                    column_value[0],
                    column_value[1],
                    line_number,
                    column_number
                  )
                  if not equal:
                    break

                if not equal:
                  break
              else:
                data[0].extend(expected_line)
                data[1].extend(observed_line)

            if True: # Option in the terminal to check presentation
              for column, output in enumerate(zip(data[0], data[1])):
                equal = compare_values(output[0], output[1], 0, column)
                if not equal:
                  self._tfwrong = self._tfwrong[:14] + self._tfwrong[
                    self._tfwrong.find(" line ") + 6:]
                  print(self._tfwrong, 123) # Debugging
                  break

          except InterruptedError:
            verdict[i] = (f"Test case {i+1}", colored_text("Presentation error", "error_4"))

          if equal:
            verdict[i] = (f"Test case {i+1}", colored_text("OK", "correct"))
            accepeted = accepeted and True
          else:
            accepeted = False
            verdict[i] = (f"Test case {i+1}", colored_text("Wrong answer", "wrong_answer"))
            self._fwrong = i + 1 if self._fwrong is None else None

    # Remove samples if the solution is accepeted
    def print_results(verdict, solution_resources):
      solution_resources = solution_resources.split("\n")
      for verdict_response in verdict:
        if solution_resources[0] != "Compilation error":
          print(
            f"{verdict_response[0]}, time: {solution_resources[0]}"
            f", memory: {solution_resources[1]}, verdict: {verdict_response[1]}"
          )
        else:
          print(f"{verdict_response[0]}, time: 0s, memory: 0B, verdict: Compilation error")
      print('')

    if accepeted:
      colored_text("Demo Accepeted", "accepted")
      print_results(verdict, solution_resources)
      remove = False
      if len(os.listdir()) == number_of_tests * 4:
        user_choice = yes_or_no(f"Do you want to remove this directory '{os.getcwd()}'")
        if user_choice:
          rmtree(os.getcwd())
        else:
          remove = yes_or_no("Remove samples and output files")

      if remove:
        def remove_files(file_list):
          for file in file_list:
            if isinstance(file, tuple):
              os.remove(file[0])
              os.remove(file[1])
            else:
              os.remove(file)

        remove_files(self._input_samples)
        remove_files(self._expected_output_list)
        remove_files([(f"{self.code}_test_case{i}.out", f"{self.code}_test_case{i}_memory.out"
                       ) for i in range(1, number_of_tests+1)])

    else:
      print(f"Checker log:\n{self._tfwrong}\n")
      print_results(verdict, solution_resources)

    # Ask the user if he wants to finish the program or not
    # If working in the solution file itself
    if _argv and any(code[line_number:]):

      def finish_program():
        sys.stdout = saved_stdout
        sys.stdin = saved_stdin
        user_choice = yes_or_no("Finish executing the program?", "[N/y]")
        if not user_choice:
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

if __name__ == "__main__":
  # print(Test.__dict__)
  # pp = "/home/ghoudiy/Downloads/"
  # os.chdir(pp)
  # Test("code.py").run_demo()
  pass
