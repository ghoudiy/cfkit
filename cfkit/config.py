"""
Documentation
"""
from os import path
from inspect import currentframe
from getpass import getpass
from json import dump#, load
from requests.utils import dict_from_cookiejar
from requests.cookies import RequestsCookieJar
from datetime import datetime, timedelta
from mechanicalsoup import StatefulBrowser

from cfkit.util.common import (
  read_json_file,
  # create_file_folder,
  display_horizontally,
  enter_number,
  write_json_file,
  resources_folder,
  conf_file,
  # config_folder,
  language_conf,
  language_conf_path,
  MACHINE,
  # json_folder
)

from cfkit.util.implementation import detect_implementation


def set_language_attributes(programming_language: str) -> str:
  """
  Documentation
  """
  command, save_command = detect_implementation(programming_language)
  execute_command, implementation = command[0], command[1]
  del command
  run_command = path.join(
    path.dirname(__file__),
    "util",
    "memory_usage.exe " if MACHINE == "win32" else "./memory_usage.exe"
  )
  if implementation == "compiler":
    run_command += (
      f" %%{{dir_name}}%%{'/./' if MACHINE != 'win32' else ''}%%{{output}}%%.exe "
      f"%%{{memory_limit}}%% %%{{output_memory}}%%_memory.out "
      f"%%{{input_file}}%% %%{{output_file}}%% \"{execute_command}\""
    )
  else:
    run_command += (
      f" \"{execute_command}\" %%{{memory_limit}}%% %%{{output_memory}}%%_memory.out "
      f"%%{{input_file}}%% %%{{output_file}}%%"
    )
  if save_command:
    language_conf[programming_language]["execute_command"] = execute_command
    language_conf[programming_language][
      "calculate_memory_usage_and_execution_time_command"] = run_command
    write_json_file(language_conf, language_conf_path, 4)

  return run_command

def set_default_language():
  """
  Documentation
  """
  default_language = conf_file["cfkit"]["default_language"]
  if not default_language:
    pass


def set_default_compiler(set_as_default: bool, programming_language: str) -> int:
  """
  Documentation
  """
  configuration = read_json_file(language_conf_path)
  if configuration[programming_language]["default_submission_language"] is None:
    languages = {
      "GNU GCC C11 5.1.0": 43,
      "Clang++20 Diagnostics": 80,
      "Clang++17 Diagnostics": 52,
      "GNU G++14 6.4.0": 50,
      "GNU G++17 7.3.0": 54,
      "GNU G++20 11.2.0 (64 bit, winlibs)": 73,
      "Microsoft Visual C++ 2017": 59,
      "GNU G++17 9.2.0 (64 bit, msys 2)": 61,
      "C# 8, .NET Core 3.1": 65,
      "C# 10, .NET SDK 6.0": 79,
      "C# Mono 6.8": 9,
      "D DMD32 v2.101.2": 28,
      "Go 1.19.5": 32,
      "Haskell GHC 8.10.1": 12,
      "Java 11.0.6": 60,
      "Java 17 64bit": 74,
      "Java 1.8.0_241": 36,
      "Kotlin 1.6.10": 77,
      "Kotlin 1.7.20": 83,
      "OCaml 4.02.1": 19,
      "Delphi 7": 3,
      "Free Pascal 3.0.2": 4,
      "PascalABC.NET 3.8.3": 51,
      "Perl 5.20.1": 13,
      "PHP 8.1.7": 6,
      "Python 2.7.18": 7,
      "Python 3.8.10": 31,
      "PyPy 2.7.13 (7.3.0)": 40,
      "PyPy 3.6.9 (7.3.0)": 41,
      "PyPy 3.9.10 (7.3.9, 64bit)": 70,
      "Ruby 3.0.0": 67,
      "Rust 1.66.0 (2021)": 75,
      "Scala 2.12.8": 20,
      "JavaScript V8 4.8.0": 34,
      "Node.js 12.16.3": 55
    }
    data = tuple(languages.keys())
    display_horizontally(data)

    user_choice = enter_number("Compiler index: ", "Compiler index: ", range(1, 36))

    print(data[user_choice-1])
    configuration[programming_language]["default_submission_language"] = data[user_choice-1]
    if set_as_default:
      write_json_file(configuration, language_conf_path)
    
    return languages[data[user_choice-1]]
  return configuration[programming_language]["default_submission_language"]
  

def login() -> (str, RequestsCookieJar):
  """
  Documentation
  """
  def valid_username(string):
    string_length = len(string)
    is_alnum = string.isalnum()
    bounds = 3 <= string_length <= 24
    if is_alnum and bounds:
      return True
    elif bounds and not is_alnum:
      i = 0
      test = True
      while test and i < string_length:
        test = string[i].isalnum() or string[i] in ("_", "-")
        i += 1
      return test
    else:
      return False

  browser = StatefulBrowser()
  session_path = resources_folder.joinpath("session.json")

  browser.open('https://codeforces.com/enter')
  form = browser.select_form('form[id="enterForm"]')
  
  username = input("Username: ")
  while not valid_username(username):
    username = input("Please type your username correctly.\nUsername: ")
  
  password = getpass()
  while len(password) < 5:
    password = getpass("Please type your password correctly.\nPassword: ")
    
  form.set("handleOrEmail", username)
  form.set("password", password)
  form.set('remember', True)

  browser.submit_selected()

  # Convert cookies to a dictionary
  cookie_dict = dict_from_cookiejar(browser.session.cookies)
  # Save the cookies to a JSON file
  session = {
    "cookies": cookie_dict,
    "cookies_expiration_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
    "username": username,
  }
  write_json_file(session, session_path)
  return username, cookie_dict
  

# create_file_folder(config_folder, 'd')
# create_file_folder(language_conf)
