"""
Detect the implementation type (compiler or interpreter) from the provided file
and execute it with sample input and output while managing memory usage.
"""

from os import path
from sys import exit as sysExit
from subprocess import run

from cfkit.util.common import EXTENSIONS, read_json_file, language_conf_path
from cfkit.config import set_language_attributes


def execute_file(file: str, input_path: str, output_path: str, memory_limit: float, *args) -> None:
  '''
  Execute the specified file with provided input, capture the output,
  and save it to the specified path while controlling memory usage in a Go program.
  '''
  ext = file[file.find(".")+1:]
  if ext == file:
    print(
      "\nPlease add the appropriate file extension to the file name.",
      "This ensures accurate language identification."
    )
    sysExit(1)

  programming_language = EXTENSIONS.get(ext)
  if programming_language is None:
    print("Oops! It looks like that the provided language is not supported by Codeforces.")
    sysExit(1)

  language_conf = read_json_file(language_conf_path)
  execute_command = language_conf[programming_language]["execute_command"]
  if execute_command is None:
    run_command = set_language_attributes(programming_language)
  else:
    run_command = read_json_file(language_conf_path)[programming_language]\
    ["calculate_memory_usage_and_execution_time_command"]

  output = path.basename(input_path)
  output = output[:output.find("_")]
  run_command = run_command.replace("%%{file}%%", file)
  run_command = run_command.replace("%%{memory_limit}%%", str(memory_limit))
  run_command = run_command.replace("%%{output_memory}%%", output_path[:-4])
  run_command = run_command.replace("%%{input_file}%%", input_path)
  run_command = run_command.replace("%%{output_file}%%", output_path)
  run_command = run_command.replace("%%{output}%%", output)
  run_command = run_command.replace("%%{dir_name}%%", path.dirname(input_path))
  run(run_command, shell=True, check=True)

  # Retrieve python execution command to prevent opening languages.json file again in run_demo function
  if args:
    run_command = run_command[run_command.find('cfkit/util/./memory_usage.exe "')+31:]
    return run_command[:run_command.find(" ")]
  return None

if __name__ == "__main__":
  pass
