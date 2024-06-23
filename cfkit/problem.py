"""
Documentation
"""
import os
import sys
from pathlib import Path
from re import search
from re import findall
from typing import Any
from math import isclose
from shutil import rmtree
from datetime import datetime
from inspect import currentframe
from subprocess import CalledProcessError, run, PIPE


from cfkit.util.common import confirm
from cfkit.util.common import is_number
from cfkit.util.common import file_name
from cfkit.util.common import check_file
from cfkit.util.common import samples_dir
from cfkit.util.common import get_response
from cfkit.util.common import colored_text
from cfkit.util.common import fetch_samples
from cfkit.util.common import english_ending
from cfkit.util.common import read_json_file
from cfkit.util.common import write_json_file
from cfkit.util.common import convert_to_bytes
from cfkit.util.common import problems_content
from cfkit.util.common import retrieve_template
from cfkit.util.common import write_text_to_file
from cfkit.util.common import create_file_folder
from cfkit.util.common import read_text_from_file
from cfkit.util.common import check_path_existence
from cfkit.util.common import wrong_answer_verdict
from cfkit.util.common import input_with_time_limit

from cfkit.util.commands import execute_file
from cfkit.util.variables import conf_file
from cfkit.util.variables import resources_folder
from cfkit.util.variables import language_conf_path
from cfkit.util.variables import output_filename
from cfkit.util.variables import errors_memory_time_filename
from cfkit.util.variables import input_extension_file
from cfkit.util.variables import output_extension_file
from cfkit.util.constants import Directory
from cfkit.util.constants import LANGUAGES
from cfkit.util.constants import EXTENSIONS
from cfkit.util.constants import LANGUAGES_EXTENSIONS
from cfkit.util.constants import PROBLEM_CODE_PATTERN
from cfkit.util.constants import ProblemCodeOrFileOrBoth
from cfkit.config import set_language_attributes


