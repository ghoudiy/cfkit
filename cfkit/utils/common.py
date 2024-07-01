"""
Documentation
"""

# Standard Library Imports
from sys import exit as sysExit
from re import search as reSearch, sub as reSub
from json import dump
from json import load
from typing import Any
from pathlib import Path
from shutil import rmtree
from datetime import datetime
from os import path as osPath, listdir, remove as osRemove
from subprocess import run, CalledProcessError

# Third-Party Imports
from bs4 import BeautifulSoup

# Cfkit Imports
from cfkit.utils.check import raise_error_if_path_exists
from cfkit.utils.print import colored_text
from cfkit.utils.input import select_option
from cfkit.utils.variables import OUTPUT_FILENAME
from cfkit.utils.variables import conf_file
from cfkit.utils.variables import template_folder
from cfkit.utils.variables import resources_folder
from cfkit.utils.variables import language_conf_path
from cfkit.utils.variables import ERRORS_MEMORY_TIME_FILENAME
from cfkit.utils.variables import INPUT_EXTENSION_FILE
from cfkit.utils.variables import OUTPUT_EXTENSION_FILE
from cfkit.utils.constants import EXTENSIONS
from cfkit.utils.constants import LANGUAGES_EXTENSIONS
from cfkit.utils.constants import Directory


def english_ending(num: int) -> str:
  """
  Documentation
  """
  num %= 100
  if num // 10 == 1:
    return "th"
  if num % 10 == 1:
    return "st"
  if num % 10 == 2:
    return "nd"
  if num % 10 == 3:
    return "rd"
  return "th"

def file_name(name: str, code: str, extension: str) -> str:
  """
  Documentation
  """
  problem_name = reSub(r"('[sS])", lambda match: "_" + match.group(1), name)
  problem_name = reSub(r"\W", "_", problem_name)
  problem_name = reSub(r"(___|__)", "_", problem_name)
  problem_name = problem_name[:-1] if problem_name[-1] == "_" else problem_name
  return f"{code}_{problem_name}.{extension}"

def read_json_file(json_file_path: str | Path) -> dict[Any, Any]:
  """
  Documentation
  """
  with open(json_file_path, 'r', encoding="UTF-8") as file:
    content = load(file)
  return content

def read_text_from_file(file_path: str) -> str:
  """
  Documentation
  """
  with open(file_path, 'r', encoding="UTF-8") as file:
    content = file.read()
  return content

def write_json_file(data: object, file_path: str, spaces: int = 4) -> None:
  """
  Write data to a json file
  """
  with open(file_path, 'w', encoding="UTF-8") as file:
    dump(data, file, indent=spaces)

def write_text_to_file(data: str, file_path: str):
  """
  Write text to a file
  """
  with open(file_path, 'w', encoding="UTF-8") as file:
    file.write(data)

def create_file_folder(
    path_to_file: str,
    file_or_dir: str = 'f',
    skip_existence: bool = False
  ) -> Path:
  """
  Documentation
  """
  path_to_file: Path = Path(path_to_file)
  if skip_existence:
    # Empty the file
    with path_to_file.open('w', encoding="UTF-8"):
      pass
    # return path_to_file.name

  elif not path_to_file.exists():
    if file_or_dir == 'd':
      path_to_file.mkdir()
    else:
      path_to_file.touch()

  else:
    path_to_file = folder_file_exists(path_to_file, "directory" if file_or_dir == "d" else "file")

  return path_to_file

def convert_to_megabytes(memory: str) -> float:
  """
  Documentation
  """
  if not memory.isdigit():
    space = memory.rfind(" ")
    unit = memory[space+1:].lower()
    conversion_factors = {
      "gigabytes": 0.0009765625,
      "megabytes": 1,
      "kilobytes": 1024,
      "bytes": 1048576
    }
    if unit in conversion_factors:
      return float(memory[:space]) * conversion_factors[unit]
    colored_text(
      "Could not recognize the memory size",
      one_color="error",
      exit_code_after_print_statement=1
    )
  return float(memory)

