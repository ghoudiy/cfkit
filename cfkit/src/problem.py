"""
Documentation
"""
from os import path as osPath, getcwd, chdir, listdir
from sys import argv as sysArgv, exit as sysExit
from pathlib import Path
from re import search
from re import findall
from datetime import datetime
from inspect import currentframe
from subprocess import CalledProcessError, run
from collections import Counter

from cfkit.utils.common import (
  file_name,
  samples_dir,
  remove_files,
  fetch_samples,
  read_json_file,
  write_json_file,
  adjusting_paths,
  execute_solution,
  problems_content,
  retrieve_template,
  write_text_to_file,
  create_file_folder,
  read_text_from_file,
  convert_to_megabytes,
  augment_errors_warnings,
)
from cfkit.utils.input import confirm
from cfkit.utils.print import colored_text
from cfkit.config.config import set_language_attributes
from cfkit.client.fetch import get_response
from cfkit.utils.check import check_file
from cfkit.utils.check import raise_error_if_path_missing
from cfkit.utils.answer_handling import check_answer
# from cfkit.utils.check import raise_error_if_path_exists

from cfkit.utils.variables import (
  conf_file,
  resources_folder,
  language_conf_path,
  INPUT_EXTENSION_FILE,
  OUTPUT_EXTENSION_FILE
)

from cfkit.utils.constants import (
  Directory,
  LANGUAGES,
  EXTENSIONS,
  LANGUAGES_EXTENSIONS,
  PROBLEM_CODE_PATTERN,
)

