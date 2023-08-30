import sys
from os import path
import re
from requests import get, HTTPError

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
  problem_name = re.sub("[A-z]'(s|S)", "s", problem_name)
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


def enter_number(message1, message2, Range):
  c = input(message1)
  while not c.isdigit() or int(c) not in Range:
    c = input(message2)

machine = sys.platform
problem_code_pattern = r"\A[1-9]{1}\d{,3}[A-z]\d?"
config_folder = path.join(path.expanduser("~"), "AppData\Roaming" if machine == "win32" else ".config", "cfkit")
config_file = path.join(config_folder, "platforms.json")