def retrieve_template(file_path: str) -> str:
  """
  Documentation
  """
  language_conf = read_json_file(language_conf_path)
  programming_language = EXTENSIONS[file_path[file_path.find(".")+1:]]
  default_template_path = language_conf[programming_language]["default_template"]
  # $$$ Add an option in the terminal to make the user choose between templates
  if not default_template_path:
    language_template_folder = template_folder.joinpath(
      LANGUAGES_EXTENSIONS[programming_language][0]
    )
    other_templates_paths = language_conf[programming_language]["templates_path"]
    templates: list = language_template_folder.iterdir()

    if any(other_templates_paths):
      for template_path in other_templates_paths:
        template_path = Path(template_path)
        if template_path.is_file():
          templates.append(template_path)
        elif template_path.is_dir():
          templates.extend(template_path.iterdir())
        else:
          colored_text(f"<error_4>No such file or directory</error_4> &apos;{template_path}&apos;")

    templates = list(filter(bool, templates)) # Maybe the user enter a path of an empty folder
    # print(templates)
    if len(templates) > 1:
      print("Available templates: ")
      template = select_option("Template index: ", templates, index=False)
      return template

    return templates[0]
  if not osPath.isfile(default_template_path):
    colored_text(
      "The path of the default template is not a file",
      one_color="error_2",
      exit_code_after_print_statement=1
    )
  return default_template_path

def problems_content(
    content: str,
    contest_id: int,
    problem_index: str = "",
    html_page = False
  ) -> (list[list[str]] | str):
  """
  Documentation
  """
  if html_page:
    # Parse problems statements from 'contestId/problems' page
    contest_name = content[content.find('class="caption">') + 16:]
    contest_name = contest_name[:contest_name.find("</div>")]

    problem_statemen_pos = content.find('<div class="problem-statement">')
    problems: list[list[str]] = []
    while problem_statemen_pos != -1:
      example_close_tag_pos = content.find("</pre></div></div></div>")
      problem_statement = list(string for string in BeautifulSoup(
        content[problem_statemen_pos:example_close_tag_pos],
        "html.parser"
      ).stripped_strings)
      content = content[example_close_tag_pos+24:]
      problems.append(problem_statement)
      problem_statemen_pos = content.find('<div class="problem-statement">')


    # Explain what are you going to do
    with resources_folder.joinpath(
      "problems",
      f"{contest_id}.txt").open('w',
      encoding="UTF-8"
    ) as file:
      file.write(contest_name + "\n\n\n")
      for problem_statement in problems:
        file.write("\n".join(problem_statement) + '\n' + '-' * 100 + '\n')

  else:
    #* The variable 'content' here represents the file path for the contest problem statements
    with open(content, 'r', encoding="UTF-8") as file:
      problems_html_source_code = list(map(lambda x: x[:-1], file.readlines()))

    seperator = '-' * 100
    pos_seperator = problems_html_source_code.index(seperator)
    contest_name = problems_html_source_code[0]
    problems = [problems_html_source_code[3:pos_seperator]] + [
      None] * (problems_html_source_code.count(seperator) - 1)
    for i in range(1, len(problems)):
      problems_html_source_code = problems_html_source_code[pos_seperator+1:]
      pos_seperator = problems_html_source_code.index(seperator)
      problems[i] = problems_html_source_code[:pos_seperator]

  if problem_index:
    i = 0
    test = False
    while not test and i < len(problems):
      test = problems[i][0].startswith(problem_index)
      i += 1
    if i == len(problems) and not test:
      colored_text(
        f"<error_4>No such problem</error_4> &apos;{problem_index}&apos; <error_4>in contest</error_4> &apos;{contest_id}&apos;",
        exit_code_after_print_statement=1
      )
    return problems[i-1], contest_name
  return problems, contest_name

def samples_dir(
    create_tests_dir: bool,
    samples_path: str,
    problem_code: str,
    __check_existence: bool = True
  ) -> Path:
  """
  Documentation
  """
  samples_path: Path = Path(samples_path)
  if create_tests_dir:
    samples_directory = samples_path.joinpath("tests")
    if samples_directory.exists() and __check_existence:
      list_of_files = listdir(samples_directory)
      input_samples = [
        file for file in list_of_files if reSearch(rf"{problem_code}_\d\.{INPUT_EXTENSION_FILE}", file)
      ]
      expected_output_list = [
        file for file in list_of_files if reSearch(rf"{problem_code}_\d\.{OUTPUT_EXTENSION_FILE}", file)
      ]
      if len(input_samples) != len(expected_output_list): #$$$
        samples_directory = samples_path.joinpath(folder_file_exists("tests", 'directory'))
    else:
      samples_directory = create_file_folder(samples_directory, 'd')
  else:
    samples_directory = samples_path
  return samples_directory