class Problem:
  """
  Documentation
  """
  def __init__(self, problem_code: str | tuple[str, str] | list[str, str] = None) -> None:
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
    self.memory_limit_megabytes: float = convert_to_megabytes(self._response[4])
    self.input_output_type: str = f"input: {self._response[6]}\noutput: {self._response[8]}"

    self._data_path: str = None
    self._input_samples: list[str] = None
    self._expected_output_samples: list[str] = None
    self._custom_input_samples: list[str] = []
    self._expected_custom_output_samples: list[str] = []
    self._fwrong: str = None


  def __retrieve_html_source_code(self, code: str) -> str:
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

    colored_text(
      f"<error_4>No such problem</error_4> &apos;{code}&apos;",
      exit_code_after_print_statement=1
    )

  def __validate_parameters(self, problem_code: (tuple | str)):
    '''
    Check if the problem code is available
    '''

    if problem_code is None and sysArgv[0].endswith(".py"):
      problem_code = osPath.abspath(sysArgv[0])

    if isinstance(problem_code, str):
      # If the user gives the problem code
      if not osPath.isfile(problem_code):
        #// if osPath.isdir(problem_code):
        #//   colored_text(
        #//     "\nYou should enter a problem code or a file not a directory\n",
        #//     one_color="error_4",
        #//     exit_code_after_print_statement=1
        #//   )
        #* If the user enters a file path that does not exist
        file_extension = problem_code.rfind(".")
        if file_extension != -1 and problem_code[file_extension+1:] in EXTENSIONS:
          colored_text(
            f"\n<error_4>No such file</error_4> &apos;{problem_code}&apos;\n",
            exit_code_after_print_statement=1
          )
        content = self.__retrieve_html_source_code(problem_code)

      # If the user gives the solution file instead of problem code
      else:
        def enter_code() -> tuple[str, str]:
          '''If the problem code couldn't be recognized from the given path'''
          colored_text(
            "\nProblem code could not be recognized from the given path",
            one_color="error_4"
          )
          code = input("Please enter the problem code: ").strip()
          content = self.__retrieve_html_source_code(code)
          return content, code

        # Searching for the problem code in the given path
        base_name = osPath.basename(problem_code)
        match_problem_code_from_file_name = search(PROBLEM_CODE_PATTERN, base_name)
        if match_problem_code_from_file_name is not None: # contestIdProblemIndex.py (e.g. 1234a.py)
          match_problem_code_from_file_name = match_problem_code_from_file_name.group()
          self._solution_file = problem_code
          if confirm(f"'{match_problem_code_from_file_name}' Is this the desired problem?"):
            content = self.__retrieve_html_source_code(
              match_problem_code_from_file_name,
            )
            problem_code = match_problem_code_from_file_name
          else:
            content, problem_code = enter_code()

        else: # contestId/problem_code (e.g. 1234/a.py: where 1234 is the folder)
          dir_name = osPath.dirname(problem_code)
          if dir_name == '':
            dir_name = osPath.basename(getcwd())


          # Check if the directory name represents the contest ID and
          # the file name represents the problem code.
          if dir_name.isdigit() and (
            search(r"[A-z]\d\.", base_name) is not None  or
            search(r"[A-z]\.", base_name) is not None
          ):
            self._solution_file = problem_code
            if confirm(
              f"'{dir_name + (base_name[0] if base_name[1] == '.' else base_name[:2])}'"
              "Is this the desired problem?"
            ):
              content = self.__retrieve_html_source_code(dir_name + base_name[0])
              problem_code = dir_name + base_name[0]
            else:
              content, problem_code = enter_code()
          else:
            colored_text(
              "Could not extract the problem code from the given path",
              one_color="error_4",
              exit_code_after_print_statement=1
            )

    elif isinstance(problem_code, (tuple, list)):
      point_pos0 = problem_code[0].find(".")
      point_pos1 = problem_code[1].find(".")
      if point_pos0 != -1 and point_pos1 == -1:
        problem_code = problem_code[1], problem_code[0]
      elif (point_pos0 == -1 and point_pos1 == -1) or (point_pos0 != -1 and point_pos1 != -1):
        colored_text(
          "Please provide the problem code, the solution file itself or both.",
          one_color="error",
          exit_code_after_print_statement=1
        )

      #* Check if the path exists and is a file
      if osPath.isfile(problem_code[0]):
        self.problem_index = problem_code[0]
        self._solution_file = problem_code[1]
        content = self.__retrieve_html_source_code(problem_code[0])
        problem_code = problem_code[0]
      else:
        colored_text(
          f"\n<error_4>No such file</error_4> &apos;{problem_code[0]}&apos;\n",
          exit_code_after_print_statement=1
        )
    else:
      colored_text(
        "Problem code must be a string, tuple, or list.",
        one_color="error_4",
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
    def add_problem_name_if_demanded(
        add_problem_name_to_file_name: bool,
        problem_code: str,
        problem_name: str,
        file_extension: str
      ) -> None:
      if add_problem_name_to_file_name:
        solution_file = file_name(
          problem_name[problem_name.find(" ") + 1:],
          problem_code,
          file_extension
        )
      else:
        solution_file = problem_code + "." + file_extension
      return solution_file

    # Cheking file extension
    # =============================================================================================
    if file_extension is None:
      default_language = conf_file["cfkit"]["default_language"].strip()
      if default_language == "":
        print(
          "You should set a default language so that you don't have to",
          "enter the programming language every time"
        ) # grammar checked

      elif default_language not in LANGUAGES:
        file_extension = input("Extension: ")
        while file_extension not in EXTENSIONS:
          colored_text("Extension is not recognised! Please try again", one_color="error_4")
          file_extension = input("Extension: ")
      else:
        file_extension = LANGUAGES_EXTENSIONS[default_language][0]
    # =============================================================================================

    # Cheking path
    # ===========================================
    if path is None:
      path = getcwd()
    else:
      raise_error_if_path_missing(path, 'd')
    chdir(path)
    # ===========================================

    if create_contest_folder:
      folder_name = create_file_folder(str(self._contestid), 'd')
      chdir(folder_name)
      solution_file = add_problem_name_if_demanded(
        add_problem_name_to_file_name,
        self._problem_index_letter.lower(),
        self.name,
        file_extension
      )
    else:
      solution_file = add_problem_name_if_demanded(
        add_problem_name_to_file_name,
        f"{self._contestid}{self._problem_index_letter.lower()}",
        self.name,
        file_extension
      )

    write_text_to_file(read_text_from_file(retrieve_template(solution_file)), solution_file)

    # Grammar checked
    colored_text("The solution file has been successfully created", one_color="correct")

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
      path = getcwd()

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
        "<keyword>Samples are saved in</keyword> "
        f"&apos;{osPath.join(path, self._data_path)}&apos;" + "\n"
        "<success>Test cases parsed successfully.</success>"
      )
    else:
      fetch(path, create_tests_dir, __check_path)

  def run_demo(
    self,
    file_path: str = None,
    any_order: bool = True,
    check_formatting: bool = False,
    remove_samples_output_files_if_demo_accepted: bool = False,
    stop_program: bool = True,
    verbose: bool = True,
  ) -> None:
    """
    Test a participant's solution against Codeforces problem samples
    and download them if they are missed.
    """
    # working_in_script, code, line_number = check_path(file_path)
    def check_path(file_path) -> tuple[bool, list[str], int | bool, None, None]:
      """
      Documentation
      """
      working_in_script = False
      code = None
      line_number = None
      if file_path is not None:
        raise_error_if_path_missing(file_path, 'f')

      # When the user enter 234A problem index as a parameter in __init__
      # -------------------------------------------------------------------------------------------
      if (file_path is None) and (self._solution_file is None):
        self._solution_file = sysArgv[0]
        working_in_script = True
        # self._solution_file = check_file(input("Path of the solution file: ").strip())
      # -------------------------------------------------------------------------------------------


      # When the user enters nothing
      elif (file_path is None) and (self._solution_file is not None):
        working_in_script = True

      # When the user enter a path as a parameter in run_demo (this function) (e.g. 1234A.py)
      # -------------------------------------------------------------------------------------------
      elif (file_path is not None) and (self._solution_file is None):
        # If the file_path is the same as the working file (working in script file)
        if Path(file_path).samefile(osPath.abspath(sysArgv[0])):
          working_in_script = True
          line_number = currentframe().f_back.f_back.f_lineno
          self._solution_file = file_path
        else:
          self._solution_file = check_file(file_path)
      # -------------------------------------------------------------------------------------------


      # When the user enters two different paths
      # (one in the init method and another in the run_demo function)
      # -------------------------------------------------------------------------------------------
      elif (file_path is not None) and (self._solution_file is not None):
        file_path = Path(file_path)
        if not file_path.samefile(self._solution_file):
          colored_text(
            "You have entered different paths",
            one_color="error_4",
            exit_code_after_print_statement=1
          )
        elif file_path.samefile(osPath.abspath(sysArgv[0])):
          working_in_script = True
          line_number = currentframe().f_back.f_back.f_lineno
      # -------------------------------------------------------------------------------------------

      def input_output_list(data_path) -> None:
        list_of_files = listdir(data_path)
        self._input_samples = sorted(
          [
            file for file in list_of_files if search(
            rf"{self.problem_index}_\d+\.{INPUT_EXTENSION_FILE}", file)
          ]
        )
        self._expected_output_samples = sorted(
          [
            file for file in list_of_files if search(
            rf"{self.problem_index}_\d+\.{OUTPUT_EXTENSION_FILE}", file)
          ]
        )

        self._custom_input_samples = sorted(
          [file for file in list_of_files if search(
            r"\A" + rf"{INPUT_EXTENSION_FILE}" + r"\d{0,}$", file
          )]
        )
        self._expected_custom_output_samples = sorted(
          [file for file in list_of_files if search(
            r"\A" + rf"{OUTPUT_EXTENSION_FILE}" + r"\d{0,}$", file
          )]
        )

      del file_path # Now we have the solution file stored in self._solution_file
      cwd = getcwd()
      self._solution_file = osPath.join(cwd, self._solution_file)

      # Parse samples
      if self._data_path is None:
        self._data_path = osPath.join(cwd, 'tests')
        test = True
        if osPath.exists(self._data_path):
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

      chdir(self._data_path)
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
          write_text_to_file("".join(code), osPath.join(getcwd(), "cfkit_module_user_code.py"))
        else:
          # Modify the participant's code by removing the 'import cfkit' package line (BETA)
          for j in range(len(code[:line_number-1])):
            module_position = code[j].find("cfkit")

            if module_position != -1:
              import_keyword_position = code[j].find("import")
              comma_position = code[j].find(",")
              from_keyword_position = code[j].find("from")
              if (
                import_keyword_position != -1 and
                import_keyword_position < module_position and
                comma_position == -1
              ) or (
                from_keyword_position != -1 and from_keyword_position < module_position
              ) :
                code[j] = f"# {code[j]}\n"

              # e.g. import math, cfkit
              elif (
                import_keyword_position != -1 and
                comma_position != -1 and
                import_keyword_position < module_position
              ):
                import_line_list = code[j].split(",")
                i = 0
                while i < len(import_line_list):
                  import_line_list[i] = (
                    "" if import_line_list[i].find("cfkit") > -1 else import_line_list[i]
                  )
                  i = i + 1
                code[j] = "import " if import_line_list[0].find("import") == -1 else "" + ", ".join(
                  [x for x in import_line_list if x]) + "\n"

          write_text_to_file(
            "".join(code[:line_number-1] + code[line_number:]),
            osPath.join(getcwd(), "cfkit_module_user_code.py")
          )

      return working_in_script

    working_in_script = check_path(file_path)

    # Retrieve the execution and compile commands
    # =============================================================================================
    ext = self._solution_file[self._solution_file.rfind(".")+1:]
    if ext == self._solution_file:
      colored_text("\nPlease add the appropriate file extension to the file name. "
        "This ensures accurate language identification. ",
        one_color="error",
        exit_code_after_print_statement=1
      )

    programming_language = EXTENSIONS.get(ext)
    if programming_language is None:
      colored_text(
        "Oops! It looks like that the provided language is not supported by Codeforces.",
        one_color="error_4",
        exit_code_after_print_statement=1
      )

    language_conf = read_json_file(language_conf_path)
    compile_command = language_conf[programming_language].get("compile_command")
    execute_command = language_conf[programming_language].get("execute_command")
    calculate_memory_usage_and_execution_time_command = (
      language_conf[programming_language].get("calculate_memory_usage_and_execution_time_command")
    )
    if (execute_command is None) or (calculate_memory_usage_and_execution_time_command is None):
      (
        compile_command,
        execute_command,
        calculate_memory_usage_and_execution_time_command
      ) = set_language_attributes(programming_language)

    mem_time_calc = conf_file["cfkit"][
      "calculate_memory_usage_and_execution_time"]

    if mem_time_calc == "false":
      execute_command += " < %%{input_file}%% > %%{output_file}%% 2> %%{time_mem_err_output_file}%%"
      
      mem_time_calc = False
    else:
      execute_command = calculate_memory_usage_and_execution_time_command
      mem_time_calc = True
      warnings = {
        "Memory limit exceeded": 0,
        "Time limit exceeded": 0,
      }

    errors = {
      "Wrong answer": 0,
      "Compilation error": 0,
      "Runtime error": 0,
      "Formatting error": 0
    }
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
        )
      except CalledProcessError as err:
        errors["Compilation error"] = 1
        colored_text(
          f"\n<error_1>Compilation error</error_1>\n<keyword>Command:</keyword> `{err.cmd}` "
          f"returned non-zero exit status: <bright_text>{err.returncode}</bright_text>",
          exit_code_after_print_statement=1
        )

    def fill_checker_log_list(checker_log_list: list[str], data: list[str], i: int):
      """
      Documentation
      """
      if (data_length:=len(data)) > 1 and data[-1] == "":
        data.pop()
      elif data_length == 1 and data[-1] == "":
        data = ["(Empty)"]
      for line in data:
        checker_log_list[i] += f"| {line} {' ' * (55 - len(line) - 2)}|\n"

    def save_accepted_test(verdict, checker_log_list, i, solution_accpeted):
      """
      Documentation
      """
      solution_accpeted = solution_accpeted and True
      checker_log_list[i] += "ok"
      verdict[i] = "<correct>OK</correct>"
      return solution_accpeted

    def save_error(
        error: str,
        verdict: list[str],
        i: int,
        one_color: str,
        errors: dict,
        checker_log_message: str,
        checker_log_list: list[str],
        start: int
      ) -> bool:
      """
      Documentation
      """
      verdict[i] = f"<{one_color}>{error}</{one_color}>"
      checker_log_list[i] += checker_log_message
      errors[error] += 1
      if self._fwrong is None:
        self._fwrong = f"<{one_color}>{error} on test {i + 1 + start}</{one_color}>"
      return False

    def check_exit_code_and_empty_output(
        exitcode: int,
        observed: str,
        warning_error: str,
        warning_error_color: str,
        i: int,
      ):
      """
      Check if the exit code is non-zero. If the exit code is zero,
      check if the observed output is empty.

      This function combines these checks for better performance by
      avoiding unnecessary checks when an error is already detected.
      """
      if exitcode != 0:
        colored_text(f"<error>Error:</error> Cannot finish executing file on test {i}")
        raise InterruptedError(["Runtime error", f"Exit code is {exitcode}", "error_2"])

      #* Check if the output is empty
      observed_len = 0
      for line in observed:
        observed_len += 1 if line else 0

      if observed_len == 0:
        colored_text(
          "\n" + f"<{warning_error_color}>{warning_error}:</{warning_error_color}> No output was generated in test {i}"
        )
        return True
      return False


    # =============================================================================================
    def test_solution_against_samples(
      input_samples_list: list[str],
      expected_output_samples: list[str] = None,
      expected_output_bool: bool = True,
      start: int = 0
    ):
      number_of_tests = len(input_samples_list)
      checker_log_list: list[str] = [None] * number_of_tests
      errors_memory_time_of_solution_filenames_list: list[str] = [None] * number_of_tests
      participant_output_filenames_list: list[str] = [None] * number_of_tests

      accepeted = True
      verdict = [None] * number_of_tests * expected_output_bool
      errors_memory_time_of_solution: list[str] = [None] * number_of_tests * mem_time_calc

      #* Loop through samples
      # =============================================================================
      for i, input_sample in enumerate(input_samples_list):
        input_sample = adjusting_paths(
          self.problem_index,
          input_sample,
          i,
          participant_output_filenames_list,
          errors_memory_time_of_solution_filenames_list,
          self._data_path,
          start
        )

        exitcode = execute_solution(
          self._solution_file,
          self.problem_index,
          execute_command,
          input_sample,
          participant_output_filenames_list[i],
          errors_memory_time_of_solution_filenames_list[i],
          working_in_script
        )

        if mem_time_calc:
          errors_memory_time_of_solution[i] = read_text_from_file(
            errors_memory_time_of_solution_filenames_list[i]
          ) # To use it later in printing results

        observed = read_text_from_file(participant_output_filenames_list[i])
        while len(observed) > 0 and observed[-1] == "\n":
          observed = observed[:-1]
        observed_without_nl = observed.replace(" \n", " ").replace("\n", " ")
        observed = observed.split("\n")

        checker_log_list[i] = f"Input\n {'-' * 55}\n"
        fill_checker_log_list(checker_log_list, read_text_from_file(input_sample).split("\n"), i)

        checker_log_list[i] += f" {'-' * 55}\n\nOutput\n {'-' * 55}\n"
        fill_checker_log_list(checker_log_list, observed, i)

        try:
          if not expected_output_bool:
            checker_log_list[i] += " " + "-" * 55 + "\n"
            try:
              check_exit_code_and_empty_output(exitcode, observed, "Warning", "warning", i + 1 + start)
            except InterruptedError:
              continue # To prevent save error in the main except statement
          else:
            expected = read_text_from_file(expected_output_samples[i])
            while len(expected) > 0 and expected[-1] == "\n":
              expected = expected[:-1]
            expected_without_nl = expected.replace(" \n", " ").replace("\n", " ")
            expected = expected.split("\n")

            checker_log_list[i] += f" {'-' * 55}\n\nAnswer\n {'-' * 55}\n"
            fill_checker_log_list(checker_log_list, expected, i)
            checker_log_list[i] += f" {'-' * 55}\nChecker log: "

            if (
              len(expected) > 0 and
              check_exit_code_and_empty_output(exitcode, observed, "Error", "error", i + 1 + start)
            ):
              accepeted = save_error(
                "Wrong answer",
                verdict,
                i,
                "wrong",
                errors,
                "No output was generated",
                checker_log_list,
                start
              )
              continue

            #* Compare the results if the output is an integer or a string
            if expected_without_nl == observed_without_nl or (
              any_order and
              Counter(expected_without_nl.split(" ")) == Counter(observed_without_nl.split(" "))
            ):
              accepeted = save_accepted_test(verdict, checker_log_list, i, accepeted)
            
            #* In case of wrong answer and results are floating point numbers
            else:
              expected = [item for item in expected if item]
              observed = [item for item in observed if item]

              # This line could raise an InterruptedError
              equal, wrong_answer_message = check_answer(expected, observed, check_formatting)

              if equal:
                accepeted = save_accepted_test(verdict, checker_log_list, i, accepeted)

              else:
                accepeted = save_error(
                  "Wrong answer",
                  verdict,
                  i,
                  "wrong",
                  errors,
                  wrong_answer_message,
                  checker_log_list,
                  start
                )

        except InterruptedError as err:
          err.args = err.args[0]
          # err.args[0]: error type, err.args[1]: message, err.args[2]: one_color
          accepeted = save_error(
            err.args[0], # Could be Runtime error, Wrong answer or Formatting error
            verdict,
            i,
            err.args[2],
            errors,
            err.args[1],
            checker_log_list,
            start
          )

      return (
        accepeted,
        verdict,
        checker_log_list,
        errors_memory_time_of_solution,
        participant_output_filenames_list,
        errors_memory_time_of_solution_filenames_list
      )


    def validate_custom_samples(
        input_samples: list[str],
        output_samples: list[str],
        input_samples_without_expected_output: list[str],
        length
    ):
      custom_input_without_expected_output_bool = True
      i = 0
      while i < length:
        try:
          output_samples.index(
            f"{OUTPUT_EXTENSION_FILE}{input_samples[i][len(INPUT_EXTENSION_FILE):]}"
          )
          i += 1
        except ValueError:
          input_samples_without_expected_output.append(input_samples.pop(i))
          length -= 1
          custom_input_without_expected_output_bool = False
      return custom_input_without_expected_output_bool

    custom_input_samples_num = len(self._custom_input_samples)
    input_samples_without_expected_output = []
    expected_output_bool = validate_custom_samples(
      self._custom_input_samples,
      self._expected_custom_output_samples,
      input_samples_without_expected_output,
      custom_input_samples_num
    )

    # Remove extra output samples (their name doesn't correspond to any input sample)
    i = 0
    expected_custom_output_samples_num = len(self._expected_custom_output_samples)
    while i < expected_custom_output_samples_num:
      try:
        self._custom_input_samples.index(
          f"{INPUT_EXTENSION_FILE}{self._expected_custom_output_samples[i][len(OUTPUT_EXTENSION_FILE):]}"
        )
        i += 1
      except ValueError:
        self._expected_custom_output_samples.pop(i)
        expected_custom_output_samples_num -= 1

    (
      accepeted,
      verdict,
      checker_log_list,
      errors_memory_time_of_solution,
      participant_output_filenames_list,
      errors_memory_time_of_solution_filenames_list
    ) = test_solution_against_samples(
      self._input_samples + self._custom_input_samples,
      self._expected_output_samples + self._expected_custom_output_samples
    )

    input_samples_num = len(self._input_samples)
    input_samples_with_expected_output_num = len(self._custom_input_samples) + input_samples_num
    if not expected_output_bool:
      (
        _,
        _,
        checker_log_list_custom,
        errors_memory_time_of_solution_custom,
        participant_output_filenames_list_custom,
        errors_memory_time_of_solution_filenames_list_custom
      ) = test_solution_against_samples(
        input_samples_without_expected_output,
        None,
        False,
        input_samples_with_expected_output_num
      )

    # Finished testing the solution
    def print_results() -> None:

      input_samples_without_expected_output_num = len(input_samples_without_expected_output)

      if mem_time_calc:
        def extract_list(solution_resources: list[str]) -> tuple[list[float], list[float]]:
          memory = [None] * len(solution_resources)
          time = [None] * len(solution_resources)
          for i, resources in enumerate(solution_resources):
            resources = resources.split("\n")
            time[i] = float(resources[0][8:-3])
            pos_space = resources[1].rfind(' ')
            # e.g. of memory item: [(123.4, "MB")]
            memory[i] = float(resources[1][8:pos_space]), resources[1][pos_space + 1:]
          return memory, time

        def check_memory_time(memory_taken: float, memory_unit: str, time_taken: float):
          if memory_unit == "KB":
            memory_taken /= 1024
          elif memory_unit == "B":
            memory_taken /= 1048576

          memory_exceeded_limit_message = ""
          if memory_taken > self.memory_limit_megabytes:
            memory_exceeded_limit_message = " (Memory limit exceeded)"
            warnings["Memory limit exceeded"] += 1

          time_limit_exceeded_message = ""
          if time_taken > self.time_limit_seconds_number * 1000:
            time_limit_exceeded_message = " (Time limit exceeded)"
            warnings["Time limit exceeded"] += 1

          return time_limit_exceeded_message, memory_exceeded_limit_message

        memory, time = extract_list(errors_memory_time_of_solution)

        for i, verdict_response in enumerate(verdict):
          time_limit_exceeded_message, memory_limit_exceeded_message = check_memory_time(
            memory[i][0],
            memory[i][1],
            time[i]
          )
          colored_text(
            "\n" + '\n' * (i > 0) + f"<keyword>Test case</keyword> <values>{i + 1}</values>"
            f"{(' (Custom &apos;' + self._custom_input_samples[i - input_samples_num] + '&apos;), ') if i >= input_samples_num else ', '}"
            f"time: <values_1>{time[i]} ms</values_1>{time_limit_exceeded_message}, "
            f"memory: <values_2>{memory[i][0]} {memory[i][1]}</values_2>"
            f"{memory_limit_exceeded_message}, "
            f"verdict: {verdict_response}"
          )
          print(checker_log_list[i] * verbose)

        if not expected_output_bool:
          memory, time = extract_list(errors_memory_time_of_solution_custom)
          for i in range(
            input_samples_with_expected_output_num,
            input_samples_with_expected_output_num + input_samples_without_expected_output_num
          ):
            aux = i - input_samples_with_expected_output_num
            time_limit_exceeded_message, memory_limit_exceeded_message = check_memory_time(
              memory[aux][0],
              memory[aux][1],
              time[aux]
            )
            colored_text(
              "\n" + "\n" * (i > 0) + f"<keyword>Test case</keyword> <values>{i + 1}</values>"
              " (Custom &apos;" + input_samples_without_expected_output[aux] + "&apos;), "
              f"time: <values_1>{time[aux]} ms</values_1>{time_limit_exceeded_message}, "
              f"memory: <values_2>{memory[aux][0]} {memory[aux][1]}</values_2>"
              f"{memory_limit_exceeded_message}"
            )
            print(checker_log_list_custom[aux] * verbose)

      else:
        for i, verdict_response in enumerate(verdict):
          colored_text(
            "\n" + '\n' * (i > 0) + f"<keyword>Test case</keyword> <values>{i + 1}</values>"
            f"{(' (Custom &apos;' + self._custom_input_samples[i - input_samples_num] + '&apos;), ') if i >= input_samples_num else ', '}"
            f"verdict: {verdict_response}"
          )
          print(checker_log_list[i] * verbose)

        if not expected_output_bool:
          for i in range(
            input_samples_with_expected_output_num,
            input_samples_with_expected_output_num + input_samples_without_expected_output_num
          ):
            aux = i - input_samples_with_expected_output_num
            colored_text(
              "\n" + "\n" * (i > 0) + f"<keyword>Test case</keyword> <values>{i + 1}</values>"
              " (Custom &apos;" + input_samples_without_expected_output[aux] + "&apos;)"
            )
            print(checker_log_list_custom[aux] * verbose)

    test_results_file_path = osPath.join(resources_folder, "test_samples_results.json")
    test_results: dict = read_json_file(test_results_file_path)
    if mem_time_calc:
      def augment_warnings(warnings: dict, test_results: dict):
        if (mem_time_calc and test_results.get("warnings") is not None):
          augment_errors_warnings(warnings, test_results["warnings"])
        elif (mem_time_calc and test_results.get("warnings") is None):
          test_results["warnings"] = warnings
        return test_results["warnings"]

    # If solution get accepted
    if accepeted:
      print_results()
      colored_text("\n\nVerdict: <accepted>Demo accepeted</accepted>")

      # Saving test results
      # ========================================================================
      if test_results["unsolved_problems"].get(self.problem_index) is not None:
        test_results["demo_accepted"][
          self.problem_index] = test_results["unsolved_problems"].pop(self.problem_index)
        test_results["demo_accepted"][self.problem_index]["timestamp"] = datetime.now(
          ).strftime("%Y-%m-%d %H:%M:%S")
        if mem_time_calc:
          test_results["demo_accepted"][self.problem_index]["warnings"] = augment_warnings(
            warnings,
            test_results["demo_accepted"][self.problem_index]
        )

      elif test_results["demo_accepted"].get(self.problem_index) is None:
        test_results["demo_accepted"][self.problem_index] = {}
        test_results["demo_accepted"][self.problem_index]["problem_name"] = self.name
        test_results["demo_accepted"][self.problem_index]["programming_language"] = programming_language
        test_results["demo_accepted"][self.problem_index]["timestamp"] = datetime.now(
          ).strftime("%Y-%m-%d %H:%M:%S")
        test_results["demo_accepted"][self.problem_index]["errors"] = errors
        if mem_time_calc:
          test_results["demo_accepted"][self.problem_index]["warnings"] = warnings

      # ========================================================================

      else:
        print("\nYou have already solved this problem!")
        augment_errors_warnings(errors, test_results["demo_accepted"][self.problem_index]["errors"])
        if mem_time_calc:
          test_results["demo_accepted"][self.problem_index]["warnings"] = augment_warnings(
            warnings,
            test_results["demo_accepted"][self.problem_index]
          )

      write_json_file(test_results, test_results_file_path, 2)

      # Removing test samples files
      # =========================================================
      if remove_samples_output_files_if_demo_accepted:

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
      print_results()
      colored_text(f"\n\nVerdict: {self._fwrong}")

      if test_results["demo_accepted"].get(self.problem_index) is not None:
        augment_errors_warnings(errors, test_results["demo_accepted"][self.problem_index]["errors"])
        if mem_time_calc:
          test_results["demo_accepted"][self.problem_index]["warnings"] = augment_warnings(
            warnings,
            test_results["demo_accepted"][self.problem_index]
          )

      elif test_results["unsolved_problems"].get(self.problem_index) is None:
        test_results["unsolved_problems"][self.problem_index] = {}
        test_results["unsolved_problems"][self.problem_index]["problem_name"] = self.name
        test_results["unsolved_problems"][self.problem_index]["programming_language"] = programming_language
        test_results["unsolved_problems"][self.problem_index]["timestamp"] = datetime.now(
          ).strftime("%Y-%m-%d %H:%M:%S")
        test_results["unsolved_problems"][self.problem_index]["errors"] = errors
        if mem_time_calc:
          test_results["unsolved_problems"][self.problem_index]["warnings"] = warnings

      else:
        augment_errors_warnings(
          errors,
          test_results["unsolved_problems"][self.problem_index]["errors"]
        )
        if mem_time_calc:
          test_results["unsolved_problems"][self.problem_index]["warnings"] = augment_warnings(
          warnings,
          test_results["unsolved_problems"][self.problem_index]
        )

      write_json_file(test_results, test_results_file_path, 2)

    if working_in_script:
      if stop_program:
        sysExit(0)
      # os.remove("cfkit_module_user_code.py")

if __name__ == "__main__":
  pass