class Problem:
  """
  Documentation
  """
  # Ask chatgpt about this name ProblemCodeOrFileOrBoth
  def __init__(self, problem_code: ProblemCodeOrFileOrBoth = None) -> None:
    self._solution_file: str = None
    self._contestid: int = None
    self._problem_index_letter: str = None
    self.contest_name: str = None

    self._response, self.problem_index = self.__validate_parameters(problem_code)

    self.name: str = self._response[0]
    self.time_limit_seconds: str = self._response[2]
    self.time_limit_seconds_number: float = float(
      self.time_limit_seconds[:self.time_limit_seconds.find(" ")]
    )
    self.memory_limit_bytes: float = convert_to_bytes(self._response[4])
    self.input_output_type: str = f"input: {self._response[6]}\noutput: {self._response[8]}"

    self._data_path: str = None
    self._input_samples: list[str] = None
    self._expected_output_samples: list[str] = None
    self._custom_input_samples: list[str] = None
    self._expected_custom_output_samples: list[str] = None
    self._fwrong: str = None


  def __retrieve_html_source_code(self, code: str, err: bool = False) -> str:
    if search(PROBLEM_CODE_PATTERN + '$', code) is not None:
      letter_index = len(code) - 1 if code[-1].isalpha() and len(findall(
        r"[A-z]", code)) == 1 else len(code) - 2
      self._contestid = int(code[:letter_index])
      self._problem_index_letter = code[letter_index:].upper()

      contest_problems_file_path = resources_folder.joinpath("problems", f"{self._contestid}.txt")
      if not contest_problems_file_path.exists():
        response, self.contest_name = problems_content(
          get_response(
            f"https://codeforces.com/contest/{self._contestid}/problems",
            code,
            self._contestid,
          ),
          self._contestid,
          self._problem_index_letter,
          True
        )
        return response
      response, self.contest_name = problems_content(
        contest_problems_file_path,
        self._contestid,
        self._problem_index_letter
      )
      return response

    if err:
      raise SyntaxError
    colored_text(
      f"<error_5>No such problem</> '{code}'",
      exit_code_after_print_statement=1
    )

  def __validate_parameters(self, problem_code: (tuple | str)):
    '''
    Check if the problem code is available
    '''

    def enter_code() -> tuple[str, str]:
      '''If the problem code couldn't be recognized from the given path'''
      colored_text(
        "\nProblem code couldn't be recognized from the given path",
        one_color="error 5"
      )
      code = input("Please enter the problem code: ").strip()
      content = self.__retrieve_html_source_code(code)
      return content, code

    if problem_code is None and sys.argv[0].endswith(".py"):
      problem_code = os.path.abspath(sys.argv[0])

    if isinstance(problem_code, str):
      # If the user gives the problem code
      if not os.path.isfile(problem_code):
        #// if os.path.isdir(problem_code):
        #//   colored_text(
        #//     "\nYou should enter a problem code or a file not a directory\n",
        #//     one_color="error 5",
        #//     exit_code_after_print_statement=1
        #//   )
        #* If the user enters a file path that does not exist
        file_extension = problem_code.rfind(".")
        if file_extension != -1 and problem_code[file_extension+1:] in EXTENSIONS:
          colored_text(
            f"\n<error_5>No such file</> '{problem_code}'\n",
            exit_code_after_print_statement=1
          )
        content = self.__retrieve_html_source_code(problem_code)

      # If the user gives the solution file instead of problem code
      else:
        # Searching for the problem code in the given path
        def desired_problem(problem_index: str) -> bool:
          return input_with_time_limit(
            confirm,
            3,
            True,
            message=f"'{problem_index}' Is this the desired problem?"
          )

        base_name = os.path.basename(problem_code)
        match_problem_code_from_file_name = search(PROBLEM_CODE_PATTERN, base_name)
        if match_problem_code_from_file_name is not None: # contestIdProblemIndex.py (e.g. 1234a.py)
          match_problem_code_from_file_name = match_problem_code_from_file_name.group()
          self._solution_file = problem_code
          if desired_problem(match_problem_code_from_file_name):
            content = self.__retrieve_html_source_code(
              match_problem_code_from_file_name,
            )
            problem_code = match_problem_code_from_file_name
          else:
            content, problem_code = enter_code()

        else: # contestId/problem_code (e.g. 1234/a.py: where 1234 is the folder)
          dir_name = os.path.dirname(problem_code)
          if dir_name == '':
            dir_name = os.path.basename(os.getcwd())

          #* Check if the directory name represents the contest ID and the file name represents the problem code.
          if dir_name.isdigit() and (
            search(r"[A-z]\d\.", base_name) is not None  or
            search(r"[A-z]\.", base_name) is not None
          ):
            self._solution_file = problem_code
            if desired_problem(dir_name + (base_name[0] if base_name[1] == "." else base_name[:2])):
              content = self.__retrieve_html_source_code(dir_name + base_name[0])
              problem_code = dir_name + base_name[0]
            else:
              content, problem_code = enter_code()
          else:
            colored_text(
              "Could not extract the problem code from the given path",
              one_color="error 5",
              exit_code_after_print_statement=1
            )

    elif isinstance(problem_code, (tuple, list)):
      point_pos0 = problem_code[0].find(".")
      point_pos1 = problem_code[1].find(".")
      if point_pos0 != -1 and point_pos1 == -1:
        problem_code = problem_code[1], problem_code[0]
      elif (point_pos0 == -1 and point_pos1 == -1) or (point_pos0 != -1 and point_pos1 != -1):
        colored_text(
          "Please provide the problem code or simply the solution file itself or both.",
          one_color="error",
          exit_code_after_print_statement=1
        )

      #* Check if the path exists and is a file
      if os.path.isfile(problem_code[0]):
        self.problem_index = problem_code[0]
        self._solution_file = problem_code[1]
        content = self.__retrieve_html_source_code(problem_code[0])
        problem_code = problem_code[0]
      else:
        colored_text(
          f"\n<error_5>No such file</> '{problem_code[0]}'\n",
          exit_code_after_print_statement=1
        )
    else:
      colored_text(
        "problem_code must be a string, tuple, or list.",
        one_color="error",
        exit_code_after_print_statement=1
      )
    return content, problem_code.upper()

  def create_solution_file(
      self,
      file_extension: str = None,
      create_contest_folder: bool = False,
      add_problem_name_to_file_name: bool = True,
      path: Directory = None
    ) -> None:
    """
    Documentation
    """

    if file_extension is None:
      default_language = conf_file["cfkit"]["default_language"].strip()
      if default_language == "":
        print(
          "You should set a default language so that you don't have to enter the programming language every time"
        ) # grammar checked

      elif default_language not in LANGUAGES:
        file_extension = input("Extension: ")
        while file_extension not in EXTENSIONS:
          colored_text("Extension not found! Please try again", one_color="error 5")
          file_extension = input("Extension: ")
      else:
        file_extension = LANGUAGES_EXTENSIONS[default_language][0]

    if path is None:
      path = os.getcwd()

    if path != os.getcwd():
      check_path_existence(path, 'd')
    os.chdir(path)

    def add_problem_name(add_problem_name_to_file_name: bool, code: str) -> None:
      if add_problem_name_to_file_name:
        solution_file = file_name(self.name[self.name.find(" ") + 1:], code, file_extension)
      else:
        solution_file = code + "." + file_extension
      return solution_file

    if create_contest_folder:
      folder_name = create_file_folder(str(self._contestid), 'd')
      os.chdir(folder_name)

      solution_file = add_problem_name(
        add_problem_name_to_file_name,
        self._problem_index_letter.lower()
      )
    else:
      solution_file = add_problem_name(
        add_problem_name_to_file_name,
        f"{self._contestid}{self._problem_index_letter.lower()}"
      )

    write_text_to_file(read_text_from_file(retrieve_template(solution_file)), solution_file)

    colored_text("The solution file has been successfully created", one_color="correct") # Grammar checked

  def parse(
      self,
      path: Directory = None,
      create_tests_dir: bool = False,
      short_names: bool = False,
      __check_path: bool = True,
      __print_message: bool = True
    ) -> None:
    """
    Documentation
    """
    if path is None:
      path = os.getcwd()

    def fetch(path, create_tests_dir, __check_path):
      self._data_path = samples_dir(create_tests_dir, path, [self.problem_index])

      self._input_samples, self._expected_output_samples = fetch_samples(
        problem_statement=self._response,
        path_to_save_samples=self._data_path,
        attributes=(self.problem_index, self.name),
        check_path=__check_path,
        short_names=short_names,
      )

    if __print_message:
      print(f"Parsing {self.problem_index} problem")
      fetch(path, create_tests_dir, __check_path)
      colored_text(
        f"<blue_text>Samples are saved in</>",
        f"'{os.path.join(path, self._data_path)}</>'\n"
        "<correct>Test cases parsed successfully.</>"
      )
    else:
      fetch(path, create_tests_dir, __check_path)

  def run_demo(
      self,
      file_path: str = None,
      check_formatting: bool = False,
      remove_samples_output_files_if_demo_accepted: bool = False,
      stop_program: bool = True,
      verbose: bool = True,
    ) -> None:
    """
    Test a participant's solution against Codeforces problem samples
    and download them if they are missed.
    """
    def check_path(file_path) -> tuple[bool, list[str], int | bool, None, None]:
      """
      Documentation
      """
      working_in_script = False
      code = None
      line_number = None

      if file_path is not None:
        check_path_existence(file_path, 'f')

      # When the user enter 234A problem index as a parameter in __init__
      # -------------------------------------------------------------------------------------------
      if (file_path is None) and (self._solution_file is None):
        self._solution_file = sys.argv[0]
        working_in_script = True
        # self._solution_file = check_file(input("Path of the solution file: ").strip())
      # -------------------------------------------------------------------------------------------


      # When the user enter a path as a parameter in run_demo (this function) (e.g. 1234A.py)
      # -------------------------------------------------------------------------------------------
      elif (file_path is not None) and (self._solution_file is None):
        # If the file_path is the same as the working file (working in script file)
        if Path(file_path).samefile(os.path.abspath(sys.argv[0])):
          working_in_script = True
          line_number = currentframe().f_back.f_back.f_lineno
          self._solution_file = file_path
        else:
          self._solution_file = check_file(file_path)
      # -------------------------------------------------------------------------------------------


      # When the user enters two different paths (one in the init method and another in the run_demo function)
      # -------------------------------------------------------------------------------------------
      elif (file_path is not None) and (self._solution_file is not None):
        file_path = Path(file_path)
        if not file_path.samefile(self._solution_file):
          colored_text(
            "You have entered different paths",
            one_color="error 5",
            exit_code_after_print_statement=1
          )
        elif file_path.samefile(os.path.abspath(sys.argv[0])):
          working_in_script = True
          line_number = currentframe().f_back.f_back.f_lineno
      # -------------------------------------------------------------------------------------------

      def input_output_list(data_path) -> None:
        list_of_files = os.listdir(data_path)
        self._input_samples = sorted(
          [
            file for file in list_of_files if search(
            rf"{self.problem_index}_\d+\.{input_extension_file}", file)
          ]
        )
        self._expected_output_samples = sorted(
          [
            file for file in list_of_files if search(
            rf"{self.problem_index}_\d+\.{output_extension_file}", file)
          ]
        )

        self._custom_input_samples = sorted(
          [file for file in list_of_files if search(r"\A" + rf"{input_extension_file}" + "\d{0,}$", file)]
        )
        self._expected_custom_output_samples = sorted(
          [file for file in list_of_files if search(r"\A" + rf"{output_extension_file}" + "\d{0,}$", file)]
        )

      del file_path # Now we have the solution file stored in self._solution_file
      cwd = os.getcwd()
      self._solution_file = os.path.join(cwd, self._solution_file)


      if self._data_path is None:
        self._data_path = os.path.join(cwd, 'tests')
        test = True
        if os.path.exists(self._data_path):
          input_output_list(self._data_path)
          input_samples_num = len(self._input_samples)
          if input_samples_num > 0 and input_samples_num == len(self._expected_output_samples):
            test = False
            del input_samples_num

        if test:
          # Here where I got the idea of adding __check_path parameter in parse function
          # To prevent checking the path again
          self.parse(cwd, True, False, False, False)

      else:
        input_output_list(self._data_path)

      os.chdir(self._data_path)
      # If working with the solution file itself and it's a python file
      if working_in_script:
        with open(self._solution_file, 'r', encoding="UTF-8") as file:
          code = file.readlines()
        code_length = len(code)

        # Searching for the beginning of the solution
        solution_pos = None
        end_pos = code_length
        for i in range(code_length):
          line_without_spaces = code[i].replace(" ", "")
          if line_without_spaces == "#solution\n":
            solution_pos = i
          elif line_without_spaces.replace("\n", "") == "#end":
            end_pos = i

        if solution_pos is not None:
          code = code[solution_pos + 1:end_pos]
          write_text_to_file("".join(code), os.path.join(os.getcwd(), "cfkit_module_user_code.py"))
        else:
          # Modify the participant's code by removing the 'import cfkit' package line (BETA)
          for j in range(len(code[:line_number-1])):
            module_position = code[j].find("cfkit")

            if module_position != -1:
              import_keyword_position = code[j].find("import")
              comma_position = code[j].find(",")
              from_keyword_position = code[j].find("from")
              if (
                import_keyword_position != -1 and import_keyword_position < module_position and comma_position == -1) or (
                from_keyword_position != -1 and from_keyword_position < module_position
              ) :
                code[j] = f"# {code[j]}\n"
              # e.g. import math, cfkit
              elif import_keyword_position != -1 and comma_position != -1 and import_keyword_position < module_position:
                import_line_list = code[j].split(",")
                i = 0
                while i < len(import_line_list):
                  import_line_list[i] = "" if import_line_list[i].find("cfkit") > -1 else import_line_list[i]
                  i = i + 1
                code[j] = "import " if import_line_list[0].find("import") == -1 else "" + ", ".join(
                  [x for x in import_line_list if x]) + "\n"

          write_text_to_file(
            "".join(code[:line_number-1] + code[line_number:]),
            os.path.join(os.getcwd(), "cfkit_module_user_code.py")
          )

      return working_in_script
      # return working_in_script, code, line_number

    # working_in_script, code, line_number = check_path(file_path)
    working_in_script = check_path(file_path)

    # Retrieve the execution and compile commands
    # =============================================================================================
    ext = self._solution_file[self._solution_file.rfind(".")+1:]
    if ext == self._solution_file:
      colored_text(
        "\nPlease add the appropriate file extension to the file name.",
        "This ensures accurate language identification.",
        one_color="error",
        exit_code_after_print_statement=1
      )

    programming_language = EXTENSIONS.get(ext)
    if programming_language is None:
      colored_text(
        "Oops! It looks like that the provided language is not supported by Codeforces.",
        one_color="error",
        exit_code_after_print_statement=1
      )

    language_conf = read_json_file(language_conf_path)
    compile_command = language_conf[programming_language].get("compile_command")
    execute_command = language_conf[programming_language].get("execute_command")
    calculate_memory_usage_and_execution_time_command = language_conf[programming_language].get("calculate_memory_usage_and_execution_time_command")
    calculate_memory_usage_and_execution_time_bool = conf_file["cfkit"][
      "calculate_memory_usage_and_execution_time"]
    if calculate_memory_usage_and_execution_time_bool == "false":
      calculate_memory_usage_and_execution_time_bool = False
      errors = {
        "Wrong answer": 0,
        "Compilation error": 0,
        "Runtime error": 0,
        "Formatting error": 0
      }

    else:
      calculate_memory_usage_and_execution_time_bool = True
      errors = {
        "Wrong answer": 0,
        "Compilation error": 0,
        "Runtime error": 0,
        "Memory limit exceeded": 0,
        "Time limit exceeded": 0,
        "Formatting error": 0
      }

    if (execute_command is None) or (compile_command is None) or (
      calculate_memory_usage_and_execution_time_command is None):
      compile_command, execute_command, calculate_memory_usage_and_execution_time_command = set_language_attributes(programming_language)


    if calculate_memory_usage_and_execution_time_bool:
      execute_command = calculate_memory_usage_and_execution_time_command
    else:
      execute_command += " < %%{input_file}%% > %%{output_file}%% 2> %%{output_memory}%%"
    # =============================================================================================

    #* Compile the solution file if the language requires compilation
    # =============================================================================================
    if compile_command is not None:
      try:
        run(
          compile_command.replace("%%{file}%%", self._solution_file).replace(
            "%%{output}%%", self.problem_index
          ),
          shell=True,
          check=True,
          # text=True
        )
      except CalledProcessError as err:
        errors["Compilation error"] = 1
        colored_text(
          f"\n<error_1>Compilation error</>\n<blue_text>Command:</> `{err.cmd}`",
          f"returned non-zero exit status: <bright_text>{err.returncode}</>",
          exit_code_after_print_statement=1
        )
    # =============================================================================================
    def save_first_error(error, test_num):
      if self._fwrong is None:
        self._fwrong = colored_text(
        f"{error} on test {test_num}",
        one_color="error 1",
        return_statement=True
      )

    def save_ok_test(verdict, i, ok):
      ok = ok and True
      if calculate_memory_usage_and_execution_time_bool and verdict[i] is not None:
        verdict[i] = colored_text(
          f"<correct>OK</> (Warning: {verdict[i]})", return_statement=True
        )
      else:
        verdict[i] = colored_text("OK", one_color="correct", return_statement=True)
      return ok

    def test_solution_against_samples(input_samples_list: list[str], expected_output_samples: list[str] = None, expected_output_bool: bool = True):

      def adjusting_paths(input_sample, i, output_filenames_list, errors_memory_time_of_solution_filenames_list):
        participant_output_path = os.path.join(self._data_path, output_filename.replace(
          "%%problem_code%%", self.problem_index).replace("%%test_case_num%%", str(i + 1)))
        output_filenames_list[i] = participant_output_path

        errors_memory_time_of_solution_filenames_list[i] = errors_memory_time_filename.replace(
          "%%problem_code%%", self.problem_index).replace("%%test_case_num%%", str(i + 1))

        input_sample = os.path.join(self._data_path, input_sample)

        return input_sample, participant_output_path

      def execute_solution(input_sample, participant_output_path, errors_memory_time_of_solution_filename):
        if not working_in_script:
          return execute_file(
            self._solution_file,
            self.problem_index,
            input_sample,
            participant_output_path,
            errors_memory_time_of_solution_filename,
            self.memory_limit_bytes,
            execute_command,
          )
        else:
          return execute_file(
            "cfkit_module_user_code.py",
            self.problem_index,
            input_sample,
            participant_output_path,
            errors_memory_time_of_solution_filename,
            self.memory_limit_bytes,
            execute_command
          )

      terminal_columns = os.get_terminal_size().columns

      number_of_tests = len(input_samples_list)
      checker_log_list = [None] * number_of_tests
      errors_memory_time_of_solution = [None] * number_of_tests

      participant_output_filenames_list = [None] * number_of_tests # To remove them later if demanded
      errors_memory_time_of_solution_filenames_list = [None] * number_of_tests # To remove them later if demanded

      if expected_output_bool:
        accepeted = True
        verdict = [None] * number_of_tests

      #* Loop through samples
      # =============================================================================
      for i, input_sample in enumerate(input_samples_list):
        input_sample, participant_output_path = adjusting_paths(
          input_sample,
          i,
          participant_output_filenames_list,
          errors_memory_time_of_solution_filenames_list
        )

        exitcode = execute_solution(
          input_sample,
          participant_output_path,
          errors_memory_time_of_solution_filenames_list[i]
        )

        def fill_checker_log_list(data):
          data = data[:-1] if data[-1] == '' else data
          for line in data:
            checker_log_list[i] += f"| {line} {' ' * (50 - len(line) - 2)}|\n"

        if expected_output_bool:
          expected = read_text_from_file(expected_output_samples[i])
          while expected[-1] == "\n":
            expected = expected[:-1]
          expected_without_nl = expected.replace("\n", " ")
          expected = expected.split("\n")

        observed = read_text_from_file(participant_output_path)
        while observed[-1] == "\n":
          observed[-1] == "\n"
        observed_without_nl = observed.replace("\n", " ")

        observed = observed.split("\n")

        checker_log_list[i] = f"Input\n {'-' * 50}\n"
        fill_checker_log_list(read_text_from_file(input_sample).split("\n"))

        checker_log_list[i] += f" {'-' * 50 }\n\nOutput\n {'-' * 50}\n"
        fill_checker_log_list(observed)

        if expected_output_bool:
          checker_log_list[i] += f" {'-' * 50 }\n\nAnswer\n {'-' * 50}\n"
          fill_checker_log_list(expected)

        if expected_output_bool:
          checker_log_list[i] += f" {'-' * 50 }\nChecker log: "
        else:
          checker_log_list[i] += " " + "-" * 50 + "\n"

        # Judge test results
        # ===========================================================================================

        try:
          def save_error(error, err_num, message):
            colored_text(message)
            print('-' * terminal_columns)
            verdict[i] = colored_text(error, one_color=f"error {err_num}", return_statement=True)
            errors[error] += 1

          if calculate_memory_usage_and_execution_time_bool:
            def checker_log(error, err_num: str, solution_resources: str, message: str) -> None:
              if solution_resources == error:
                save_error(error, err_num, message)
                if error == "Runtime error":
                  raise InterruptedError

              elif error == "Time limit exceeded":
                time_taken_test = float(solution_resources[:solution_resources.find(" ")])
                if time_taken_test > self.time_limit_seconds_number * 1000:
                  save_error()

            errors_memory_time_of_solution[i] = read_text_from_file(
              errors_memory_time_of_solution_filenames_list[i]
            )

            checker_log(
              "Runtime error",
              2,
              errors_memory_time_of_solution[i],
              f"<error>Error:</> Can't finish executing file on test {i + 1}:\n{observed}\n"
            )
            checker_log(
              "Memory limit exceeded",
              3,
              errors_memory_time_of_solution[i],
              f"<warning>Warning</>: The memory limit exceeded for test case {i + 1}."
            )
            checker_log(
              "Time limit exceeded",
              8,
              errors_memory_time_of_solution[i],
              f"<warning>Warning</>: The time limit exceeded for test case {i + 1}."
            )
          else:
            if exitcode != 0:
              save_error(
                "Runtime error", 2, f"<error>Error:</> Can't finish executing file on test {i + 1}"
              )
              raise InterruptedError

        except InterruptedError:
          if expected_output_bool:
            accepeted = False
          save_first_error("Runtime error", i + 1)
          checker_log_list[i] += f"Exit code is {exitcode}"
          continue

        # If there are no runtime errors
        else:
          if expected_output_bool:
            #* Compare the results if the output is an integer or a string
            # =========================================================================================
            observed_len = 0
            for line in observed:
              observed_len += 1 if line else 0
            if len(expected) > 0 and observed_len == 0:
              colored_text(
                "No output was generated",
                one_color="error",
                exit_code_after_print_statement=1
              )

            if expected_without_nl == observed_without_nl:
              accepeted = save_ok_test(verdict, i, accepeted)
              checker_log_list[i] += "ok"
          # ===========================================================================================


            # In case of wrong answer and results are floating point numbers
            # =========================================================================================
            else:
              def check_length(line1, line2, message, err = True) -> bool | str | None:
                if (line1_length:=len(line1)) != (line2_length:=len(line2)):
                  message = message.replace('%1%', str(line1_length)).replace('%2%', str(line2_length))
                  if line1_length > 1:
                    message = message.replace("(s)", 's')
                  else:
                    message = message.replace("(s)", '')
                  if not err:
                    return message
                  raise InterruptedError(message)
                return True

              def check_answer() -> tuple[bool, str] | tuple[None, None]:
                wrong_answer_message = None
                if check_formatting:
                  check_length(expected, observed, "Wrong answer: expected %1% line(s), found %2%\n\n")

                def compare_values(expected_value, observed_value, line, column) -> bool:
                  """
                  Compare two values only
                  """
                  if is_number(expected_value) and is_number(observed_value):
                    num1 = float(expected_value)
                    num2 = float(observed_value)
                    equal = isclose(num1, num2, rel_tol=1.5E-5 + 1E-15)
                    numbers_or_words = 'numbers'
                  else:
                    equal = expected_value == observed_value
                    numbers_or_words = 'words'

                  wrong_answer_message = None
                  if not equal:
                    wrong_answer_message = wrong_answer_verdict(
                      line,
                      column,
                      numbers_or_words,
                      expected_value,
                      observed_value
                    )
                    return False, wrong_answer_message
                  return True, wrong_answer_message

                equal = False

                if check_formatting:
                  for line_number, line_values in enumerate(zip(expected, observed)):
                    expected_line = line_values[0].split(' ')
                    observed_line = line_values[1].split(' ')
                    check_length(
                      expected_line,
                      observed_line,
                      f"Wrong answer: {line_number + 1}{english_ending(line_number + 1)} line, "
                      "expected %1% value(s), found %2%\n\n"
                    )
                    for column_number, column_value in enumerate(zip(expected_line, observed_line)):
                      # column_value[0] is the exepected value and column_value[1] is the observed value
                      equal, wrong_answer_message = compare_values(
                        column_value[0],
                        column_value[1],
                        line_number + 1,
                        column_number + 1
                      )
                      if not equal:
                        return equal, wrong_answer_message

                else:
                  data = [[], []]
                  if len(observed) == 0 and len(expected) > 0:
                    equal, wrong_answer_message = compare_values(expected[0].split(" ")[0], '', 0, 1)

                  for line_number, line_values in enumerate(zip(expected, observed)):
                    expected_line = line_values[0].split(' ')
                    observed_line = line_values[1].split(' ')
                    data[0].extend(expected_line)
                    data[1].extend(observed_line)

                  remove_empty_strings(data[0])
                  remove_empty_strings(data[1])

                  if len(data[0]) != len(data[1]):
                    length = check_length(
                      data[0],
                      data[1],
                      "Wrong answer: expected %1% value(s), found %2%\n\n",
                      False
                    )
                    if isinstance(length, str):
                      return False, length
                  for column_num, output in enumerate(zip(data[0], data[1])):
                    equal, wrong_answer_message = compare_values(output[0], output[1], 0, column_num + 1)
                    if not equal:
                      return equal, wrong_answer_message

                # End of check_answer() function
                return True, None


              del expected_without_nl
              del observed_without_nl
              def remove_empty_strings(data: list):
                while data[-1] == "":
                  data.pop()

              remove_empty_strings(expected)
              remove_empty_strings(observed)

              try:
                equal, wrong_answer_message = check_answer()
              except InterruptedError as err:
                if self._fwrong is None:
                  self._fwrong = colored_text(
                    f"Formatting error on test {i + 1}",
                    one_color="error 1",
                    return_statement=True
                  )

                accepeted = False
                verdict[i] = colored_text("Formatting error", one_color="error 4",return_statement=True)
                checker_log_list[i] += err
                errors["Formatting error"] += 1
                save_first_error("Formatting error", i + 1)
                continue

              if equal:
                accepeted = save_ok_test(verdict, i, accepeted)
                checker_log_list[i] += "ok"

              else:
                accepeted = False
                verdict[i] = colored_text("Wrong answer", one_color="wrong", return_statement=True)
                checker_log_list[i] += wrong_answer_message
                errors["Wrong answer"] += 1
                save_first_error("Wrong answer", i + 1)
            # =========================================================================================


          # =============================================================================================

      if expected_output_bool:
        return accepeted, verdict, checker_log_list, errors_memory_time_of_solution, participant_output_filenames_list, errors_memory_time_of_solution_filenames_list
      else:
        return checker_log_list, errors_memory_time_of_solution, participant_output_filenames_list, errors_memory_time_of_solution_filenames_list


    def validate_custom_samples(
        input_samples: list[str],
        output_samples: list[str],
        input_samples_without_expected_output: list[str],
        length
    ):
        ok = True
        for i in range(length):
          try:
            output_samples.index(f"{output_extension_file}{input_samples[i][len(input_extension_file):]}")
          except ValueError:
            input_samples_without_expected_output.append(input_samples.pop(i))
            ok = False
        return ok

    custom_input_samples_num = len(self._custom_input_samples)
    input_samples_without_expected_output = []
    expected_output_bool = validate_custom_samples(self._custom_input_samples, self._expected_custom_output_samples, input_samples_without_expected_output, custom_input_samples_num)

    accepeted, verdict, checker_log_list, errors_memory_time_of_solution, participant_output_filenames_list, errors_memory_time_of_solution_filenames_list = test_solution_against_samples(self._input_samples + self._custom_input_samples, self._expected_output_samples + self._expected_custom_output_samples)

    if not expected_output_bool:
      checker_log_list_custom, errors_memory_time_of_solution_custom, participant_output_filenames_list_custom, errors_memory_time_of_solution_filenames_list_custom = test_solution_against_samples(input_samples_without_expected_output, None, False)


    # Finished testing the solution
    def print_results() -> None:

      input_samples_num = len(self._input_samples)

      if calculate_memory_usage_and_execution_time_bool:
        def extract_list(solution_resources: list[str]) -> tuple[list[float], list[float]]:
          memory = [None] * len(solution_resources)
          time = [None] * len(solution_resources)
          for i, resources in enumerate(solution_resources):
            resources = resources.split("\n")
            time[i] = round(float(resources[0][:resources[0].find(' ')]), 3)
            pos_space = resources[1].find(' ')
            # e.g. of memory item: [(123.4, "MB")]
            memory[i] = round(float(resources[1][:pos_space]), 3), resources[1][pos_space+1:]
          return memory, time

        memory, time = extract_list(errors_memory_time_of_solution)

        for i, verdict_response in enumerate(verdict):
          colored_text(
            "\n" + '\n' * (i > 0) + f"Test case {i + 1}" + ((" (Custom '" + self._custom_input_samples[i - input_samples_num] + "'),") if i >= input_samples_num else ','),
            f"time: <values>{time[i]} ms</>,",
            f"memory: <values_1>{memory[i][0]} <values_1>{memory[i][1]}</>,",
            f"verdict: {verdict_response}"
          )
          print(checker_log_list[i] * verbose)

        if not expected_output_bool:
          memory, time = extract_list(errors_memory_time_of_solution_custom)
          x = 0
          custom_input_samples_num = len(self._custom_input_samples)
          for i in range(input_samples_num + custom_input_samples_num, input_samples_num + custom_input_samples_num + len(input_samples_without_expected_output)):
            colored_text(
              "\n" + '\n' * (i > 0) + f"Test case {i + 1} (Custom '" + input_samples_without_expected_output[i - (input_samples_num + custom_input_samples_num)] + "'),",
              f"time: <values>{time[i]} ms</>,",
              f"memory: <values_1>{memory[i][0]} <values_1>{memory[i][1]}</>,",
            )
            print(checker_log_list_custom[x] * verbose)
            x += 1

      else:
        for i, verdict_response in enumerate(verdict):
          colored_text(
            "\n" + '\n' * (i > 0) + f"Test case {i + 1}" + ((" (Custom '" + self._custom_input_samples[i - input_samples_num] + "'),") if i >= input_samples_num else ','),
            f"verdict: {verdict_response}"
          )
          print(checker_log_list[i] * verbose)

        if not expected_output_bool:
          x = 0
          custom_input_samples_num = len(self._custom_input_samples)
          for i in range(input_samples_num + custom_input_samples_num, input_samples_num + custom_input_samples_num + len(input_samples_without_expected_output)):
            colored_text(
              "\n" + '\n' * (i > 0) + f"<color_red>Test case</> {i + 1} (Custom '" + input_samples_without_expected_output[i - (input_samples_num + custom_input_samples_num)] + "')",
            )
            print(checker_log_list_custom[x] * verbose)
            x += 1

    def augment_errors(errors: dict, test_results_errors_dict: dict):
      for err in errors.keys():
        if test_results_errors_dict.get(err) is not None:
          test_results_errors_dict[err] += errors[err]
        else:
          test_results_errors_dict[err] = errors[err]


    test_results_file_path = os.path.join(resources_folder, "test_samples_results.json")
    test_results: dict = read_json_file(test_results_file_path)
    # If solution get accepted
    if accepeted:
      colored_text("\nDemo accepeted", one_color="accepted")
      print_results()

      # Saving test results
      # ========================================================================
      if test_results["unsolved_problems"].get(self.problem_index) is not None:
        test_results["demo_accepted"][
          self.problem_index] = test_results["unsolved_problems"].pop(self.problem_index)
        test_results["demo_accepted"][self.problem_index]["timestamp"] = datetime.now(
          ).strftime("%Y-%m-%d %H:%M:%S")

      elif test_results["demo_accepted"].get(self.problem_index) is None:
        test_results["demo_accepted"][self.problem_index] = {}
        test_results["demo_accepted"][self.problem_index]["problem_name"] = self.name
        test_results["demo_accepted"][self.problem_index]["programming_language"] = programming_language
        test_results["demo_accepted"][self.problem_index]["timestamp"] = datetime.now(
          ).strftime("%Y-%m-%d %H:%M:%S")
        test_results["demo_accepted"][self.problem_index]["errors"] = errors
      # ========================================================================

      else:
        print("\nYou have already solved this problem!")
        augment_errors(errors, test_results["demo_accepted"][self.problem_index]["errors"])

      write_json_file(test_results, test_results_file_path, 2)

      # Removing test samples files
      # =========================================================
      if remove_samples_output_files_if_demo_accepted:
        def remove_files(file_list) -> None:
          for file in file_list:
            if isinstance(file, tuple):
              os.remove(file[0])
              os.remove(file[1])
            else:
              os.remove(file)

        remove_files(self._input_samples)
        remove_files(self._expected_output_samples)
        remove_files(participant_output_filenames_list)
        remove_files(errors_memory_time_of_solution_filenames_list)
        if not expected_output_bool:
          remove_files(errors_memory_time_of_solution_filenames_list_custom)
          remove_files(participant_output_filenames_list_custom)
      # =========================================================

    #* The solution is not correct, whether the verdict outputs 'wrong answer' or an error
    else:
      print(f"\n{self._fwrong}")
      print_results()

      if test_results["demo_accepted"].get(self.problem_index) is not None:
        augment_errors(errors, test_results["demo_accepted"][self.problem_index]["errors"])

      elif test_results["unsolved_problems"].get(self.problem_index) is None:
        test_results["unsolved_problems"][self.problem_index] = {}
        test_results["unsolved_problems"][self.problem_index]["problem_name"] = self.name
        test_results["unsolved_problems"][self.problem_index]["programming_language"] = programming_language
        test_results["unsolved_problems"][self.problem_index]["timestamp"] = datetime.now(
          ).strftime("%Y-%m-%d %H:%M:%S")
        test_results["unsolved_problems"][self.problem_index]["errors"] = errors

      else:
        augment_errors(errors, test_results["unsolved_problems"][self.problem_index]["errors"])

      write_json_file(test_results, test_results_file_path, 2)

    if working_in_script:
      os.remove("cfkit_module_user_code.py")
      if stop_program:
        sys.exit(0)

if __name__ == "__main__":
  # problem_one = Problem("1882C")
  # print(problem_one.time_limit_seconds)
  # print(problem_one.name)
  # print(problem_one.input_output_type)
  # print(problem_one.time_limit_seconds)
  # print(problem_one.memory_limit_bytes)
  # problem_one.parse()
  # Problem(("/home/ghoudiy/Documents/Programming/Python/CP/Codeforces/A_Problems/Optimization/4/2a43.py", "43A2"))
  pass