"""
Documentation
"""

import sys
import re
from os import path, mkdir, get_terminal_size, listdir
from shutil import rmtree
from json import load
from configparser import ConfigParser, NoOptionError
from requests import get, HTTPError, exceptions as requestsExceptions
from colorama import init, Fore, Back, Style

def path_exist_error(file_path, file_or_dir):
  """
  Documentation
  """
  if path.exists(file_path):
    colored_text(
          f"<error_8>File exists</> '{file_path}'"
      if file_or_dir == 'f' else
          f"<error_8>Directory exists</> '{file_path}'"
    )
    sys.exit(1)


def check_path_existence(file_path, file_or_dir):
  """
  Documentation
  """
  if not path.exists(file_path):
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

def check_url(url: str, code, contest_id=0, raise_err=False):
  """
  Documentation
  """
  try:
    response = get(url, timeout=10)
  except requestsExceptions.Timeout:
    print(
      "Unable to fetch data from Codeforces server. "
      "This may be due to one of the following reasons:",
      "   1. The server is currently experiencing a high volume of requests.",
      "   2. The server is temporarily down or unreachable.",
      "Please try again later or check the status of the Codeforces server.",
      sep="\n"
    )
    sys.exit(1)
  check_status(response)
  html_source_code = response.text
  current = html_source_code.find('<li class="current"><a href="/contests">Contests</a></li>')
  valid_contest = html_source_code.find('Codeforces.showMessage("No such contests");') == -1
  valid_contest = valid_contest and html_source_code.find(
    'Codeforces.showMessage'
    '("No such contest");') == -1
  contest_started = html_source_code.find(
    '<div class="contest-state-phase">'
    'Before the contest</div>') == -1
  if not valid_contest:
    if contest_id:
      colored_text(f"<error_5>No such contest</> '{contest_id}'")
      sys.exit(1)
    colored_text(f"<error_5>No such contest</> '{code}'")
    sys.exit(1)

  elif not contest_started:
    colored_text("Contest has not started yet", "error_6")
    sys.exit(1)

  if not isinstance(code, int):
    if not html_source_code.find('Codeforces.showMessage("No such problem");') == -1:
      if raise_err:
        raise SyntaxError
      colored_text(f"<error_5>No such problem</> '{code}'")
      sys.exit(1)
  return response.text

def english_ending(num):
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

def wrong_answer_verdict(line, column, word_or_number, expected_value, observed_value):
  '''
  verdict wrong answer message
  '''
  return (
    f"Wrong answer: {line}{english_ending(line)} line "
    f"{column}{english_ending(column)} {word_or_number} "
    f"differ - expected_value: '{expected_value}', found: '{observed_value}'"
  ) + f" error = '{(abs(expected_value - observed_value) / observed_value):5f}'" if (
    word_or_number == 'numbers' and int(expected_value) != expected_value) else ''

def file_name(name, code, extension):
  """
  Documentation
  """
  problem_name = re.sub(r"('[sS])", lambda match: "_" + match.group(1), name)
  problem_name = re.sub(r"\W", "_", problem_name)
  problem_name = re.sub(r"(___|__)", "_", problem_name)
  problem_name = problem_name[:-1] if problem_name[-1] == "_" else problem_name
  return f"{code}_{problem_name}.{extension}"

def yes_or_no(message, aux="[Y/n]"):
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

def check_command(command, message):
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

def confirm(data, input_type, __command = None):
  """
  Documentation
  """
  if not yes_or_no(f"Confirm the {input_type}"):
    if __command:
      return confirm(
        check_command(input(f"Please retype the {input_type}:\n"), __command),
        input_type,
        __command
      )
    return confirm(input(f"Please retype the {input_type}:\n"), input_type)
  return data

def enter_number(message, error_message, num_range):
  """
  Documentation
  """
  num = input(message).strip()
  while not num.isdigit() or int(num) not in num_range:
    num = input(error_message).strip()
  return int(num)

def read_json_file(json_file_path):
  """
  Documentation
  """
  with open(json_file_path, 'r', encoding="UTF-8") as file:
    return load(file)

def read_text_from_file(file_path):
  """
  Documentation
  """
  with open(file_path, 'r', encoding="UTF-8") as file:
    content = file.read()
  return content

def is_number(text):
  """
  Documentation
  """
  try:
    float(text)
    return True
  except ValueError:
    return False

def create_file_folder(path_to_file, file_or_dir='f'):
  """
  Documentation
  """
  if not path.exists(path_to_file):
    if file_or_dir == 'd':
      mkdir(path_to_file)
    else:
      with open(path_to_file, 'x', encoding="UTF-8"):
        pass
  else:
    folder_file_exists(path_to_file, "directory" if file_or_dir == "d" else "file")
  return path.basename(path_to_file)

