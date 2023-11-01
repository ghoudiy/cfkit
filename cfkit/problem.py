"""
Documentation
"""
import sys
import os
from math import isclose
from pathlib import Path
from subprocess import run, PIPE, CalledProcessError
from re import search, findall
from datetime import datetime
from inspect import currentframe
from shutil import rmtree
from typing import TypeAlias, NoReturn

from cfkit.util.common import (
  get_response,
  check_path_existence,
  file_name,
  write_text_to_file,
  colored_text,
  convert_to_bytes,
  create_file_folder,
  # folder_file_exists,
  retrieve_template,
  # display_horizontally,
  # enter_number,
  write_json_file,
  samples_dir,
  read_text_from_file,
  read_json_file,
  wrong_answer_verdict,
  is_number,
  yes_or_no,
  problems_content,
  fetch_samples,
  input_with_timer,
  # download_contests_json_file,
  # conf_file,
  # template_folder,
  # language_conf,
  PROBLEM_CODE_PATTERN,
  extensions,
  resources_folder
)
from cfkit.util.commands import execute_file

File: TypeAlias = str
Directory: TypeAlias = str
FileOrDirectory: TypeAlias = str
ProblemCodeOrFileOrBoth: TypeAlias = str | tuple

class Problem:
  """
  Documentation
  """
  # Ask chatgpt about this name ProblemCodeOrFileOrBoth
  def __init__(self, problem: ProblemCodeOrFileOrBoth = sys.argv[0]) -> None:
    self._solution_file = None
    self._contestid: int = None
    self._problem_index_letter: str = None
    self.contest_name: str = None

    self._response, self.problem_index = self.__validate_parameters(problem)

    self.name: str = self._response[0]
    self.time_limit_seconds: str = self._response[2]
    self.memory_limit_bytes: float = convert_to_bytes(self._response[4])
    self.input_output_type: str = f"input: {self._response[6]}\noutput: {self._response[8]}"

    self._data_path = None
    self._expected_output_list = None
    self._input_samples = None
    self._fwrong = None
    self._tfwrong = None


  def __retrieve_html_source_code(self, code, err=False):
    if search(PROBLEM_CODE_PATTERN + '$', code):
      letter_index = len(code) - 1 if code[-1].isalpha() and len(findall(
        r"[A-z]", code)) == 1 else len(code) - 2
      self._contestid = int(code[:letter_index])
      self._problem_index_letter = code[letter_index:]

      contest_problems_file_path = resources_folder.joinpath("problems", f"{self._contestid}.txt")
      if not contest_problems_file_path.exists():
        response, self.contest_name =  problems_content(
          get_response(
            f"https://codeforces.com/contest/{self._contestid}/problems",
            code,
            self._contestid,
            err
          ).text,
          self._contestid,
          self._problem_index_letter,
          True
        )
        return response
      response, self.contest_name =  problems_content(contest_problems_file_path,
          self._contestid,
          self._problem_index_letter
        )
      return response
    if err:
      raise SyntaxError
    colored_text("No such problem", "error 10")
    sys.exit(1)

  def __validate_parameters(self, problem_code: (tuple | str)):
    '''
    Check if the problem code is available
    '''

    def enter_code():
      '''If the problem code couldn't be recognized from the given path'''
      colored_text("\nProblem code couldn't be recognized from the given path", "error 5")
      code = input("Please enter the problem code: ").strip()
      content = self.__retrieve_html_source_code(code)
      return content, code

    if isinstance(problem_code, str):
      is_file = os.path.isfile(problem_code)
      if not is_file: # If the user gives the problem code
        if os.path.isdir(problem_code):
          colored_text(
            "\nYou should enter a problem code or a file not a directory\n",
            "error 5"
          )
          sys.exit(1)
        file_extension = problem_code.rfind(".")
        if file_extension != -1 and problem_code[file_extension+1:] in extensions:
          colored_text(f"\n<error_9>No such file</> '{problem_code}'\n")
          sys.exit(1)
        content = self.__retrieve_html_source_code(problem_code)

      else: # If the user gives the solution file instead of problem code
        # Searching for the problem code in path
        def desired_problem(problem_index):
          aux = input_with_timer(f"'{problem_index}' Is this the desired problem? [Y/n] ", 'y', 3)
          if aux in ("yes", 'y', ''):
            return True
          elif aux in ("no", 'n', ''):
            return False
          return desired_problem(problem_index)

        base_name = os.path.basename(problem_code)
        match_problem_code_from_file_name = search(PROBLEM_CODE_PATTERN, base_name)
        if match_problem_code_from_file_name: # contestIdProblemIndex.py -> 1234a.py
          try:
            match_problem_code_from_file_name = match_problem_code_from_file_name.group()
            if desired_problem(match_problem_code_from_file_name):
              content = self.__retrieve_html_source_code(
                match_problem_code_from_file_name,
                err=True
              )
              self._solution_file = problem_code
              problem_code = match_problem_code_from_file_name
            else:
              raise SyntaxError
          except SyntaxError:
            content, problem_code = enter_code()

        else: # contestId/problem_index -> 1234/a.py
          dir_name = os.path.dirname(problem_code)
          if dir_name.isdigit() and (
            base_name[0].isalpha() and (base_name[1].isdigit() or base_name[1] == '.')):
            try:
              content = self.__retrieve_html_source_code(dir_name + base_name[0], err=True)
              self._solution_file = problem_code
              problem_code = dir_name + base_name[0]
            except SyntaxError:
              content, problem_code = enter_code()
    else:
      pos_point0 = problem_code[0].find(".")
      pos_point1 = problem_code[1].find(".")
      if pos_point0 != -1 and pos_point1 == -1:
        problem_code = problem_code[1], problem_code[0]
      elif (pos_point0 == -1 and pos_point1 == -1) or (pos_point0 != -1 and pos_point1 != -1):
        print(
          "Please provide the problem code, the solution file, or simply the solution file itself."
        )
        sys.exit(1)
      if search(PROBLEM_CODE_PATTERN + "$", problem_code[0]):
        pass

    return content, problem_code


  def create_solution_file(
      self,
      file_extension: str = None,
      create_contest_folder: bool = True,
      add_problem_name_to_file_name: bool = True,
      path: Directory = os.getcwd()
    ) -> None:
    """
    Documentation
    """

    if file_extension is None:
      # $$$
      # Need to check if there is a default language otherwise he need to enter an extension
      file_extension = "py"

    if path != os.getcwd():
      check_path_existence(path, 'f')
    os.chdir(path)

    def add_problem_name(add_problem_name_to_file_name, code):
      if add_problem_name_to_file_name:
        solution_file = file_name(self.name[3:], code, file_extension)
      else:
        solution_file = code + "." + file_extension
      return solution_file

    if create_contest_folder:
      folder_name = create_file_folder(str(self._contestid), 'd')
      os.chdir(folder_name)
      solution_file = add_problem_name(add_problem_name_to_file_name, self._problem_index_letter.lower())
    else:
      solution_file = add_problem_name(add_problem_name_to_file_name, self._problem_index_letter.lower())

    write_text_to_file(read_text_from_file(retrieve_template(solution_file)), solution_file)

    colored_text("The solution file has been successfully created", "correct") # Grammar checked

  def parse(
      self,
      path: Directory = os.getcwd(),
      create_tests_dir: bool = True,
      __check_path: bool = True,
      print_message: bool = True
    ) -> None:
    """
    Documentation
    """
    def fetch(path, create_tests_dir, __check_path):
      self._data_path = samples_dir(create_tests_dir, path, [self.problem_index], os.listdir(path))

      fetch_samples(
        problem_statement=self._response,
        path_to_save_samples=self._data_path,
        attributes=(self.problem_index, self.name),
        check_path=__check_path,
      )

    if print_message:
      print(f"Parsing {self.problem_index} problem")
      fetch(path, create_tests_dir, __check_path)
      colored_text(f"<error_1>Samples are saved in</> <error_5>{os.path.join(path, self._data_path)}</>")
      colored_text("Test cases parsed successfully.", "correct")
    else:
      fetch(path, create_tests_dir, __check_path)

  def run_demo(
      self,
      check_formatting: bool = False,
      __stop_program: bool = True,
      file_path: str = None
    ):
    """
    Test a participant's solution against Codeforces problem samples
    and download them if they are missed.
    """
    def check_path(file_path):

      def check_file(file_path):
        check_path_existence(file_path, 'f')
        while not os.path.isfile(file_path):
          # Enter a new path
          file_path = colored_text(
            "The path you provided is not a file path" +
            "\nPlease provide <error>an existing file path</> instead: ",
            False, False, True
          )
          check_path_existence(file_path, 'f')
        return file_path

      working_in_script = False
      line_number = None

      # When the user enter 234A problem_index parameter in __init__
      if (file_path is None) and (self._solution_file is None):
        self._solution_file = sys.argv[0]
        if self._solution_file[-3:] == ".py" != -1:
          working_in_script = True
          line_number = currentframe().f_back.f_back.f_lineno          
        else:
          self._solution_file = check_file(input("Path of the solution file: ").strip())

      # When the user enter a path as a parameter in this function (run_demo) (e.g. 1234A.py)
      elif file_path and (self._solution_file is None):
        self._solution_file = check_file(file_path)

      # When the user enter the solution path as a parameter in __init__ function
      elif (file_path is None) and self._solution_file:
        if currentframe().f_back.f_back.f_code.co_filename != os.path.join(
          os.path.dirname(__file__), "cli.py"):
          working_in_script = True

      del file_path
      cwd = os.getcwd()
      self._solution_file = os.path.join(cwd, self._solution_file)
      print(f"{cwd = }")
      print(f"{self._solution_file = }")
      if self._data_path is None:
        self._data_path = os.path.join(cwd, 'tests')
        test = True

        def input_output_list(data_path):
          list_of_files = os.listdir(data_path)
          self._input_samples = sorted(
            [file for file in list_of_files if search(rf"{self.problem_index}_\d.in", file)])
          self._expected_output_list = sorted(
            [file for file in list_of_files if search(rf"{self.problem_index}_\d.out", file)])
          length_input_samples = len(self._input_samples)
          return length_input_samples
        
        if os.path.exists(self._data_path):
          length_input_samples = input_output_list()
          if length_input_samples > 0 or length_input_samples == len(self._expected_output_list):
            test = False
            del length_input_samples
        
        if test:
          # Here where I got the idea of adding __check_path parameter in parse function
          # To prevent checking the path again
          self.parse(cwd, True, False, False)
        
        del cwd
      os.chdir(self._data_path)

      code = None
      # If working with the solution file itself and it's a python file
      if working_in_script:
        with open(self._solution_file, 'r', encoding="UTF-8") as file:
          code = file.readlines()
        # Change the participant code by remove importing cfkit package line from the code
        try:
          my_solution = code.index("# my solution\n")
        except ValueError:
          my_solution = -1

        if my_solution != -1:
          try:
            end_pos = code.index("# end\n")
          except ValueError:
            end_pos = len(code)
          code = code[my_solution+1:end_pos]
          line_number = 0
        else:
          for j in range(len(code[:line_number-1])):
            module_position = code[j].find("cfkit")

            if module_position != -1:
              import_keyword_position = code[j].find("import")
              comma_position = code[j].find(",")
              from_keyword_position = code[j].find("from")
              if (import_keyword_position != -1 and import_keyword_position < module_position and
                  comma_position == -1) or (
                    from_keyword_position != -1 and from_keyword_position < module_position) :
                code[j] = f"# {code[j]}\n"
              elif import_keyword_position != -1 and comma_position != -1: # e.g. import math, cfkit
                code[j] = code[j].split(",")
                if code[j][0].find("cfkit") != -1:
                  if len(code[j][1:]) > 1:
                    code[j] = f"import {', '.join(code[j][1:])}\n"
                  else:
                    code[j] = f"import {code[j][1]}\n"
                else:
                  code[j] = list(map(lambda x: x.replace("cfkit", "").strip(), code[j]))
                  code[j] = ", ".join(list(filter(bool, code[j]))) + "\n"
        write_text_to_file(
          "".join(code[:line_number-1] + code[line_number:]),
          os.path.join(os.getcwd(), "cfkit_module_user_code.py")
        )

      return working_in_script, code, line_number

    working_in_script, code, line_number = check_path(file_path)

    number_of_tests = len(self._input_samples)
    verdict = [(None, None)] * number_of_tests
    errors = {
      "Wrong answer": 0,
      "Compilation error": 0,
      "Runtime error": 0,
      "Memory limit exceeded": 0,
      "Formatting error": 0
    }

    # Loop through samples
    accepeted = True
    solution_resources = [None] * len(self._input_samples)
    for i, input_sample in enumerate(self._input_samples):
      output_path = f"{self.problem_index}_test_case{i+1}.out"

      # Executing solution
      # ================================================================
      if working_in_script:
        python_command = execute_file(
          "cfkit_module_user_code.py",
          input_sample,
          output_path,
          self.memory_limit_bytes,
          working_in_script
        )
        os.remove("cfkit_module_user_code.py")
      else:
        execute_file(self._solution_file, input_sample, output_path, self.memory_limit_bytes)
      # ================================================================

      # Checking go program output
      # ================================================================
      def checker_log(error, err_num, solution_resources, terminal_columns, observed, i):
        if solution_resources == error:
          verdict[i] = (f"Test case {i+1}", colored_text(error, err_num, False, False))
          errors[error] += 1
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
        solution_resources[i] = read_text_from_file(output_path[:-4] + "_memory.out")
        checker_log(
          "Compilation error", "error 1",
          solution_resources,
          terminal_columns,
          observed,
          i
        )
        checker_log(
          "Runtime error",
          "error 2",
          solution_resources,
          terminal_columns,
          observed,
          i
        )
        checker_log(
          "Memory limit exceeded",
          "error 3",
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
          verdict[i] = (f"Test case {i+1}", colored_text("OK", "correct", False, False))
          accepeted = accepeted and True
      # ================================================================

        # In case of wrong answer and results are floating point numbers
        # ================================================================
        else:
          expected = expected.split("\n")[:-1]
          observed = observed.split("\n")[:-1]
          def check_length(line1, line2):
            if len(line1) != len(line2):
              raise InterruptedError

          if check_formatting: # Option in the terminal to check formatting
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

            equal = False
            if check_formatting:
              for line_number, line_values in enumerate(zip(expected, observed)):
                expected_line = line_values[0].split(' ')
                observed_line = line_values[1].split(' ')
                # Option in the terminal that choose between checking formatting or not
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
              data = [[], []]
              for line_number, line_values in enumerate(zip(expected, observed)):
                expected_line = line_values[0].split(' ')
                observed_line = line_values[1].split(' ')
                data[0].extend(expected_line)
                data[1].extend(observed_line)

              for column_num, output in enumerate(zip(data[0], data[1])):
                equal = compare_values(output[0], output[1], 0, column_num)
                if not equal:
                  # Remove word 'line' from the error message
                  self._tfwrong = self._tfwrong[:14] + self._tfwrong[
                    self._tfwrong.find(" line ") + 6:]
                  break

          except InterruptedError:
            verdict[i] = (
              f"Test case {i+1}",
              colored_text("Formatting error", "error 4", False, False)
            )
            errors["Formatting error"] += 1

          if equal:
            verdict[i] = (f"Test case {i+1}", colored_text("OK", "correct", False, False))
            accepeted = accepeted and True

          else:
            accepeted = False
            verdict[i] = (f"Test case {i+1}", colored_text("Wrong answer", "wrong", False, False))
            errors["Wrong answer"] += 1
            self._fwrong = i + 1 if self._fwrong is None else None
    # =============================================================================================

    # Results
    def print_results(verdict, solution_resources: list[str]):
      def extract_list(solution_resources) -> (list[float], list[float]):
        memory = [None] * len(solution_resources)
        time = [None] * len(solution_resources)
        for i, resources in enumerate(solution_resources):
          resources = resources.split("\n")
          time[i] = round(float(resources[0][:resources[0].find(' ')]), 3)
          pos_space = resources[1].find(' ')
          memory[i] = round(float(resources[1][:pos_space]), 3), resources[1][pos_space+1:] 
        return memory, time
      memory, time = extract_list(solution_resources)
      max_length_time = len(str(max(time, key=lambda x: len(str(x)))))
      max_length_memory = len(str(max(memory, key=lambda x: len(str(x[0])))))
      print(f"{max_length_time = }")
      print(f"{max_length_memory = }")
      for i, verdict_response in enumerate(verdict):
        if memory[0] != "Compilation error":
          print(
            f"{verdict_response[0]},",
            f"time: {time[i]}{' ' * (max_length_time - len(str(time[i])))} ms,",
            f"memory: {memory[i][0]}{' ' * (max_length_memory - len(str(memory[i][0])))} {memory[i][1]},",
            # The problem here is that there are extra spaces between (MB|KB|B) unit and the value
            f"verdict: {verdict_response[1]}"
          )
        else:
          print(f"{verdict_response[0]}, time: 0s, memory: 0B, verdict: Compilation error")
      print('')

    test_results_file_path = os.path.join(resources_folder, "test_samples_results.json")
    test_results: dict = read_json_file(test_results_file_path)
    # If solution get accepted
    # ================================================================
    if accepeted:
      colored_text("Demo Accepeted", "accepted")
      print_results(verdict, solution_resources)
      if test_results["unsolved_problems"].get(self.problem_index) is not None:
        test_results["demo_accepted"][
          self.problem_index] = test_results["unsolved_problems"].pop(self.problem_index)
        test_results["demo_accepted"][self.problem_index]["timestamp"] = datetime.now(
          ).strftime("%Y-%m-%d %H:%M:%S")
        write_json_file(test_results, test_results_file_path, 2)

      elif test_results["demo_accepted"].get(self.problem_index) is None:
        test_results["demo_accepted"][self.problem_index] = {}
        test_results["demo_accepted"][self.problem_index]["problem_name"] = self.name
        test_results["demo_accepted"][self.problem_index]["timestamp"] = datetime.now(
          ).strftime("%Y-%m-%d %H:%M:%S")
        if test_results["unsolved_problems"].get(self.problem_index) is None:
          test_results["demo_accepted"][self.problem_index]["errors"] = errors
        else:
          test_results["demo_accepted"][self.problem_index]["errors"] = test_results[
            "unsolved_problems"][self.problem_index]["errors"]
        write_json_file(test_results, test_results_file_path, 2)

      else:
        print("You have already solved this problem!")

      remove = False
      cwd = os.getcwd()
      user_choice = yes_or_no(
        f"Do you want to remove this directory '{cwd}'\n"
        f"i.e. '{os.path.basename(cwd)}'"
        )
      if user_choice:
        rmtree(os.getcwd())
        os.chdir("..")
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
        remove_files(
          [
            (f"{self.problem_index}_test_case{i}.out",
            f"{self.problem_index}_test_case{i}_memory.out"
            ) for i in range(1, number_of_tests+1)
          ]
        )
    # ================================================================
    # If solution is not correct whether the verdict output wrong answer or an error
    else:
      print(f"\nChecker log:\n{self._tfwrong}\n")
      print_results(verdict, solution_resources)

      if test_results["demo_accepted"].get(self.problem_index) is not None:
        for key in test_results["demo_accepted"][self.problem_index]["errors"].keys():
          test_results["demo_accepted"][self.problem_index]["errors"][key] += errors[key]

      elif test_results["unsolved_problems"].get(self.problem_index) is None:
        test_results["unsolved_problems"][self.problem_index] = {}
        test_results["unsolved_problems"][self.problem_index]["problem_name"] = self.name
        test_results["unsolved_problems"][self.problem_index]["timestamp"] = datetime.now(
          ).strftime("%Y-%m-%d %H:%M:%S")
        test_results["unsolved_problems"][self.problem_index]["errors"] = errors

      else:
        for key in test_results["unsolved_problems"][self.problem_index]["errors"].keys():
          test_results["unsolved_problems"][self.problem_index]["errors"][key] += errors[key]

      write_json_file(test_results, test_results_file_path, 2)

    if working_in_script and __stop_program:
      print(code)
      print(f"{line_number = }")
      print(code[line_number:])
      print(any(code[line_number:]))
      print(working_in_script, any(code[line_number:]))
      if working_in_script and any(code[line_number:]):
        print(os.getcwd())
        with open("cfkit_finish_program.py", 'w', encoding="UTF-8") as file:
          file.writelines(code[line_number:])

        create_file_folder("cfkit_empty_input_test.in", 'f', True)
        try:
          process = run(
            f"{python_command} cfkit_finish_program.py < cfkit_empty_input_test.in",
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
            text=True
          )
          if len(process.stderr) != 0 or len(process.stdout) != 0:
            if not yes_or_no("Finish executing the program", "[N/y]"):
              sys.exit(1)

        except CalledProcessError as err:
          colored_text(f"<error>Error:</> {err}")

        os.remove("cfkit_empty_input_test.in")
        os.remove("cfkit_finish_program.py")

if __name__ == "__main__":
  # problem_one = Problem("1882C")
  # print(problem_one.name)
  # print(problem_one.input_output_type)
  # print(problem_one.time_limit_seconds)
  # print(problem_one.memory_limit_bytes)
  # problem_one.parse()
  pass
