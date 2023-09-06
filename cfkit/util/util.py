from colorama import init, Fore, Back, Style
import sys
import re
from os import path, mkdir
from requests import get, HTTPError
from json import load

def path_exist_error(file_path, fileorDir):
  if path.exists(file_path):
    # raise FileExistsError(f"File exists '{path}'" if fileorDir == "f" else f"Directory exists '{path}'")
    print(f"File exists '{file_path}'" if fileorDir == 'f' else f"Directory exists '{file_path}'")
    sys.exit(1)


def check_path_existence(file_path, fileOrDir):
  if not path.exists(file_path):
    # raise FileNotFoundError(f"No such file: '{path}'" if fileOrDir == "f" else f"No such directory '{path}'")
    print(f"No such file: '{file_path}'" if fileOrDir == 'f' else f"No such directory '{file_path}'")
    sys.exit(1)


def check_status(response):
  try:
    response.raise_for_status()
  except HTTPError as e:
    print(f"HTTP Error: {e}")
    sys.exit(1)


def check_url(url: str, err_message, data, raise_err=False):
    # with open(path.join(config_folder, "valid_urls"), 'r') as file:
    #   pass
    response = get(url)
    check_status(response)
    codeforces_message = response.text
    contest_valid_bool = codeforces_message.find(f'Codeforces.showMessage("No such contests");') == -1
    problem_valid_bool = codeforces_message.find(f'Codeforces.showMessage("No such problem");') == -1
    if not (contest_valid_bool and problem_valid_bool):
      if raise_err:
        raise SyntaxError

      if contest_valid_bool and not problem_valid_bool:
        print(f"No such contests '{data}'")

      else:
        print(f"No such {err_message} '{data}'")
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
  problem_name = re.sub("[A-z]'(text|S)", "text", problem_name)
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


def retrieve_configuration() -> dict:
  with open(config_file, 'r', encoding="UTF-8") as file:
    return load(file)

def colored_text(message, print_statement=True, fore=True, style=True, back=False):
  init()

  # Define a regular expression pattern to match color tags like <blue> and </blue>
  fore_color_mapping = {None: None}
  if fore:
    fore_color_mapping = {
      "fore-black":          Fore.BLACK,
      "fore-red":            Fore.RED,
      "fore-green":          Fore.GREEN,
      "fore-yellow":         Fore.YELLOW,
      "fore-blue":           Fore.BLUE,
      "fore-magenta":        Fore.MAGENTA,
      "fore-cyan":           Fore.CYAN,
      "fore-white":          Fore.WHITE,
      "fore-bright-black":   Fore.LIGHTBLACK_EX,
      "fore-bright-red":     Fore.LIGHTRED_EX,
      "fore-bright-green":   Fore.LIGHTGREEN_EX,
      "fore-bright-yellow":  Fore.LIGHTYELLOW_EX,
      "fore-bright-blue":    Fore.LIGHTBLUE_EX,
      "fore-bright-magenta": Fore.LIGHTMAGENTA_EX,
      "fore-bright-cyan":    Fore.LIGHTCYAN_EX,
      "fore-bright-white":   Fore.LIGHTWHITE_EX
    }
  
  style_brightness_mapping = {None: None}
  if style:
    style_brightness_mapping = {
    "style-bright": Style.BRIGHT,
    "style-dim":    Style.DIM
    }
  
  back_color_mapping = {None: None}
  if back:
    back_color_mapping = {
      "back-black":          Back.BLACK,
      "back-red":            Back.RED,
      "back-green":          Back.GREEN,
      "back-yellow":         Back.YELLOW,
      "back-blue":           Back.BLUE,
      "back-magenta":        Back.MAGENTA,
      "back-cyan":           Back.CYAN,
      "back-white":          Back.WHITE,
      "back-bright-black":   Back.LIGHTBLACK_EX,
      "back-bright-red":     Back.LIGHTRED_EX,
      "back-bright-green":   Back.LIGHTGREEN_EX,
      "back-bright-yellow":  Back.LIGHTYELLOW_EX,
      "back-bright-blue":    Back.LIGHTBLUE_EX,
      "back-bright-magenta": Back.LIGHTMAGENTA_EX,
      "back-bright-cyan":    Back.LIGHTCYAN_EX,
      "back-bright-white":   Back.LIGHTWHITE_EX
    }

  pattern = r'<(.*?)>'
  color_pattern = re.compile(pattern)
  # Split the message using the color tags as delimiters
  parts = color_pattern.split(message)
  text = ""
  for part in parts:
    if part.startswith('/fore'):
      color = Fore.RESET
    elif part.startswith('/back'):
      color = Back.RESET
    elif part.startswith('/style'):
      color = Style.NORMAL
    else:
      color = fore_color_mapping.get(part, '')
      color += style_brightness_mapping.get(part, '')
      color += back_color_mapping.get(part, '')
    text += part if not color else color
  
  if not print_statement:
    return text
  print(text)


machine = sys.platform
problem_code_pattern = r"\A[1-9]{1}\d{,3}[A-z]\d?"
config_folder = path.join(path.expanduser("~"), "AppData\Roaming" if machine == "win32" else ".config", "cfkit")
config_file = path.join(config_folder, "platforms.json")
json_folder = path.join(path.dirname(path.dirname(__file__)), "json")
