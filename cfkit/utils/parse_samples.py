"""
Documentation
"""

# Standard Library Imports
from sys import exit as sysExit
from re import search as reSearch, compile as reCompile, IGNORECASE
from pathlib import Path
from datetime import datetime
from os import listdir

# Third-Party Imports
from bs4 import BeautifulSoup

# Cfkit Imports
from cfkit.utils.check import raise_error_if_path_exists
from cfkit.utils.print import colored_text
from cfkit.utils.file_operations import (
  read_json_file,
  folder_file_exists,
  write_json_file,
  create_file_folder
)

from cfkit.utils.variables import resources_folder
from cfkit.utils.variables import INPUT_EXTENSION_FILE
from cfkit.utils.variables import OUTPUT_EXTENSION_FILE
from cfkit.utils.variables import OUTPUT_FILENAME_PATTERN
# from cfkit.utils.variables import ERRORS_MEMORY_TIME_FILENAME_PATTERN
from cfkit.utils.constants import HTML_CLOSE_DIV_TAG
from cfkit.utils.constants import HTML_CLASS_PATTERN
from cfkit.utils.constants import HTML_DIV_CLASS_PATTERN
from cfkit.utils.constants import HTML_DOUBLE_DIV_CLASS_PATTERN
from cfkit.utils.constants import Directory


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
    content = content[reSearch(rf"{HTML_CLASS_PATTERN}caption['\"]\s*>", content, IGNORECASE).start() + 16:]
    contest_name = content[:reSearch(HTML_CLOSE_DIV_TAG, content).start()]

    problems: list[list[str]] = []

    OUTPUT_FILE_TAG_PATTERN = reCompile(
      rf"{HTML_DIV_CLASS_PATTERN.replace('class_name', 'output-file')}"
      rf"(.*?){HTML_CLOSE_DIV_TAG}\s*{HTML_CLOSE_DIV_TAG}"
    )
    PROBLEM_STATEMENT_TAG_PATTERN = reCompile(HTML_DIV_CLASS_PATTERN.replace("class_name", "problem-statement"))
    SCRIPT_TAG_PATTERN = reCompile(r"<\s*script\s*>")
    EXAMPLE_OPEN_TAG_PATTERN = reCompile(HTML_DIV_CLASS_PATTERN.replace("class_name", "sample-test"))
    INPUT_TAG_PATTERN = reCompile(
      HTML_DOUBLE_DIV_CLASS_PATTERN.replace("class_name", "input", 1).replace("class_name", "title")
    )
    NOTE_TAG_PATTERN = reCompile(
      HTML_DOUBLE_DIV_CLASS_PATTERN.replace("class_name", "note", 1).replace("class_name", "section-title")
    )

    problem_statement_pos = PROBLEM_STATEMENT_TAG_PATTERN.search(content)
    while problem_statement_pos is not None:

      problem_statement_pos = problem_statement_pos.end()
      problem_properties = list(
        string for string in BeautifulSoup(
          content[problem_statement_pos:OUTPUT_FILE_TAG_PATTERN.search(content, problem_statement_pos).end()],
          "html.parser"
        ).stripped_strings
      )

      problem_properties = [
        problem_properties[0], # problem name
        f"time limit per test: {problem_properties[2]}",
        f"memory limit per test: {problem_properties[4]}",
        f"input: {problem_properties[6]}",
        f"output: {problem_properties[8]}"
      ]

      try:
        script_tag_pos = SCRIPT_TAG_PATTERN.search(content, problem_statement_pos).start()
        example_close_tag_pos = NOTE_TAG_PATTERN.search(
          content,
          pos=problem_statement_pos,
          endpos=script_tag_pos
        )
        if example_close_tag_pos is None:
          example_close_tag_pos = script_tag_pos
        else:
          example_close_tag_pos = example_close_tag_pos.start()

        example_open_tag_pos = EXAMPLE_OPEN_TAG_PATTERN.search(
          content,
          pos=problem_statement_pos,
          endpos=example_close_tag_pos
        )

        if example_open_tag_pos is None:
          raise InterruptedError("There is no 'Examples' title at all")

        example_open_tag_pos = example_open_tag_pos.end()

        if INPUT_TAG_PATTERN.search(
          content,
          pos=problem_statement_pos,
          endpos=example_close_tag_pos
        ) is None:
          raise InterruptedError("There is an 'Examples' title, but there are no samples")

        problem_samples = list(
          string for string in BeautifulSoup(
            content[example_open_tag_pos:example_close_tag_pos],
            "html.parser"
          ).stripped_strings
        )
        for i in range(len(problem_samples)):
          if problem_samples[i] == "Входные данные":
            problem_samples[i] = "Input"
          elif problem_samples[i] == "Выходные данные":
            problem_samples[i] = "Output"

        # print(f"{problem_samples = }")
        problems.append(problem_properties + ["", "Examples"] + problem_samples)

      except InterruptedError:
        colored_text(f"There are no test samples for &apos;{problem_properties[0]}&apos; problem")
        problems.append(problem_properties + ["", "No test samples are available for this problem"])

      finally:
        problem_statement_pos = PROBLEM_STATEMENT_TAG_PATTERN.search(content, problem_statement_pos)


    # Explain what are you going to do
    with resources_folder.joinpath("problems", f"{contest_id}.txt").open('w', encoding="UTF-8") as file:
      file.write(contest_name + "\n\n\n")
      for problem in problems:
        file.write("\n".join(problem) + '\n' + '-' * 100 + '\n')

  else:
    #* The variable 'content' here represents the file path for the contest problem statements
    with open(content, 'r', encoding="UTF-8") as file:
      problems_html_source_code = file.read().split("\n")

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
    __check_existence: bool = True
  ) -> Path:
  """
  Documentation
  """
  samples_path: Path = Path(samples_path)
  if create_tests_dir:
    samples_directory = samples_path.joinpath("tests")
    if __check_existence and samples_directory.exists() and len(listdir(samples_directory)) > 0:
      samples_directory = samples_path.joinpath(folder_file_exists("tests", 'directory'))
    else:
      samples_directory = create_file_folder(samples_directory, 'd')
  else:
    samples_directory = samples_path
  return samples_directory