def colored_text(message: str, one_statement_color='', print_statement=True, input_statement=False):
  """
  Documentation
  """
  init(autoreset=True)

  def generate_color_code_from_components(part: str):
    order = ["\x1b[", "s-bright", "s-dim", "light"]
    background = part.find("bg")
    if background != -1:
      # Just make it works
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

  if one_statement_color:
    try:
      one_statement_color = color_conf.get("theme", one_statement_color)
      message = generate_color_code_from_components(one_statement_color) + message + Style.RESET_ALL
    except NoOptionError:
      pass
  else:
    pattern = r'<(\w{5,}|/)>'
    color_pattern = re.compile(pattern)
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

def convert_to_bytes(memory: str):
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

def folder_file_exists(name, file_or_dir):
  """
  Documentation
  """
  print(
    f"Another {file_or_dir} with the name '{name}' already exists.",
    "1. Write in the same directory" if file_or_dir == "directory" else "1. Override the file",
    f"2. Replace the old {file_or_dir} with the new one",
    f"3. Create a new {file_or_dir} with another name",
    sep="\n"
  )
  user_choice = enter_number("Action index: ", "Action index: ", range(1, 4))

  if user_choice == 3:
    name = input(f"{file_or_dir.capitalize()} name: ").strip()
    path_exist_error(name, file_or_dir[0])
    folder_path = create_file_folder(name, file_or_dir[0])

  elif user_choice == 2:
    rmtree(name)
    folder_path = create_file_folder(name, file_or_dir[0])

  else:
    folder_path = name

  return folder_path

def display_horizontally(data: tuple):
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

def retrieve_template(file):
  """
  Documentation
  """
  ext = file[file.rfind(".")+1:]
  programming_language = extensions[ext]
  default_template = language_conf[programming_language]["default_template"]
  # $$$ Add an option in the terminal to make the user choose between templates
  if not default_template:
    aux = language_conf[programming_language]["extensions"]
    language_template_folder = path.join(template_folder, ext if aux[0] == ext else aux[0])
    other_templates_paths = language_conf[programming_language]["templates_path"]
    templates: list = list(map(
      lambda x: path.join(language_template_folder, x),
      listdir(language_template_folder)
    ))
    if any(other_templates_paths):
      for template_path in other_templates_paths:
        if template_path.isfile(template_path):
          templates.append(template_path)
        elif template_path.isdir(template_path):
          templates.extend(listdir(template_path))
        else:
          colored_text(f"<error_9>No such file or directory</> '{template_path}'")
    templates = list(filter(bool, templates))
    if len(templates) > 1:
      print("Available templates: ")
      display_horizontally(templates)
      template_index = enter_number(
        "Template index: ",
        "Template index: ",
        range(1,
        len(templates)+1)
      )
      return templates[template_index]
    return templates[0]
  if not path.isfile(default_template):
    colored_text("The path of the default template is not a file", "error_12")
    sys.exit(1)
  return default_template

def download_contests_json_file():
  """
  Documentation
  """
  contests_json_file = path.join(config_folder, "contests", "contests.json")
  if not path.exists(contests_json_file):
    response = get("https://codeforces.com/api/contest.list")
    check_status(response)
    contests = {}
    for contest in response.json()["result"]:
      contest_id = contest.pop("id")
      contests[contest_id] = {}
      for key, value in contest.items():
        contests[contest_id][key] = value
    with open(contests_json_file, 'w') as file:
      file.write()
        

MACHINE = sys.platform
PROBLEM_CODE_PATTERN = r"\A[1-9]{1}\d{,3}[A-z]\d?"
json_folder = path.join(path.dirname(path.dirname(__file__)), "json")
config_folder = path.join(
  path.expanduser("~"),
  "AppData\\Roaming" if MACHINE == "win32" else ".config", "cfkit"
)
template_folder = path.join(config_folder, "templates")
language_conf_path = path.join(config_folder, "languages.json")
language_conf = read_json_file(language_conf_path)
conf_file = ConfigParser()
conf_file.read(path.join(config_folder, "cfkit.conf"))
color_conf = ConfigParser()
color_conf.read(path.join(config_folder, "colorschemes", conf_file["cfkit"]["color_scheme"]))
extensions = {
  "c": "C",
  "cpp": "C++",
  "cxx": "C++",
  "C": "C++",
  "cc": "C++",
  "c++": "C++",
  "cs": "C#",
  "d": "D",
  "go": "Go",
  "hs": "Haskell",
  "java": "Java",
  "kt": "Kotlin",
  "ml": "OCaml",
  "dpr": "Delphi",
  "pas": "Pascal",
  "pl": "Perl",
  "php": "PHP",
  "py": "Python",
  "rb": "Ruby",
  "rs": "Rust",
  "scala": "Scala",
  "js": "JavaScript"
}
