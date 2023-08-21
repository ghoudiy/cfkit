import sys
import os
import re
from bs4 import BeautifulSoup
from requests import get

def path_exist_error(path, fileorDir):
  if os.path.exists(path):
    # raise FileExistsError(f"File exists '{path}'" if fileorDir == "f" else f"Directory exists '{path}'")
    print(f"File exists '{path}'" if fileorDir == 'f' else f"Directory exists '{path}'")
    sys.exit(1)


def check_path_existence(path, fileOrDir):
  if not os.path.exists(path):
    # raise FileNotFoundError(f"No such file: '{path}'" if fileOrDir == "f" else f"No such directory '{path}'")
    print(f"No such file: '{path}'" if fileOrDir == 'f' else f"No such directory '{path}'")
    sys.exit(1)


def check_contest_id(contestId: int):    
    ok = isinstance(contestId, int)
    if isinstance(contestId, str) and not ok  and contestId.isdigit():
      contestId = int(contestId)
    if ok:
      response = get(f"https://codeforces.com/problemset/")
      response.raise_for_status()
      ub = response.text   
      ub = ub[ub.find('<a href="/problemset/problem/') + 29:]
      ub = BeautifulSoup(ub[:ub.find('/')], "html.parser") # Or to the last <script> tag
      if not 1 <= contestId <= int(str(ub)):
        # raise SyntaxError(f"invalid contestId '{contestId}'")
        print(f"Invalid contestId '{contestId}'")
        sys.exit(1)
    else: 
      # raise ValueError("contestId must be an integer")
        print(f"Contest ID must be an integer")
        sys.exit(1)


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
  name = re.sub("[A-z]'(s|S)", "s", name)
  name = re.sub(r"\W", "_", name)
  name = re.sub(r"(___|__)", "_", name)
  name = f"{code}{name[:-1]}" if name[-1] == "_" else f"{code}{name}"
  return name

machine = sys.platform