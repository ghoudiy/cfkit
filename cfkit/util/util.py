from colorama import init, Fore, Back, Style
import sys
import re
from os import path, mkdir, get_terminal_size
from shutil import rmtree
from requests import get, HTTPError
from json import load
from configparser import ConfigParser, NoOptionError

def path_exist_error(file_path, fileorDir):
  if path.exists(file_path):
    colored_text(f"<f-red>File exists</f> '{file_path}'" if fileorDir == 'f' else f"<f-red>Directory exists</f> '{file_path}'")
    sys.exit(1)


def check_path_existence(file_path, fileOrDir):
  if not path.exists(file_path):
    colored_text(f"<f-red>No such file</f>: '{file_path}'" if fileOrDir == 'f' else f"<f-red>No such directory</f> '{file_path}'")
    sys.exit(1)

def check_status(response):
  try:
    response.raise_for_status()
  except HTTPError as e:
    colored_text(f"<f-red>HTTP Error</f>: {e}")
    sys.exit(1)


def check_url(url: str, code, contestId=0, raise_err=False):
    # with open(path.join(config_folder, "valid_urls"), 'r') as file:
    #   pass
    response = get(url)
    check_status(response)
    codeforces_message = response.text
    valid_contest = codeforces_message.find(f'Codeforces.showMessage("No such contests");') == -1
    valid_contest = valid_contest and codeforces_message.find(f'Codeforces.showMessage("No such contest");') == -1
    contest_started = codeforces_message.find(f'<div class="contest-state-phase">Before the contest</div>') == -1
    if not valid_contest:
      if contestId:
        colored_text(f"<f-red>No such contest</f> '{contestId}'")
        sys.exit(1)
      colored_text(f"<f-red>No such contest</f> '{code}'")
      sys.exit(1)
    
    elif not contest_started:
      colored_text(f"Contest has not started yet", ["f light magenta"])
      sys.exit(1)

    if not isinstance(code, int):
      if not codeforces_message.find(f'Codeforces.showMessage("No such problem");') == -1:
        if raise_err:
          raise SyntaxError
        colored_text(f"<f-red>No such problem</f> '{code}'")
        sys.exit(1)
    return response

def english_ending(x):
  x %= 100
  if x // 10 == 1:
    return "th"
  if x % 10 == 1:
    return "st"
  if x % 10 == 2:
    return "nd"
  if x % 10 == 3:
    return "rd"
  return "th"


def file_name(name, code):
  problem_name = re.sub("[A-z]'(text|S)", "text", name)
  problem_name = re.sub(r"\W", "_", problem_name)
  problem_name = re.sub(r"(___|__)", "_", problem_name)
  problem_name = f"{code}{problem_name[:-1]}" if problem_name[-1] == "_" else f"{code}{problem_name}"
  return problem_name


def yesOrNo(message):
  c = input(f"{message}? [Y/n] ").lower()
  if c in ("yes", "y", ""):
    return True
  elif c in ("no", "n"):
     return False
  else:
    yesOrNo(message)


def check_command(x, s):
  if isinstance(s, tuple):
    while x.find("{output}") == -1 or x.find("{file}") == -1:
      print(s)
      x = input("Please enter your command correctly:\n")
  else:
    while x.find("{file}") == -1:
      print(s)
      x = input("Please enter your command correctly:\n")
  return x


def confirm(x, z, __command = None):
    if not yesOrNo(f"Confirm the {z}"):
      if __command:
        return confirm(check_command(input(f"Please retype the {z}:\n"), __command), z, __command)
      return confirm(input(f"Please retype the {z}:\n"), z)
    return x


def enter_number(message1, error_message, Range):
  c = input(message1)
  while not c.isdigit() or int(c) not in Range:
    c = input(error_message)
  return int(c)

def read_json_file(x):
  with open(x, 'r', encoding="UTF-8") as file:
    return load(file)


def read_text_from_file(x):
  with open(x, 'r', encoding="UTF-8") as file:
    y = file.read()
  return y

def is_number(text):
  try:
    float(text)
    return True
  except ValueError:
    return False


def create_file_folder(path_to_file, fileType='f'):
  if not path.exists(path_to_file):
    if fileType == 'd':
      mkdir(path_to_file)
    else:
      with open(path_to_file, 'x'):
        pass
  return path.basename(path_to_file)


def colored_text(message: str, one_statement_color='', print_statement=True, input_statement=False):
  init(autoreset=True)

  def generate_color_code_from_components(s: str):
    order = ["\x1b[", "s-bright", "s-dim", "light"]
    p = s.find("bg")
    if p != -1:
      # Just make it works
      bg_light_color = s.find("(") != -1
      if bg_light_color:
        p1 = s[p:].find("+") + len(s[:p])
        s = s[:p1] + s[p1+1:]
        bg_index = s[:p].count("+")
        s = s.replace(" ", '').split("+")
        s.insert(0, (s[bg_index][4:-1].upper() + "_EX"))
        s[0] = Back.__dict__.get(("LIGHT" + s[0][:-8] + "_EX") if s[0][-8:] == "LIGHT_EX" else s[0].upper(), '')
        s[bg_index+1] = ""

      else:
        bg_index = s[:p].count("+")
        s = s.replace(" ", '').split("+")
        s.insert(0, s[bg_index][3:].upper())
        s[0] = Back.__dict__.get(s[0].upper(), '')
        s[bg_index+1] = ""

    else:
      s = s.replace(" ", '').split("+")
 
    r = [None] * 4
    for style in s:
      i = 0
      ok = False
      while not ok and i < 4:
        ok = style[:2] == order[i][:2]
        i += 1
      if not ok:
        r.append(style)
      else:
        r[i-1] = style

    colors = ""
    r = filter(bool, r)
    light = False
    for style in r:
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
    return input(message)

  if not print_statement:
    return message
  print(message)


def convert_to_bytes(memory: str):
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
    else:
      print("Couldn't recognize the memory size")
      sys.exit(1)
  return float(memory)

def folder_exists(folder_name):
  c = input(f"Another folder with the same name '{folder_name}' already exists\n[W]rite in the same folder or [R]eplace the folder or [C]reate a new one with another name? ").strip().lower()
  while c not in ('w', 'r', 'c'):
    c = input("[W]rite/[R]eplace/[C]reate]").strip().lower()

  if c == 'r':
    rmtree(path.join(path, folder_name))
    folder_path = create_file_folder(folder_name, 'd')

  elif c == 'c':
    name = input("Folder name: ").strip()
    path_exist_error(name, "d")
    folder_path = create_file_folder(name, 'd')

  else:
    folder_path = folder_name
  
  return folder_path


def display_horizontally(data: tuple):
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
    formatted_row = "  ".join(col[row].ljust(max_item_width) if row < len(col) else ' ' * max_item_width for col in columns)
    print(formatted_row)


machine = sys.platform
problem_code_pattern = r"\A[1-9]{1}\d{,3}[A-z]\d?"
json_folder = path.join(path.dirname(path.dirname(__file__)), "json")
config_folder = path.join(path.expanduser("~"), "AppData\Roaming" if machine == "win32" else ".config", "cfkit")
template_folder = path.join(config_folder, "templates")
language_conf = read_json_file(path.join(config_folder, "languages.json"))
conf_file = ConfigParser()
conf_file.read(path.join(config_folder, "cfkit.conf"))
color_conf = ConfigParser()
color_conf.read(path.join(config_folder, "colorschemes", conf_file["cfkit"]["color_scheme"]))