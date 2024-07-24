"""
Documentation
"""
from os import path as osPath, getcwd, chdir, listdir, remove as osRemove
from sys import argv as sysArgv, exit as sysExit
from pathlib import Path
from re import search, findall, compile as reCompile
from datetime import datetime
from inspect import currentframe
from typing import Optional
from subprocess import CalledProcessError, run

from cfkit._utils.common import (
  file_name,
  execute_file,
  adjusting_paths,
  retrieve_template,
  convert_to_megabytes,
  augment_errors_warnings,
)

from cfkit._utils.parse_samples import samples_dir, fetch_samples, problems_content
from cfkit._utils.file_operations import (
  remove_files,
  read_json_file,
  write_json_file,
  write_text_to_file,
  read_text_from_file,
  create_file_folder
)
from cfkit._utils.input import confirm
from cfkit._utils.print import colored_text
from cfkit._config.config import set_language_attributes
from cfkit._client.fetch import get_response
from cfkit._utils.check import check_file, raise_error_if_path_missing
from cfkit._utils.answer_handling import check_answer


from cfkit._utils.variables import (
  conf_file,
  resources_folder,
  config_folder,
  language_conf_path,
  INPUT_FILENAME_PATTERN,
  EXPECTED_OUTPUT_FILENAME_PATTERN,
  CUSTOM_INPUT_FILENAME,
  CUSTOM_OUTPUT_FILENAME,
  CUSTOM_INPUT_FILENAME_PATTERN,
  CUSTOM_OUTPUT_FILENAME_PATTERN
)

