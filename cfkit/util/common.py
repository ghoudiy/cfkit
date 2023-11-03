"""
Documentation
"""

# Standard Library Imports
import sys
import re
from pathlib import Path
from os import get_terminal_size, path as osPath, listdir
from shutil import rmtree
from json import load, dump
from datetime import datetime
from configparser import NoOptionError
from typing import Any
from inspect import currentframe

# Third-Party Imports
from questionary import Choice, Separator, select, confirm
from requests import get, HTTPError, exceptions as requestsExceptions
from bs4 import BeautifulSoup
from colorama import init, Fore, Back, Style
from threading import Thread
from pynput.keyboard import Controller

# Cfkit Imports
from cfkit.util.variables import color_conf
from cfkit.util.variables import template_folder
from cfkit.util.variables import config_folder
from cfkit.util.variables import resources_folder
from cfkit.util.variables import language_conf_path
from cfkit.util.constants import EXTENSIONS
from cfkit.util.constants import Directory


def input_with_time_limit(
    func,
    timeout_seconds: float,
    default: Any = None,
    default_key: str = 'y',
    **kwargs
  ) -> Any:
  """
  Documentation
  """
  # Create a thread for the question
  confirmation_thread = Thread(
    target = lambda: setattr(confirmation_thread, 'result', func(**kwargs))
  )
  # Start the thread
  confirmation_thread.start()
  # Wait for the thread to complete or for the timeout to occur
  confirmation_thread.join(timeout=timeout_seconds)

  if confirmation_thread.is_alive():
    # If the thread is still running, it means the timeout occurred
    keyboard = Controller()
    keyboard.press(default_key)
    keyboard.release(default_key)
    if default is None:
      return True

  return confirmation_thread.result

def select_option(message: str, data: list, index: bool = False, **kwargs) -> int | Any:
    print(currentframe().f_back)
    question = select(
        message=message,
        choices=data,
        # qmark="😃",
        # style=custom_style_dope,
        # use_shortcuts=True,
        pointer=">",
        **kwargs,
    )
    if index:
      return data.index(question.ask())
    return question.ask()

def get_url_with_timeout(url: str, seconds: float = 15):
  """
  Send HTTP request to url with timeout $$$
  """
  try:
    return get(url, timeout=seconds)
  except requestsExceptions.Timeout:
    print(
      "Unable to fetch data from Codeforces server. "
      "This may be due to one of the following reasons:\n"
      "   • The server is currently experiencing a high volume of requests.\n"
      "   • The server is temporarily down or unreachable.\n"
      "Please try again later or check the status of the Codeforces server.\n"
    )
    return None