def fetch_samples( #$$$
  problem_statement: list[list[str]] | list[str],
  path_to_save_samples: Directory = Path.cwd(),
  attributes: tuple = None, # (problem index, problem name) or ('contest', contest id and contest name)
  check_path: bool = True,
  short_names: bool = False,
) -> None:
  """
  Documentation
  """
  path_to_save_samples = Path(path_to_save_samples)
  if path_to_save_samples != Path.cwd() and check_path:
    raise_error_if_path_exists(path_to_save_samples, 'd')

  def fetch(problem_statement: list, problem_index: str, short_names: bool) -> int:
    # Search for Example section to fetch samples
    try:
      example_index = problem_statement.index("Example")
    except ValueError:
      try:
        example_index = problem_statement.index("Examples")
      except ValueError:
        example_index = problem_statement.index("Example(s)")

    problem_statement = problem_statement[example_index+1:]

    samples_num = problem_statement.count("Input")
    if short_names:
      def naming_style(test_case_num, ext):
        return f"{ext}{test_case_num}"
    else:
      def naming_style(test_case_num, ext):
        return f"{problem_index}_{test_case_num}.{ext}"


    def create_in_out_files(filename, start, end) -> None:
      sample = path_to_save_samples.joinpath(filename)
      if not sample.exists():
        with open(sample, 'w', encoding="UTF-8") as sample_file:
          for data in problem_statement[start+1:end]:
            sample_file.write(f"{data}\n")

    input_samples_filenames = [None] * samples_num
    expected_output_samples_filenames = [None] * samples_num
    for i in range(1, samples_num + 1):
      input_index = problem_statement.index("Input")
      output_index = problem_statement.index("Output")
      input_samples_filenames[i - 1] = naming_style(i, 'in')
      create_in_out_files(input_samples_filenames[i - 1], input_index, output_index)
      problem_statement[input_index] = "input-done"
      input_index = problem_statement.index("Input") if "Input" in problem_statement else len(
        problem_statement)
      expected_output_samples_filenames[i - 1] = naming_style(i, "out")
      create_in_out_files(expected_output_samples_filenames[i - 1], output_index, input_index)
      problem_statement[output_index] = "output-done"
    return input_samples_filenames, expected_output_samples_filenames, samples_num

  last_fetched_file_path = resources_folder.joinpath("last_fetched_data.json")
  if attributes[0] == "contest":
    for problem in problem_statement:
      problem_letter = problem[0][:problem[0].find(".")]
      input_samples_filenames, expected_output_samples_filenames, samples_num = fetch(
        problem,
        str(attributes[1]) + problem_letter,
        short_names
      )
      print(
        f"Parsed {samples_num} sample{'s' if samples_num > 1 else ''} for problem {problem_letter}"
      ) # Grammar checked

    # Save problem attributes to last fetched file
    last_fetched_contest = read_json_file(last_fetched_file_path)
    last_fetched_contest["last_fetched_contest"]["contest_id"] = attributes[1]
    last_fetched_contest["last_fetched_contest"]["contest_name"] = attributes[2]
    last_fetched_contest["last_fetched_contest"]["timestamp"] = datetime.now(
      ).strftime("%Y-%m-%d %H:%M:%S")
    write_json_file(last_fetched_contest, last_fetched_file_path)
  else:
    input_samples_filenames, expected_output_samples_filenames, samples_num = fetch(
      problem_statement,
      attributes[0],
      short_names
    )
    print(f"Parsed {samples_num} sample{'s' if samples_num > 1 else ''}.") # Grammar checked
    # Save problem attributes to last fetched file
    last_fetched_file_path = resources_folder.joinpath("last_fetched_data.json")
    last_fetched_problem = read_json_file(last_fetched_file_path)
    last_fetched_problem["last_fetched_problem"]["problem_index"] = attributes[0]
    last_fetched_problem["last_fetched_problem"]["problem_name"] = attributes[1]
    last_fetched_problem["last_fetched_problem"]["timestamp"] = datetime.now(
      ).strftime("%Y-%m-%d %H:%M:%S")
    write_json_file(last_fetched_problem, last_fetched_file_path)

  return input_samples_filenames, expected_output_samples_filenames

