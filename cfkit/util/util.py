from colorama import init, Fore, Back, Style
import sys
import re
from os import path, mkdir
from requests import get, HTTPError
from json import load
from configparser import ConfigParser

def path_exist_error(file_path, fileorDir):
  if path.exists(file_path):
    # raise FileExistsError(f"File exists '{path}'" if fileorDir == "f" else f"Directory exists '{path}'")
    colored_text(f"<f-red>File exists</f> '{file_path}'" if fileorDir == 'f' else f"<f-red>Directory exists</f> '{file_path}'")
    sys.exit(1)


def check_path_existence(file_path, fileOrDir):
  if not path.exists(file_path):
    # raise FileNotFoundError(f"No such file: '{path}'" if fileOrDir == "f" else f"No such directory '{path}'")
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


def check_command(x, L):
  while x.find("{output}") == -1 or x.find("{file}") == -1:
    print("\n" + "\n".join(L[:-2]))
    x = input("Command: ")
  return x


def confirm(x, z, __command = []):
    if not yesOrNo(f"Confirm the {z}"):
      if __command:
        return confirm(check_command(input(f"Please retype the {z}:\n"), __command), "command", __command)
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


def colored_text(message: str, one_statement_color="", output="text", print_statement=True, input_statement=False):
  init(autoreset=True)

  def identify_color(s: str):
    order = ["bg-", "bright", "light"]
    # s = s.replace(" ", "").split(")")
    print(s)
    pattern = r'bg-\((.*?)\)'
    color_pattern = re.compile(pattern)
    parts = color_pattern.split(s)
    print(parts)
    exit()
    # Split the message using the color tags as delimiters
    print(s)
    r = [None] * 3
    for j, style in enumerate(s):
      i = 0
      ok = False
      while not ok and i < 3:
        ok = re.search(order[i], style)
        i += 1
      if not ok:
        r.append(style)
      else:
        r[i-1] = style
    print(r)
    exit()

    if s.find("light") != -1:
      s += "_EX"

    if s[0] == 'f':
      color = Fore.__dict__.get(s[1:].upper(), '')
    elif s[0] == 's':
      color = Style.__dict__.get(s[1:].upper(), '')
    else:
      color = Back.__dict__.get(s[1:].upper(), '')
    return color

  if one_statement_color:
    text = identify_color(one_statement_color) + message
  else:
    pattern = r'<(.*?)>'
    color_pattern = re.compile(pattern)
    # Split the message using the color tags as delimiters
    parts = color_pattern.split(message)
    print(parts)
    text = ""
    for part in parts:
      if part.startswith('/f'):
        color = Fore.RESET
      elif part.startswith('/b'):
        color = Back.RESET
      elif part.startswith('/s'):
        color = Style.NORMAL
      else:
        color = color_conf.get(part)
      text += part if not color else color
  
  if input_statement:
    return input(text)

  if not print_statement:
    return text
  print(text)


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


# def retrieve_configuration() -> dict:
#   with open(language_conf_file, 'r', encoding="UTF-8") as file:
#     return load(file)


machine = sys.platform
problem_code_pattern = r"\A[1-9]{1}\d{,3}[A-z]\d?"
json_folder = path.join(path.dirname(path.dirname(__file__)), "json")
config_folder = path.join(path.expanduser("~"), "AppData\Roaming" if machine == "win32" else ".config", "cfkit")
language_conf_file = read_json_file(path.join(config_folder, "languages.json"))
conf_file = ConfigParser()
conf_file.read(path.join(config_folder, "cfkit.conf"))
color_conf = ConfigParser()
color_conf.read(path.join(config_folder, "colorschemes", conf_file["cfkit"]["color_scheme"]))

# message = f"Please run <{color_conf['configuration_errors']}>'cf config'</f> command to set your favorite programming language."
message = f"contestID must be an integer"
colored_text(message, color_conf["theme"]["user_input_errors"])