def colored_text(
    *message: object,
    one_color='',
    print_statement: bool = True,
    input_statement: bool = False,
  ) -> str | Any:
  """
  Documentation
  """
  init(autoreset=True)

  def generate_color_code_from_components(part: str) -> str:
    order = ["\x1b[", "s-bright", "s-dim", "light"]
    background = part.find("bg")
    if background != -1:
      bg_light_color = part.find("(") != -1
      if bg_light_color:
        background_color = part[background:].find("+") + len(part[:background])
        part = part[:background_color] + part[background_color+1:]
        bg_index = part[:background].count("+")
        part = part.replace(" ", '').split("+")
        part.insert(0, (part[bg_index][4:-1].upper() + "_EX"))
        part[0] = Back.__dict__.get(
              ("LIGHT" + part[0][:-8] + "_EX")
          if part[0][-8:] == "LIGHT_EX" else
              part[0].upper(), '')
        part[bg_index+1] = ""

      else:
        bg_index = part[:background].count("+")
        part = part.replace(" ", '').split("+")
        part.insert(0, part[bg_index][3:].upper())
        part[0] = Back.__dict__.get(part[0].upper(), '')
        part[bg_index+1] = ""

    else:
      part = part.replace(" ", '').split("+")

    components = [None] * 4
    for style in part:
      i = 0
      test = False
      while not test and i < 4:
        test = style[:2] == order[i][:2]
        i += 1
      if not test:
        components.append(style)
      else:
        components[i-1] = style

    colors = ""
    components = filter(bool, components)
    light = False
    for style in components:
      if style == "light":
        light = True
      if style[0] == 's':
        color = Style.__dict__.get(style[2:].upper(), '')
      else:
        style = (f"LIGHT{style.upper()}_EX") if light else style
        color = Fore.__dict__.get(style.upper(), style if style[:2] == "\x1b[" else '')
      colors += color
    return colors

  message = " ".join(map(str, message))

  if one_color:
    try:
      one_color = color_conf.get("theme", one_color.replace(" ", "_"))
      message = generate_color_code_from_components(one_color) + message + Style.RESET_ALL
    except NoOptionError:
      pass
  else:
    color_pattern = re.compile(r'<(\w{5,}|/)>')
    # Split the message using the color tags as delimiters
    def replace(match):
      color_key = match.group(1)
      if color_key == "/":
        return Style.RESET_ALL
      color_value = color_conf.get('theme', color_key)
      return generate_color_code_from_components(color_value)
    message = color_pattern.sub(replace, message)

  if input_statement:
    return input(message).strip()

  if not print_statement:
    return message
  print(message)


def path_exist_error(file_path: str, file_or_dir: str):
  """
  Documentation
  """
  if osPath.exists(file_path):
    colored_text(
          f"<error_8>File exists</> '{file_path}'"
      if file_or_dir == 'f' else
          f"<error_8>Directory exists</> '{file_path}'"
    )
    sys.exit(1)

def check_path_existence(file_path: str, file_or_dir: str):
  """
  Documentation
  """
  if not osPath.exists(file_path):
    colored_text(
          f"<error_9>No such file</>: '{file_path}'"
      if file_or_dir == 'f' else
          f"<error_9>No such directory</> '{file_path}'"
    )
    sys.exit(1)

def check_status(response):
  """
  Documentation
  """
  try:
    response.raise_for_status()
  except HTTPError as err:
    colored_text(f"<error_6>HTTP Error</>: {err}")
    sys.exit(1)

def get_response(url: str, code, contest_id: int = 0, raise_err: bool = False) -> str:
  """
  Documentation
  """
  response = get_url_with_timeout(url)
  check_status(response)
  html_source_code = response.text
  problems = html_source_code.find('<div class="problem-statement">') != -1
  contest_started = html_source_code.find(
    '<div class="contest-state-phase">'
    'Before the contest</div>') == -1

  if not problems:
    if html_source_code.find('Fill in the form to login into Codeforces.') != -1:
      colored_text(
        f"<error_10>You are not allowed to participate in this contest.</> '{contest_id}'"
      )
      sys.exit(1)

    elif not isinstance(code, int) and not code.isdigit():
      if raise_err:
        raise SyntaxError
      colored_text(f"<error_10>No such problem</> '{code}'")
      sys.exit(1)

    colored_text(f"<error_10>No such contest</> '{code}'")
    sys.exit(1)

  elif not contest_started:
    colored_text("Contest has not started yet", one_color="error 11")
    sys.exit(1)

  return response

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

def wrong_answer_verdict(
    line: int,
    column: int,
    word_or_number: str,
    expected_value: Any,
    observed_value: Any
  ) -> str:
  '''
  verdict wrong answer message
  '''
  return (
    f"Wrong answer: {line}{english_ending(line)} line "
    f"{column}{english_ending(column)} {word_or_number} "
    f"differ - expected_value: '{expected_value}', found: '{observed_value}'"
  ) + (f" error = '{(abs(expected_value - observed_value) / observed_value):5f}'" if (
    word_or_number == 'numbers' and int(expected_value) != expected_value) else '')

