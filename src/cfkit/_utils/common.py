"""
Documentation
"""

# Standard Library Imports
from os import path as osPath
from re import sub as reSub
from pathlib import Path
from subprocess import run, CalledProcessError
from datetime import datetime

# Cfkit Imports
from cfkit._utils.print import colored_text
from cfkit._utils.input import select_option
from cfkit._utils.file_operations import read_json_file

from cfkit._utils.variables import (
  conf_file,
  separator,
  OUTPUT_FILENAME,
  template_folder,
  language_conf_path,
  ERRORS_MEMORY_TIME_FILENAME
)
from cfkit._utils.constants import EXTENSIONS, LANGUAGES_EXTENSIONS


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

def trim_data(data: list[str]) -> list[str]:
  """
  Remove empty lines and extra spaces
  """
  data_without_new_lines = []
  values = []
  for i in range(len(data)):
    data[i] = data[i].strip().split(" ")
    for j in range(len(data[i])):
      if data[i][j]:
        values.append(data[i][j])
        data_without_new_lines.append((i, j, data[i][j]))
  return data_without_new_lines, values

def remove_empty_lines(data: list[str]):
  """
  Documentation
  """
  i = 0
  while (l:=len(data)) > 0 and i < l:
    if data[i] == "":
      data.pop(i)
    else:
      i += 1

def convert_to_megabytes(memory: str) -> float:
  """
  Documentation
  """
  space = memory.rfind(" ")
  unit = memory[space+1:].lower()
  conversion_factors = {
    "gigabytes": 0.0009765625,
    "гигабайты": 0.0009765625,
    "megabytes": 1,
    "мегабайт": 1,
    "kilobytes": 1024,
    "килобайты": 1024,
    "bytes": 1048576,
    "байты": 1048576
  }
  if unit in conversion_factors:
    return float(memory[:space]) * conversion_factors[unit]
  colored_text(
    "Could not recognize the memory size",
    one_color="error",
    exit_code_after_print_statement=1
  )

def retrieve_template(file_path: str) -> str:
  """
  Documentation
  """
  language_conf = read_json_file(language_conf_path)

  if (programming_language:=EXTENSIONS.get(file_path[file_path.rfind(".")+1:])) is None:
    colored_text("Extension is not recognised! Please try again", one_color="error_4", exit_code_after_print_statement=4)

  default_template_path = language_conf[programming_language]["default_template"]
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

    templates: list[Path] = [templ for templ in templates if templ] # Maybe the user enter a path of an empty folder
    
    i = -1
    test = False
    len_templates = len(templates)
    while not test and i < len_templates - 1:
      i += 1
      test = templates[i].name.startswith("default.")
    if test:
      return templates[i]

    if len(templates) > 1:
      print("Available templates: ")
      template = select_option("Template index: ", templates, index=False)
      return template

    return templates[0]
  if not osPath.isfile(default_template_path):
    colored_text(
      "The path of the default template is not a file",
      one_color="error_2",
      exit_code_after_print_statement=2
    )
  return default_template_path

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

  output_filenames_list[i] = osPath.join(samples_path, OUTPUT_FILENAME.replace(
    "%%problem_code%%", problem_index).replace("%%test_case_num%%", str(i + 1 + start))
  )

  errors_memory_time_of_solution_filenames_list[i] = osPath.join(
    samples_path,
    ERRORS_MEMORY_TIME_FILENAME.replace("%%problem_code%%",problem_index).replace("%%test_case_num%%", str(i + 1 + start)))

  input_sample = osPath.join(samples_path, input_sample)

  return input_sample

def execute_file(
    file: str,
    problem_index: str,
    input_path: str,
    output_path: str,
    time_mem_err_path: str,
    run_command: str,
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

def augment_errors_warnings(data: dict, test_results: dict):
  """
  Documentation
  """
  for key in data.keys():
    if test_results.get(key) is not None:
      test_results[key] += data[key]
    else:
      test_results[key] = data[key]

def fill_checker_log_list(
  checker_log_list: list[list] | list[str],
  data: list[str],
  i: int,
  replace_non_xml_valid_char_bool: bool = False,
  columns_num: int = 55,
):
  """
  Documentation
  """
  while (data_length:=len(data)) > 1 and data[-1] == "":
    data.pop()
  if data_length == 1 and data[0] == "":
    data = ["(Empty)"]
  if replace_non_xml_valid_char_bool:
    for line in data:
      checker_log_list[i] += f"| {replace_non_xml_valid_characters(line)} {' ' * (columns_num - len(line) - 2)}|\n"
  else:
    for line in data:
      checker_log_list[i] += f"| {line} {' ' * (columns_num - len(line) - 2)}|\n"

def replace_non_xml_valid_characters(text: str) -> str:
  """
  Documentation
  """
  return (
    text.replace("&", "&amp;")
    .replace("<", "&lt;")
    .replace(">", "&gt;")
    .replace('"', "&quot;")
  )

def fill_checker_log_normal_way(checker_log_list, test_sample_num, input_string, observed, expected):
  """
  Documentation
  """
  checker_log_list[test_sample_num] = f"Input\n {separator}\n"
  fill_checker_log_list(checker_log_list, input_string, test_sample_num)

  checker_log_list[test_sample_num] += f" {separator}\n\nOutput\n {separator}\n"
  fill_checker_log_list(checker_log_list, observed, test_sample_num)

  checker_log_list[test_sample_num] += f" {separator}\n\nAnswer\n {separator}\n"
  fill_checker_log_list(checker_log_list, expected, test_sample_num)

  checker_log_list[test_sample_num] += f" {separator}\nChecker log: "

def insert_placeholders_template(code):
  return (
    code.replace("$%author%$", conf_file["cfkit"]["user"])
    .replace("$%year%$",   str(datetime.now().year))
    .replace("$%month%$",  str(datetime.now().month))
    .replace("$%day%$",    str(datetime.now().day))
    .replace("$%hour%$",   str(datetime.now().hour))
    .replace("$%minute%$", str(datetime.now().minute))
    .replace("$%second%$", str(datetime.now().second))
  )