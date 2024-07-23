"""
Documentation
"""

# Standard Library Imports
from sys import exit as sysExit
from pathlib import Path
from datetime import datetime

# Third-Party Imports
from bs4 import BeautifulSoup

# Cfkit Imports
from cfkit._utils.check import raise_error_if_path_missing
from cfkit._utils.print import colored_text
from cfkit._utils.file_operations import (
  read_json_file,
  write_json_file,
  create_file_folder
)

from cfkit._utils.variables import (
  resources_folder,
  INPUT_FILENAME,
  EXPECTED_OUTPUT_FILENAME,
  SHORT_INPUT_FILENAME,
  SHORT_EXPECTED_OUTPUT_FILENAME,
  history_file_path
)
from cfkit._utils.constants import Directory


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
    soup = BeautifulSoup(content, 'html.parser')
    contest_name = soup.find("div", class_="caption").get_text(strip=True)

    problems: list[list[str]] = []

    problem_statement_div = soup.find_all("div", class_="problem-statement")
    for div in problem_statement_div:
      problem_properties = div.find("div", class_="header").get_text(separator="\n", strip=True).split("\n")
      problem_properties = [
        problem_properties[0], # problem name
        f"time limit per test: {problem_properties[2]}",
        f"memory limit per test: {problem_properties[4]}",
        f"input: {problem_properties[6]}",
        f"output: {problem_properties[8]}"
      ]
      try:
        problem_samples_div = div.find_all("div", class_="sample-test")
        assert len(problem_samples_div) > 0

        problem_samples = []
        for problem_sample in problem_samples_div:
          aux = problem_sample.get_text(strip=True)

          if aux.startswith("Input\n"):
            problem_sample = aux.split("\n")
          else:
            problem_sample = problem_sample.get_text(separator="\n").split("\n")

          problem_sample = [sample for sample in problem_sample if sample]

          assert len(problem_sample) > 0

          for i in range(len(problem_sample)):
            if problem_sample[i] == "Входные данные":
              problem_sample[i] = "Input"
            elif problem_sample[i] == "Выходные данные":
              problem_sample[i] = "Output"

          problem_samples.extend(problem_sample)

        problems.append(problem_properties + ["", "Examples"] + problem_samples)

      except AssertionError:
        colored_text(f"There are no test samples for &apos;{problem_properties[0]}&apos; problem")
        problems.append(problem_properties + ["", "No test samples are available for this problem"])

    # Explain what are you going to do
    with resources_folder.joinpath("problems", f"{contest_id}.txt").open('w', encoding="UTF-8") as file:
      file.write(contest_name + "\n\n\n")
      for problem in problems:
        file.write("\n".join(problem) + '\n' + '-' * 100 + '\n')

  else:
    #* The variable 'content' here represents the file path for the contest problem statements
    with open(content, 'r', encoding="UTF-8") as file:
      problems_html_source_code = file.read().split("\n")

    separator = '-' * 100
    pos_seperator = problems_html_source_code.index(separator)
    contest_name = problems_html_source_code[0]
    problems = [problems_html_source_code[3:pos_seperator]] + [
      None] * (problems_html_source_code.count(separator) - 1)
    for i in range(1, len(problems)):
      problems_html_source_code = problems_html_source_code[pos_seperator+1:]
      pos_seperator = problems_html_source_code.index(separator)
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
        exit_code_after_print_statement=4
      )
    return problems[i-1], contest_name
  return problems, contest_name

def samples_dir(create_tests_dir: bool,samples_path: str) -> Path:
  """
  Documentation
  """
  samples_path: Path = Path(samples_path)
  if create_tests_dir:
    samples_directory = samples_path.joinpath("tests")
    if not samples_directory.exists():
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
  if check_path and path_to_save_samples != Path.cwd():
    raise_error_if_path_missing(path_to_save_samples, 'd')

  def fetch(
      problem_statement: list,
      problem_code: str,
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

      input_samples_filenames[sample_num - 1] = naming_style(
        sample_num,
        INPUT_FILENAME,
        SHORT_INPUT_FILENAME
      )
      create_in_out_files(input_samples_filenames[sample_num - 1], input_index, output_index)
      problem_statement[input_index] = None

      input_index = func(problem_statement)

      expected_output_samples_filenames[sample_num - 1] = naming_style(
        sample_num,
        EXPECTED_OUTPUT_FILENAME,
        SHORT_EXPECTED_OUTPUT_FILENAME
      )
      create_in_out_files(expected_output_samples_filenames[sample_num - 1], output_index, input_index)
      problem_statement[output_index] = None

    if short_names:
      def naming_style(test_case_num, _, filename: str):
        return filename.replace("%%test_case_num%%", str(test_case_num))
    else:
      def naming_style(test_case_num: int, filename: str, _):
        return filename.replace("%%problem_code%%", problem_code).replace("%%test_case_num%%", str(test_case_num))

    if problem_statement[6] == "No test samples are available for this problem":
      return None, None, None

    problem_statement = problem_statement[7:]

    samples_num = problem_statement.count("Input")
    input_samples_filenames = [None] * samples_num
    expected_output_samples_filenames = [None] * samples_num

    def func(problem_statement):
      return problem_statement.index("Input")
    for i in range(1, samples_num):
      get_input_output_samples(i, func)

    get_input_output_samples(samples_num, lambda problem_statement: len(problem_statement))

    return input_samples_filenames, expected_output_samples_filenames, samples_num

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
    history = read_json_file(history_file_path)
    history["last_fetched_contest"]["contest_id"] = attributes[1]
    history["last_fetched_contest"]["contest_name"] = attributes[2]
    history["last_fetched_contest"]["timestamp"] = datetime.now(
      ).strftime("%Y-%m-%d %H:%M:%S")
    write_json_file(history, history_file_path)
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
  last_fetched_problem = read_json_file(history_file_path)
  last_fetched_problem["last_fetched_problem"]["problem_index"] = attributes[0]
  last_fetched_problem["last_fetched_problem"]["problem_name"] = attributes[1]
  last_fetched_problem["last_fetched_problem"]["timestamp"] = datetime.now(
    ).strftime("%Y-%m-%d %H:%M:%S")
  write_json_file(last_fetched_problem, history_file_path)

  return input_samples_filenames, expected_output_samples_filenames