def file_name(name: str, code: str, extension: str) -> str:
  """
  Documentation
  """
  problem_name = re.sub(r"('[sS])", lambda match: "_" + match.group(1), name)
  problem_name = re.sub(r"\W", "_", problem_name)
  problem_name = re.sub(r"(___|__)", "_", problem_name)
  problem_name = problem_name[:-1] if problem_name[-1] == "_" else problem_name
  return f"{code}_{problem_name}.{extension}"

def yes_or_no(message: str, aux="[Y/n]") -> bool:
  """
  Documentation
  """
  user_choice = input(f"{message}? {aux} ").strip().lower()
  if aux == "[Y/n]":
    yes = ("yes", "y", '')
    nope = ("no", "n")
  else:
    yes = ("yes", "y")
    nope = ("no", "n", '')
  if user_choice in yes:
    aux = True
  elif user_choice in nope:
    aux = False
  else:
    aux = yes_or_no(message)
  return aux

def check_command(command: str, message: str) -> str:
  """
  Documentation
  """
  if isinstance(message, tuple):
    while command.find("{output}") == -1 or command.find("{file}") == -1:
      print(message[0])
      command = input("Please enter your command correctly:\n")
  else:
    while command.find("{file}") == -1:
      print(message)
      command = input("Please enter your command correctly:\n")
  return command

def retype(data: str, input_type: str, _command: str) -> str:
  """
  Documentation
  """
  if not confirm(f"Confirm the {input_type}"):
    if _command is not None:
      return retype(
        check_command(input(f"Please retype the {input_type}:\n"), _command),
        input_type,
        _command
      )
    return retype(input(f"Please retype the {input_type}:\n"), input_type)
  return data

def enter_number(message: str, error_message: str, num_range: range) -> int:
  """
  Documentation
  """
  num = input(message).strip()
  while not num.isdigit() or int(num) not in num_range:
    num = input(error_message).strip()
  return int(num)

def read_json_file(json_file_path: str) -> dict:
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

def is_number(text: str) -> bool:
  """
  Documentation
  """
  try:
    float(text)
    return True
  except ValueError:
    return False

def create_file_folder(
    path_to_file: str,
    file_or_dir: str = 'f',
    skip_existence: bool = False
  ) -> Path:
  """
  Documentation
  """
  path_to_file = Path(path_to_file)
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

def convert_to_bytes(memory: str) -> float:
  """
  Documentation
  """
  if not memory.isdigit():
    space = memory.rfind(" ")
    unit = memory[space+1:].lower()
    conversion_factors = {
      "gigabytes": 1E+9,
      "megabytes": 1E+6,
      "kilobytes": 1000,
      "bytes": 1
    }
    if unit in conversion_factors:
      return float(memory[:space]) * conversion_factors[unit]
    print("Couldn't recognize the memory size")
    sys.exit(1)
  return float(memory)

def folder_file_exists(name: str, file_or_dir: str) -> str:
  """
  Documentation
  """
  print(f"\nAnother {file_or_dir} with the name '{name}' already exists.")
  user_choice = select_option(
    message="What do you want to do?",
    data=[
      "Write in the same directory" if file_or_dir == "directory" else "1. Override the file",
      f"Replace the old {file_or_dir} with the new one",
      f"Create a new {file_or_dir} with another name",
      "Abort"
    ],
    index=True,
    user_shortcuts=True
  )

  if user_choice == 3:
    name = input(f"{file_or_dir.capitalize()} name: ").strip()
    path_exist_error(name, file_or_dir[0])
    folder_path = create_file_folder(name, file_or_dir[0])

  elif user_choice == 2:
    rmtree(name)
    folder_path = create_file_folder(name, file_or_dir[0])

  elif user_choice == 1:
    folder_path = name

  else:
    sys.exit(1)

  return folder_path
file_or_dir = "directory"