from cfkit._utils.constants import (
  Directory,
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

    self._time_limit_seconds: float = None
    self._memory_limit_megabytes: float = None
    self._input_output_type: str = None
    self._data_path: str = None
    self._input_samples: list[str] = []
    self._expected_output_samples: list[str] = []
    self._custom_input_samples: list[str] = []
    self._expected_custom_output_samples: list[str] = []
    self._fwrong: str = None


  @property
  def name(self) -> str:
    """
    Documentation
    """
    return self._response[0]

  @property
  def time_limit_seconds(self) -> float:
    """
    Documentation
    """
    self._time_limit_seconds: float = float(self._response[1][21:self._response[1].rfind(" ")])
    return self._time_limit_seconds

  @property
  def memory_limit_megabytes(self) -> float:
    """
    Documentation
    """
    self._memory_limit_megabytes: float = convert_to_megabytes(self._response[2][23:])
    return self._memory_limit_megabytes

  @property
  def input_output_type(self) -> str:
    """
    Documentation
    """
    self._input_output_type: str = f"{self._response[3]}\n{self._response[4]}"
    return self._input_output_type


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
      exit_code_after_print_statement=4
    )

  def __validate_parameters(self, problem_code: str | tuple[str, str] | list[str, str] | None):
    '''
    Check if the problem code is available
    '''

    if problem_code is None and sysArgv[0].endswith(".py"):
      problem_code = osPath.abspath(sysArgv[0])

    if isinstance(problem_code, str):
      # If the user gives the problem code
      if not osPath.isfile(problem_code):
        #* If the user enters a file path that does not exist
        file_extension = problem_code.rfind(".")

        if file_extension != -1 and problem_code[file_extension+1:] in EXTENSIONS:
          colored_text(
            f"\n<error_4>No such file</error_4> &apos;{problem_code}&apos;\n",
            exit_code_after_print_statement=4
          )
        
        elif file_extension == -1 and (contestid:=osPath.basename(getcwd())).isdigit() and 1 <= int(contestid) <= 9999:
          problem_code = f"{contestid}{problem_code}"
        
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
          if dir_name.isdigit() and search(r"[A-z]\d{,2}\.", base_name) is not None:
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
              exit_code_after_print_statement=4
            )

    elif isinstance(problem_code, (tuple, list)):
      pos_point = problem_code[0].find(".")
      pos_point_1 = problem_code[1].find(".")
      if pos_point != -1 and pos_point_1 == -1:
        problem_code = problem_code[1], problem_code[0]
      elif (pos_point == -1 and pos_point_1 == -1) or (pos_point != -1 and pos_point_1 != -1):
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
          exit_code_after_print_statement=4
        )
    else:
      colored_text(
        "Problem code must be a string, tuple, or list.",
        one_color="error_4",
        exit_code_after_print_statement=4
      )
    return content, problem_code.upper()

  def create_solution_file(
      self,
      path: Optional[Directory] = None,
      file_extension: Optional[str] = None,
      create_contest_folder: bool = False,
      add_problem_name_to_file_name: bool = True
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
        )
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
    path: Optional[Directory] = None,
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
      self._data_path = samples_dir(create_tests_dir, path)

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
    file_path: Optional[str] = None,
    any_order: bool = False,
    multiple_answers: bool = False,
    check_formatting: bool = False,
    run_custom_samples_only: bool = False,
    print_answers: bool = True,
    remove_samples_output_files_if_demo_accepted: bool = False,
    stop_program: bool = True,
    verbose: bool = True
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
      # -------------------------------------------------------------------------------------------
      elif (file_path is None) and (self._solution_file is not None):
        working_in_script = True
      # -------------------------------------------------------------------------------------------

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
            exit_code_after_print_statement=4
          )
        # elif file_path.samefile(osPath.abspath(sysArgv[0])):
        #   working_in_script = True
        #   line_number = currentframe().f_back.f_back.f_lineno
      # -------------------------------------------------------------------------------------------

      def input_output_list(
        data_path,
        INPUT_FILENAME_PATTERN,
        EXPECTED_OUTPUT_FILENAME_PATTERN,
        CUSTOM_INPUT_FILENAME_PATTERN,
        CUSTOM_OUTPUT_FILENAME_PATTERN
      ) -> None:
        list_of_files = listdir(data_path)
        if run_custom_samples_only is False:
          INPUT_FILENAME_COMPILED_PATTERN = reCompile(rf"\A{INPUT_FILENAME_PATTERN.replace('%%problem_code%%', self.problem_index)}$")
          EXPECTED_OUTPUT_FILENAME_COMPILED_PATTERN = reCompile(rf"\A{EXPECTED_OUTPUT_FILENAME_PATTERN.replace('%%problem_code%%', self.problem_index)}$")

          self._input_samples = sorted(
            [file for file in list_of_files if INPUT_FILENAME_COMPILED_PATTERN.search(file)]
          )
          self._expected_output_samples = sorted(
            [file for file in list_of_files if EXPECTED_OUTPUT_FILENAME_COMPILED_PATTERN.search(file)]
          )

        CUSTOM_INPUT_FILENAME_COMPILED_PATTERN = reCompile(rf"\A{CUSTOM_INPUT_FILENAME_PATTERN.replace('%%problem_code%%', self.problem_index)}$")
        CUSTOM_OUTPUT_FILENAME_COMPILED_PATTERN = reCompile(rf"\A{CUSTOM_OUTPUT_FILENAME_PATTERN.replace('%%problem_code%%', self.problem_index)}$")
        
        self._custom_input_samples = sorted(
          [file for file in list_of_files if CUSTOM_INPUT_FILENAME_COMPILED_PATTERN.search(file)]
        )
        self._expected_custom_output_samples = sorted(
          [file for file in list_of_files if CUSTOM_OUTPUT_FILENAME_COMPILED_PATTERN.search(file)]
        )


      del file_path # Now we have the solution file stored in self._solution_file
      cwd = getcwd()
      self._solution_file = osPath.join(cwd, self._solution_file)

      # Parse samples
      if self._data_path is None:
        self._data_path = osPath.join(cwd, 'tests')
        test = True
        if osPath.exists(self._data_path):
          input_output_list(
            self._data_path,
            INPUT_FILENAME_PATTERN,
            EXPECTED_OUTPUT_FILENAME_PATTERN,
            CUSTOM_INPUT_FILENAME_PATTERN,
            CUSTOM_OUTPUT_FILENAME_PATTERN
          )
          if (run_custom_samples_only is False) and (
            (input_samples_num:=len(self._input_samples)) > 0 and input_samples_num == len(self._expected_output_samples)
          ):
            test = False
            del input_samples_num

        if test and run_custom_samples_only is False:
          # Here where I got the idea of adding __check_path parameter in parse function
          # To prevent checking the path again
          self.parse(cwd, True, False, False, False)

      else:
        input_output_list(self._data_path)

      chdir(self._data_path)
      # If working with the solution file itself and it's a python file
      if working_in_script:
        with open(self._solution_file, 'r', encoding="UTF-8") as file:
          code = file.read().split("\n")

        # Searching for the beginning of the solution
        solution_pos = None
        code_length = len(code)
        end_pos = code_length
        for i in range(code_length):
          line_without_spaces = code[i].replace(" ", "")
          last_line_without_spaces = code[code_length - i - 1].replace(" ", "")

          if line_without_spaces == "#solution":
            solution_pos = i

          if last_line_without_spaces == "#end":
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
        exit_code_after_print_statement=4
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
      "calculate_memory_usage_and_execution_time"].strip().lower()

    if mem_time_calc == "false":
      execute_command += " < %%{input_file}%% > %%{output_file}%% 2> %%{time_mem_err_output_file}%%"

      mem_time_calc = False
    elif mem_time_calc == "true":
      execute_command = calculate_memory_usage_and_execution_time_command
      mem_time_calc = True
      warnings = {
        "Memory limit exceeded": 0,
        "Time limit exceeded": 0,
      }
    else:
      colored_text(
        "The calculate_memory_usage_and_execution_time option must have a value of either "
        "`true` or `false`",
        exit_code_after_print_statement=6
      )

    errors = {
      "Wrong answer": 0,
      "Compilation error": 0,
      "Runtime error": 0,
      "Formatting error": 0
    }
    # =============================================================================================
    
    test_results_file_path = osPath.join(config_folder, "test_samples_results.json")
    test_results: dict = read_json_file(test_results_file_path)
    test_results["progress"]["total_attempts"] += 1
    if mem_time_calc:
      def augment_warnings(warnings: dict, test_results: dict):
        if (mem_time_calc and test_results.get("warnings") is not None):
          augment_errors_warnings(warnings, test_results["warnings"])
        elif (mem_time_calc and test_results.get("warnings") is None):
          test_results["warnings"] = warnings
        return test_results["warnings"]

    def move_programming_language_to_right(programming_language, key):
      if programming_language in test_results[key][self.problem_index]["programming_language"] and test_results[key][self.problem_index]["programming_language"][-1] != programming_language:
        test_results[key][self.problem_index]["programming_language"].remove(programming_language)
        test_results[key][self.problem_index]["programming_language"].append(programming_language)

    def save_non_accepted_test_result():
      # Saving test results
      # ===========================================================================================
      if test_results["demo_accepted"].get(self.problem_index) is not None:
        move_programming_language_to_right(programming_language, "demo_accepted")
        augment_errors_warnings(errors, test_results["demo_accepted"][self.problem_index]["errors"])
        if mem_time_calc:
          test_results["demo_accepted"][self.problem_index]["warnings"] = augment_warnings(
            warnings,
            test_results["demo_accepted"][self.problem_index]
          )

      elif test_results["unsolved_problems"].get(self.problem_index) is None:
        test_results["unsolved_problems"][self.problem_index] = {}
        test_results["unsolved_problems"][self.problem_index]["problem_name"] = self.name
        test_results["unsolved_problems"][self.problem_index]["programming_language"] = [programming_language]
        test_results["unsolved_problems"][self.problem_index]["timestamp"] = datetime.now(
          ).strftime("%Y-%m-%d %H:%M:%S")
        test_results["unsolved_problems"][self.problem_index]["errors"] = errors
        if mem_time_calc:
          test_results["unsolved_problems"][self.problem_index]["warnings"] = warnings

      else:
        move_programming_language_to_right(programming_language, "unsolved_problems")
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
      # ===========================================================================================

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
        save_non_accepted_test_result()
        write_json_file(test_results, test_results_file_path, 2)
        colored_text(
          f"\n<error_1>Compilation error</error_1>\n<keyword>Command:</keyword> `{err.cmd}` "
          f"returned non-zero exit status: <bright_text>{err.returncode}</bright_text>",
          exit_code_after_print_statement=1
        )
      else:
        colored_text("Compilation is done", one_color="correct")
    # =============================================================================================


    def fill_checker_log_list(
      checker_log_list: list[str],
      data: list[str],
      i: int,
      columns_num: int = 55
    ):
      """
      Documentation
      """
      if (data_length:=len(data)) > 1 and data[-1] == "":
        data.pop()
      elif data_length == 1 and data[-1] == "":
        data = ["(Empty)"]
      for line in data:
        checker_log_list[i] += f"| {line} {' ' * (columns_num - len(line) - 2)}|\n"

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
      if len(observed) == 0:
        colored_text(
          "\n" + f"<{warning_error_color}>{warning_error}:</{warning_error_color}> "
          f"No output was generated in test {i}"
        )
        return True
      return False

    def execute_solution(
        solution_file: str,
        problem_index: str,
        execute_command: str,
        input_sample: str,
        participant_output_path: str,
        errors_memory_time_of_solution_filename: str,
        working_in_script: bool
      ):
      if working_in_script:
        solution_file = "cfkit_module_user_code.py"

      return execute_file(
        solution_file,
        problem_index,
        input_sample,
        participant_output_path,
        errors_memory_time_of_solution_filename,
        execute_command
      )

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
      errors_memory_time_of_solution: list[str] = [None] * number_of_tests

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

        errors_memory_time_of_solution[i] = read_text_from_file(
          errors_memory_time_of_solution_filenames_list[i]
        ) # To use it later in printing results

        observed = read_text_from_file(participant_output_filenames_list[i]).split("\n")

        checker_log_list[i] = f"Input\n {'-' * 55}\n"
        fill_checker_log_list(checker_log_list, read_text_from_file(input_sample).split("\n"), i)

        checker_log_list[i] += f" {'-' * 55}\n\nOutput\n {'-' * 55}\n"
        fill_checker_log_list(checker_log_list, observed, i)

        try:
          if not expected_output_bool:
            checker_log_list[i] += " " + "-" * 55
            try:
              check_exit_code_and_empty_output(exitcode, observed, "Warning", "warning", i + 1 + start)
            except InterruptedError:
              continue # To prevent save error in the main except statement

          else:
            expected_str = read_text_from_file(expected_output_samples[i])
            expected = expected_str.split("\n")
            # Remove the content of the variable if multiple_answers is False (for better performance)
            expected_str = expected_str * multiple_answers

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

            # This line could raise an InterruptedError
            equal, wrong_answer_message = check_answer(
              expected,
              observed,
              any_order,
              multiple_answers,
              check_formatting,
              expected_str
            )

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
          if err.args[0] == "Runtime error":
            checker_log_list[i] += f"\n\nDiagnostics\n {'-' * 70}\n"
            fill_checker_log_list(
              checker_log_list,
              errors_memory_time_of_solution[i].split("\n")[2 * mem_time_calc:],
              i,
              70
            )
            checker_log_list[i] += f" {'-' * 70}"


      return (
        accepeted,
        verdict,
        checker_log_list,
        errors_memory_time_of_solution,
        participant_output_filenames_list,
        errors_memory_time_of_solution_filenames_list
      )


    if run_custom_samples_only:
      self._input_samples = []
      self._expected_output_samples = []

    if print_answers:
      def validate_custom_samples(
        data1: list[str],
        data2: list[str],
        func,
        length: int,
        filename1: str,
        filename2: str
      ):
        # Remove extra samples (their name doesn't correspond to any input/output sample)
        custom_input_without_expected_output_bool = True
        i = 0
        while i < length:
          try:
            test_case_num_of_custom_input = filename1.find("%%test_case_num%%")
            prefix = filename1[:test_case_num_of_custom_input]
            suffix = filename1[test_case_num_of_custom_input + 17:]
            suffix = data1[i].find(suffix) if suffix else len(data1[i])
            data2.index(
              filename2.replace("%%test_case_num%%", data1[i][len(prefix):suffix])
            )
            i += 1
          except ValueError:
            func(data1.pop(i))
            length -= 1
            custom_input_without_expected_output_bool = False
        return custom_input_without_expected_output_bool, length


      input_samples_without_expected_output = []
      custom_input_without_expected_output_bool, input_samples_with_expected_output_num = validate_custom_samples(
        self._custom_input_samples,
        self._expected_custom_output_samples,
        lambda x: input_samples_without_expected_output.append(x),
        len(self._custom_input_samples),
        CUSTOM_INPUT_FILENAME,
        CUSTOM_OUTPUT_FILENAME
      )

      validate_custom_samples(
        self._expected_custom_output_samples,
        self._custom_input_samples,
        lambda x: None,
        len(self._expected_custom_output_samples),
        CUSTOM_OUTPUT_FILENAME,
        CUSTOM_INPUT_FILENAME
      )

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
      input_samples_with_expected_output_num = input_samples_with_expected_output_num + input_samples_num
    else:
      input_samples_with_expected_output_num = 0
      input_samples_without_expected_output = self._input_samples + self._custom_input_samples
      accepeted = None
      custom_input_without_expected_output_bool = False

    if not custom_input_without_expected_output_bool:
      (
        _,
        _,
        checker_log_list_no_expec_out,
        err_mem_time_of_sol_no_expec_out,
        participant_output_filenames_list_no_expec_out,
        err_mem_time_of_sol_filenames_list_no_expec_out
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
          if time_taken > self.time_limit_seconds * 1000:
            time_limit_exceeded_message = " (Time limit exceeded)"
            warnings["Time limit exceeded"] += 1

          return time_limit_exceeded_message, memory_exceeded_limit_message
        if print_answers:
          memory, time = extract_list(errors_memory_time_of_solution)

          for i, verdict_response in enumerate(verdict):
            time_limit_exceeded_message, memory_limit_exceeded_message = check_memory_time(
              memory[i][0],
              memory[i][1],
              time[i]
            )
            colored_text(
              "\n\n" * verbose * (i > 0)+ f"<keyword>Test case</keyword> <values>{i + 1}</values>"
              f"{(' (Custom &apos;' + self._custom_input_samples[i - input_samples_num] + '&apos;), ') if i >= input_samples_num else ', '}"
              f"time: <values_1>{time[i]} ms</values_1>{time_limit_exceeded_message}, "
              f"memory: <values_2>{memory[i][0]} {memory[i][1]}</values_2>"
              f"{memory_limit_exceeded_message}, "
              f"verdict: {verdict_response}"
            )
            print(checker_log_list[i] * verbose, end="\n" * verbose)

        if not custom_input_without_expected_output_bool:
          memory, time = extract_list(err_mem_time_of_sol_no_expec_out)
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
              "\n\n" * verbose * (i > 0)+ f"<keyword>Test case</keyword> <values>{i + 1}</values>"
              " (" + ("Custom " * print_answers) + "&apos;" + input_samples_without_expected_output[aux] + "&apos;), "
              f"time: <values_1>{time[aux]} ms</values_1>{time_limit_exceeded_message}, "
              f"memory: <values_2>{memory[aux][0]} {memory[aux][1]}</values_2>"
              f"{memory_limit_exceeded_message}"
            )
            print(checker_log_list_no_expec_out[aux] * verbose, end="\n" * verbose)

      else:
        if print_answers:
          for i, verdict_response in enumerate(verdict):
            colored_text(
              "\n\n" * verbose * (i > 0)+ f"<keyword>Test case</keyword> <values>{i + 1}</values>"
              f"{(' (Custom &apos;' + self._custom_input_samples[i - input_samples_num] + '&apos;), ') if i >= input_samples_num else ', '}"
              f"verdict: {verdict_response}"
            )
            print(checker_log_list[i] * verbose, end="\n" * verbose)

        if not custom_input_without_expected_output_bool:
          for i in range(
            input_samples_with_expected_output_num,
            input_samples_with_expected_output_num + input_samples_without_expected_output_num
          ):
            aux = i - input_samples_with_expected_output_num
            colored_text(
              "\n\n" * verbose * (i > 0)+ f"<keyword>Test case</keyword> <values>{i + 1}</values>"
              " (" + ("Custom " * print_answers) + "&apos;" + input_samples_without_expected_output[aux] + "&apos;)"
            )
            print(checker_log_list_no_expec_out[aux] * verbose, end="\n" * verbose)

    print_results()
    # If solution get accepted
    if accepeted:
      colored_text("\nVerdict: <accepted>Demo accepeted</accepted>")
      # Saving test results
      # ========================================================================
      test_results["progress"]["problems_solved"] += 1

      if test_results["unsolved_problems"].get(self.problem_index) is not None:
        move_programming_language_to_right(programming_language, "unsolved_problems")
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
        colored_text("Great job! You solved this problem on your first attempt! Keep up the pace :)", one_color="Cyan")
        test_results["demo_accepted"][self.problem_index] = {}
        test_results["demo_accepted"][self.problem_index]["problem_name"] = self.name
        test_results["demo_accepted"][self.problem_index]["programming_language"] = [programming_language]
        test_results["demo_accepted"][self.problem_index]["timestamp"] = datetime.now(
          ).strftime("%Y-%m-%d %H:%M:%S")
        test_results["demo_accepted"][self.problem_index]["errors"] = errors
        if mem_time_calc:
          test_results["demo_accepted"][self.problem_index]["warnings"] = warnings

      else:
        print("\nYou have already solved this problem!")
        move_programming_language_to_right(programming_language, "demo_accepted")
        augment_errors_warnings(errors, test_results["demo_accepted"][self.problem_index]["errors"])
        if mem_time_calc:
          test_results["demo_accepted"][self.problem_index]["warnings"] = augment_warnings(
            warnings,
            test_results["demo_accepted"][self.problem_index]
          )

      write_json_file(test_results, test_results_file_path, 2)
      # ========================================================================

      # Removing test samples files
      # =========================================================
      if remove_samples_output_files_if_demo_accepted:
        remove_files(self._input_samples)
        remove_files(self._expected_output_samples)
        remove_files(participant_output_filenames_list)
        remove_files(errors_memory_time_of_solution_filenames_list)
        if not custom_input_without_expected_output_bool:
          remove_files(err_mem_time_of_sol_filenames_list_no_expec_out)
          remove_files(participant_output_filenames_list_no_expec_out)
      # =========================================================

    #* The solution is not correct, whether the verdict outputs 'wrong answer' or an error
    elif accepeted is False:
      colored_text(f"\nVerdict: {self._fwrong}")
      save_non_accepted_test_result()


    if working_in_script:
      osRemove("cfkit_module_user_code.py")
      if stop_program:
        sysExit(0)