def fetch_samples(
  problem_statement: list[list[str]] | list[str],
  path_to_save_samples: Directory = Path.cwd(),
  attributes: tuple = None, # (problem index, problem name) or ('contest', contest id and contest name)
  check_path: bool = True,
  short_names: bool = False,
) -> tuple[list[str], list[str]]:
  """
  Documentation
  """
  path_to_save_samples = Path(path_to_save_samples)
  if path_to_save_samples != Path.cwd() and check_path:
    raise_error_if_path_exists(path_to_save_samples, 'd')

  def fetch(
      problem_statement: list,
      problem_index: str,
      short_names: bool
    ) -> tuple[list[str], list[str], int]:
    def create_in_out_files(filename, start, end) -> None:
      sample = path_to_save_samples.joinpath(filename)
      if not sample.exists():
        with open(sample, 'w', encoding="UTF-8") as sample_file:
          for data in problem_statement[start+1:end]:
            sample_file.write(f"{data}\n")

    def get_input_output_samples(sample_num, func):
      input_index = problem_statement.index("Input")
      output_index = problem_statement.index("Output")

      input_samples_filenames[sample_num - 1] = naming_style(sample_num, INPUT_EXTENSION_FILE)
      create_in_out_files(input_samples_filenames[sample_num - 1], input_index, output_index)
      problem_statement[input_index] = None

      input_index = func(problem_statement)

      expected_output_samples_filenames[sample_num - 1] = naming_style(sample_num, OUTPUT_EXTENSION_FILE)
      create_in_out_files(expected_output_samples_filenames[sample_num - 1], output_index, input_index)
      problem_statement[output_index] = None

    if short_names:
      def naming_style(test_case_num, ext):
        return f"{ext}{test_case_num}"
    else:
      def naming_style(test_case_num, ext):
        return f"{problem_index}_{test_case_num}.{ext}"

    if problem_statement[6] == "No test samples are available for this problem":
      return None, None, None

    problem_statement = problem_statement[7:]

    samples_num = problem_statement.count("Input")
    input_samples_filenames = [None] * samples_num
    expected_output_samples_filenames = [None] * samples_num

    func = lambda problem_statement: problem_statement.index("Input")
    for i in range(1, samples_num):
      get_input_output_samples(i, func)

    get_input_output_samples(samples_num, lambda problem_statement: len(problem_statement))

    return input_samples_filenames, expected_output_samples_filenames, samples_num


  last_fetched_file_path = resources_folder.joinpath("last_fetched_data.json")
  if attributes[0] == "contest":
    for problem in problem_statement:
      problem_letter = problem[0][:problem[0].find(".")]
      # input_samples_filenames, expected_output_samples_filenames, samples_num = fetch(
      _, _, samples_num = fetch(
        problem,
        str(attributes[1]) + problem_letter,
        short_names
      )
      if samples_num is None:
        print(f"No test samples are available for '{str(attributes[1]) + problem_letter}' problem")
      else:
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
    return None, None

  input_samples_filenames, expected_output_samples_filenames, samples_num = fetch(
    problem_statement,
    attributes[0],
    short_names
  )
  if samples_num is None:
    print(f"No test samples are available for '{attributes[0]}' problem")
    sysExit(1)

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