def display_horizontally(data: tuple) -> None:
  """
  Documentation
  """
  data = tuple(map(lambda x: f"{x[0]}. {x[1]}", enumerate(data, 1)))
  terminal_width = get_terminal_size().columns
  max_item_width = max(len(item) for item in data)
  # Add some padding between columns
  num_columns = max(1, terminal_width // (max_item_width + 2))

  # Distribute items into columns
  items_per_column = -(-len(data) // num_columns)  # Ceiling division
  columns = [data[i:i + items_per_column] for i in range(0, len(data), items_per_column)]

  # Calculate the number of rows needed to accommodate the columns
  num_rows = max(len(col) for col in columns)

  # Format and print the output using textwrap
  for row in range(num_rows):
    formatted_row = "  ".join(col[row].ljust(max_item_width) if row < len(
      col) else ' ' * max_item_width for col in columns)

    print(formatted_row)

def retrieve_template(file_path: str) -> str:
  """
  Documentation
  """
  language_conf = read_json_file(language_conf_path)
  programming_language = EXTENSIONS[file_path[file_path.find(".")+1:]]
  default_template_path = language_conf[programming_language]["default_template"]
  # $$$ Add an option in the terminal to make the user choose between templates
  if not default_template_path:
    aux = language_conf[programming_language]["extensions"]
    language_template_folder = template_folder.joinpath(aux[0])
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
          colored_text(f"<error_9>No such file or directory</> '{template_path}'")

    templates = list(filter(bool, templates)) # $$$
    print(templates)
    if len(templates) > 1:
      print("Available templates: ")
      display_horizontally(templates)
      template_index = enter_number(
        "Template index: ",
        "Template index: ",
        range(1,
        len(templates)+1)
      )
      return templates[template_index-1]
    return templates[0]
  if not osPath.isfile(default_template_path):
    colored_text("The path of the default template is not a file", one_color="error 2")
    sys.exit(1)
  return default_template_path

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

def download_contests_json_file() -> None:
  """
  Documentation
  """
  contests_json_file = config_folder.joinpath("resources", "contests.json")
  if not contests_json_file.exists():
    response = get_url_with_timeout("https://codeforces.com/api/contest.list")
    check_status(response)
    contest_list = response.json()
    contest_list: list[dict] = sorted(contest_list["result"], key=lambda x: x["id"], reverse=True)

    contests = {}
    for contest in contest_list:
      contest.pop("relativeTimeSeconds")
      contest_id = contest.pop("id")
      contests[contest_id] = dict(contest.items())

    response = get_url_with_timeout("https://codeforces.com/api/problemset.problems")
    check_status(response)
    problem_list = response.json()
    problem_list: list[dict] = sorted(
      problem_list["result"]["problems"], key=lambda x: x["contestId"], reverse=True
    )
    problems = {}
    for problem in problem_list:
      contest_id = problem.pop("contestId")
      problem_index = {problem.pop("index"): dict(problem.items())}
      if problems.get(contest_id) is None:
        problems[contest_id] = {}
        problems[contest_id].update(problem_index)
      else:
        problems[contest_id].update(problem_index)
    write_json_file(contests, contests_json_file, 2)
    write_json_file(problems, config_folder.joinpath("resources", "problems.json"), 2)

download_contests_json_file()

def problems_content(
    content: str,
    contest_id: int,
    problem_index: str = None,
    html_page = False
  ) -> (list[list[str]] | str):
  """
  Documentation
  """
  if html_page:
    # Parse problems statements from 'contestId/problems' page
    problem_statemen_pos = content.find('<div class="problem-statement">')
    contest_name = content.find('class="caption">')
    contest_name = content[contest_name+16:content[contest_name+16:].find("</div>")+contest_name+16]
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

    def create_problems_txt(
        resources_folder: Path,
        contest_id: int,
        problems: list,
        contest_name: str
      ) -> None:
      '''
      Documentation
      '''
      with resources_folder.joinpath(
        "problems",
        f"{contest_id}.txt").open('w',
        encoding="UTF-8"
      ) as file:
        file.write(contest_name + "\n\n\n")
        for problem_statement in problems:
          file.write("\n".join(problem_statement) + '\n' + '-' * 100 + '\n')

    create_problems_txt(resources_folder, contest_id, problems, contest_name)

  else:
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
      test = problems[i][0][0].startswith(problem_index)
      i += 1
      if i == len(problems) and not test:
        colored_text(f"<error_10>No such problem</> '{problem_index}'")
        sys.exit(1)
    return problems[i-1], contest_name
  return problems, contest_name

def samples_dir(create_tests_dir: bool, samples_path: str, problem_index: str) -> Path:
  """
  Documentation
  """
  samples_path: Path = Path(samples_path)
  if create_tests_dir:
    samples_directory = samples_path.joinpath("tests")
    if samples_directory.exists():
      list_of_files = listdir(samples_directory)
      input_samples = sorted(
        [file for file in list_of_files if re.search(rf"{problem_index}_\d\.in", file)])
      expected_output_list = sorted(
        [file for file in list_of_files if re.search(rf"{problem_index}_\d\.out", file)])
      if len(input_samples) == len(expected_output_list):
        samples_directory = samples_directory
      else:
        samples_directory = samples_path.joinpath(folder_file_exists("tests", 'directory'))
    else:
      samples_directory = create_file_folder(samples_directory, 'd')
  else:
    samples_directory = samples_path
  return samples_directory

def fetch_samples(
  problem_statement: list[list[str]] | list[str],
  path_to_save_samples: Directory = Path.cwd(),
  attributes: tuple = None,
  check_path: bool = True,
) -> None:
  """
  Documentation
  """
  path_to_save_samples = Path(path_to_save_samples)
  if path_to_save_samples != Path.cwd() and check_path:
    check_path_existence(path_to_save_samples, 'd')

  def fetch(problem_statement: list, problem_index: str) -> int:
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
    aux = samples_num

    def create_in_out_files(nr1, nr2, ext, start, end) -> None:
      sample = path_to_save_samples.joinpath(f"{problem_index}_{nr1 - nr2 + 1}.{ext}")
      if not sample.exists():
        with open(sample, 'w', encoding="UTF-8") as sample_file:
          for data in problem_statement[start+1:end]:
            sample_file.write(f"{data}\n")

    for i in range(samples_num, 0, -1):
      input_index = problem_statement.index("Input")
      output_index = problem_statement.index("Output")
      create_in_out_files(aux, i, "in", input_index, output_index)
      problem_statement[input_index] = "input-done"
      input_index = problem_statement.index("Input") if "Input" in problem_statement else len(
        problem_statement)
      create_in_out_files(aux, i, "out", output_index, input_index)
      problem_statement[output_index] = "output-done"
    return samples_num

  last_fetched_file_path = resources_folder.joinpath("last_fetched_data.json")
  if attributes[0] == "contest":
    for problem in problem_statement:
      problem_letter = problem[0][:problem[0].find(".")]
      samples_num = fetch(problem, str(attributes[1]) + problem_letter)
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
    samples_num = fetch(problem_statement, attributes[0])
    print(f"Parsed {samples_num} sample{'s' if samples_num > 1 else ''}.") # Grammar checked
    # Save problem attributes to last fetched file
    last_fetched_file_path = resources_folder.joinpath("last_fetched_data.json")
    last_fetched_problem = read_json_file(last_fetched_file_path)
    last_fetched_problem["last_fetched_problem"]["problem_index"] = attributes[0]
    last_fetched_problem["last_fetched_problem"]["problem_name"] = attributes[1]
    last_fetched_problem["last_fetched_problem"]["timestamp"] = datetime.now(
      ).strftime("%Y-%m-%d %H:%M:%S")
    write_json_file(last_fetched_problem, last_fetched_file_path)
