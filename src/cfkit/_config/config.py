"""
Documentation
"""
from os import path as osPath
from pathlib import Path

from cfkit._utils.file_operations import read_json_file, write_json_file
from cfkit._utils.input import select_option
from cfkit._config.implementation import detect_implementation

from cfkit._utils.variables import language_conf_path, MACHINE

def set_language_attributes(programming_language: str) -> str:
  """
  Documentation
  """
  command, save_command, default_implementation = detect_implementation(programming_language)
  command, implementation = command[0], command[1]
  calculate_memory_usage_and_execution_time_command = str(Path(__file__).parent.parent.joinpath(
    "_dependencies",
    "memory_time_usage.exe " if MACHINE == "win32" else "./memory_time_usage "
  ))
  if implementation == "compiler":
    if MACHINE == "win32":
      execute_command = osPath.join("%%{dir_name}%%", "%%{output}%%.exe")
    else:
      execute_command = osPath.join("%%{dir_name}%%", "./%%{output}%%")

    calculate_memory_usage_and_execution_time_command += f'"{execute_command}" ' + (
      "%%{time_mem_err_output_file}%% "
      "%%{input_file}%% %%{output_file}%%"
    )
  else:
    calculate_memory_usage_and_execution_time_command += (
      f" \"{command}\" %%{{time_mem_err_output_file}}%% "
      "%%{input_file}%% %%{output_file}%%"
    )

  if MACHINE == "win32" and isinstance(command, str) and command.find("%%{output}%%.exe") == -1:
    command = command.replace("%%{output}%%", "%%{output}%%.exe")

  if save_command:

    language_conf = read_json_file(language_conf_path)
    if implementation == "compiler":
      language_conf[programming_language]["compile_command"] = command
      language_conf[programming_language]["execute_command"] = execute_command
      language_conf[programming_language][
        "calculate_memory_usage_and_execution_time_command"
      ] = calculate_memory_usage_and_execution_time_command
    else:
      language_conf[programming_language]["execute_command"] = command
      language_conf[programming_language][
        "calculate_memory_usage_and_execution_time_command"
      ] = calculate_memory_usage_and_execution_time_command
    if default_implementation:
      language_conf[programming_language]["default_implementation"] = default_implementation
    write_json_file(language_conf, language_conf_path, 4)

  if implementation == "compiler":
    return command, execute_command, calculate_memory_usage_and_execution_time_command
  return None, command, calculate_memory_usage_and_execution_time_command

def set_default_submission_language(set_as_default: bool, programming_language: str) -> int:
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

    user_choice = select_option("Compiler index: ", tuple(languages.keys()), index=False)

    configuration[programming_language]["default_submission_language"] = user_choice
    if set_as_default:
      write_json_file(configuration, language_conf_path)

    return languages[user_choice]
  return configuration[programming_language]["default_submission_language"]
