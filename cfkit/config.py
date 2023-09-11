from os import path
from getpass import getpass
from json import dump, load
from mechanicalsoup import StatefulBrowser

from cfkit.util.util import (
  read_json_file,
  create_file_folder,
  display_horizontally,
  conf_file,
  config_folder,
  language_conf,
  machine,
  json_folder
)

from cfkit.util.implementation import detect_implementation


def set_language_attributes(programming_language, configuration):
  execute_command = language_conf["execute_command"]

  execute_command, implementation = detect_implementation(programming_language)
  
  run_command = path.join(path.dirname(__file__), "util", "memory_usage.exe " if machine == "win32" else "./memory_usage.exe")
  
  if implementation == "compiler":
    run_command += f" %%{{dir_name}}%%{'/./' if machine != 'win32' else ''}%%{{output}}%%.exe %%{{memory_limit}}%% %%{{output_memory}}%%_memory.out %%{{input_file}}%% %%{{output_file}}%% \"{execute_command}\""
  
  else:
    run_command += f" \"{execute_command}\" %%{{memory_limit}}%% %%{{output_memory}}%%_memory.out %%{{input_file}}%% %%{{output_file}}%%"

  # language_conf["extension"] = 
  language_conf["execute_command"] = execute_command
  language_conf["calculate_memory_usage_and_execution_time_command"] = run_command
  with open(language_conf, 'w', encoding="UTF-8") as platforms_file:
    dump(configuration, platforms_file, indent=4)


def default_language():
  default_language = conf_file["cfkit"]["default_language"]


def default_compiler():

  configuration = read_json_file(language_conf)
  if configuration["default_compiler"] is None:
    LANGUAGES = {
      "1. GNU GCC C11 5.1.0": 43,
      "2. Clang++20 Diagnostics": 80,
      "3. Clang++17 Diagnostics": 52,
      "4. GNU G++14 6.4.0": 50,
      "5. GNU G++17 7.3.0": 54,
      "6. GNU G++20 11.2.0 (64 bit, winlibs)": 73,
      "7. Microsoft Visual C++ 2017": 59,
      "8. GNU G++17 9.2.0 (64 bit, msys 2)": 61,
      "9. C# 8, .NET Core 3.1": 65,
      "10. C# 10, .NET SDK 6.0": 79,
      "11. C# Mono 6.8": 9,
      "12. D DMD32 v2.101.2": 28,
      "13. Go 1.19.5": 32,
      "14. Haskell GHC 8.10.1": 12,
      "15. Java 11.0.6": 60,
      "16. Java 17 64bit": 74,
      "17. Java 1.8.0_241": 36,
      "18. Kotlin 1.6.10": 77,
      "19. Kotlin 1.7.20": 83,
      "20. OCaml 4.02.1": 19,
      "21. Delphi 7": 3,
      "22. Free Pascal 3.0.2": 4,
      "23. PascalABC.NET 3.8.3": 51,
      "24. Perl 5.20.1": 13,
      "25. PHP 8.1.7": 6,
      "26. Python 2.7.18": 7,
      "27. Python 3.8.10": 31,
      "28. PyPy 2.7.13 (7.3.0)": 40,
      "29. PyPy 3.6.9 (7.3.0)": 41,
      "30. PyPy 3.9.10 (7.3.9, 64bit)": 70,
      "31. Ruby 3.0.0": 67,
      "32. Rust 1.66.0 (2021)": 75,
      "33. Scala 2.12.8": 20,
      "34. JavaScript V8 4.8.0": 34,
      "35. Node.js 12.16.3": 55
    }
    data = tuple(LANGUAGES.keys())
    display_horizontally(data)
    
    c = input("Compiler index: ")
    while not c.isdigit() or not (1 <= int(c) <= 35):
      c = input("Compiler index: ")
    
    configuration["default_compiler"] = data[int(c)-1][data[int(c)-1].find(" ")+1:]
    with open(language_conf, 'w') as file:
      dump(configuration, file, indent=4)


def login():
    browser = StatefulBrowser()
    login_url = 'https://codeforces.com/enter'
    browser.open(login_url)
    browser.select_form('form[id="enterForm"]')
    browser["handleOrEmail"] = input("Handle/Email: ")
    browser["password"] = getpass()
    browser.submit_selected()

    # Check if login was successful
    pass




# create_file_folder(config_folder, 'd')
# create_file_folder(language_conf)
# create_file_folder(path.join(config_folder, 'valid_urls'), 'd')
# create_file_folder(path.join(config_folder, 'valid_urls', "contests.json"))
# create_file_folder(path.join(config_folder, 'valid_urls', "A"))