def retrieve_default_language():
  """
  Documentation
  """
  default_language = conf_file["cfkit"]["default_language"]
  # print(default_language)
  if default_language not in read_json_file(language_conf_path):
    pass

def adjusting_paths(
    problem_index: str,
    input_sample: str,
    i: int,
    output_filenames_list: list[str],
    errors_memory_time_of_solution_filenames_list: list[str],
    samples_path: str,
    start: int
  ) -> tuple[str, str]:
  """
  Documentation
  """
  output_filenames_list[i] = Path(samples_path).joinpath(OUTPUT_FILENAME.replace(
    "%%problem_code%%", problem_index).replace("%%test_case_num%%", str(i + 1 + start))
  ).__str__()

  errors_memory_time_of_solution_filenames_list[i] = osPath.join(
    samples_path,
    ERRORS_MEMORY_TIME_FILENAME.replace("%%problem_code%%",problem_index).replace("%%test_case_num%%", str(i + 1 + start)))

  input_sample = Path(samples_path).joinpath(input_sample).__str__()

  return input_sample

def execute_file(
    file: str,
    problem_index: str,
    input_path: str,
    output_path: str,
    time_mem_err_path: str,
    run_command: str,
    # time_limit: float,
    # test_num: int,
  ) -> None:
  '''
  Execute the specified file with provided input, capture the output,
  and save it to the specified path while controlling memory usage in a Go program.
  '''
  run_command = run_command.replace("%%{file}%%", file)
  run_command = run_command.replace("%%{time_mem_err_output_file}%%", time_mem_err_path)
  run_command = run_command.replace("%%{input_file}%%", input_path)
  run_command = run_command.replace("%%{output_file}%%", output_path)
  run_command = run_command.replace("%%{output}%%", problem_index)
  run_command = run_command.replace("%%{dir_name}%%", osPath.dirname(input_path))

  try:
    exitcode = run(run_command, shell=True, check=True).returncode
  except CalledProcessError as err:
    exitcode = err.returncode
  return exitcode

def execute_solution(
    solution_file: str,
    problem_index: str,
    execute_command: str,
    input_sample: str,
    participant_output_path: str,
    errors_memory_time_of_solution_filename: str,
    working_in_script: bool
  ):
  """
  Documentation
  """
  if not working_in_script:
    return execute_file(
      solution_file,
      problem_index,
      input_sample,
      participant_output_path,
      errors_memory_time_of_solution_filename,
      execute_command
    )
  return execute_file(
    "cfkit_module_user_code.py",
    problem_index,
    input_sample,
    participant_output_path,
    errors_memory_time_of_solution_filename,
    execute_command
  )

def remove_files(file_list) -> None:
  """
  Documentation
  """
  for file in file_list:
    osRemove(file)

def augment_errors_warnings(data: dict, test_results: dict):
  """
  Documentation
  """
  for key in data.keys():
    if test_results.get(key) is not None:
      test_results[key] += data[key]
    else:
      test_results[key] = data[key]

def folder_file_exists(name: str, file_or_dir: str) -> str:
  """
  Documentation
  """
  print(f"\nAnother {file_or_dir} with the name '{name}' already exists.")
  user_choice = select_option(
    message="What do you want to do?",
    data=[
      "Write in the same directory" if file_or_dir == "directory" else "Override the file",
      f"Replace the old {file_or_dir} with the new one",
      f"Create a new {file_or_dir} with another name",
      "Abort"
    ],
    index=True,
  )

  if user_choice == 3:
    name = input(f"{file_or_dir.capitalize()} name: ").strip()
    raise_error_if_path_exists(name, file_or_dir[0])
    folder_path = create_file_folder(name, file_or_dir[0])

  elif user_choice == 2:
    rmtree(name)
    folder_path = create_file_folder(name, file_or_dir[0])

  elif user_choice == 1:
    folder_path = name

  else:
    sysExit(1)

  return folder_path
