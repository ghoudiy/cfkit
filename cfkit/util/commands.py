"""
Detect the implementation type (compiler or interpreter) from the provided file
and execute it with sample input and output while managing memory usage.
"""

from os import path
from subprocess import run, CalledProcessError
# from cfkit.util.common import colored_text
# from subprocess import run, TimeoutExpired
# from threading import Thread


def execute_file(
    file: str,
    problem_index: str,
    input_path: str,
    output_path: str,
    errors_memory_time_path: str,
    memory_limit: float,
    run_command: str,
    # time_limit: float,
    # test_num: int,
  ) -> None:
  '''
  Execute the specified file with provided input, capture the output,
  and save it to the specified path while controlling memory usage in a Go program.
  '''
  run_command = run_command.replace("%%{file}%%", file)
  run_command = run_command.replace("%%{memory_limit}%%", str(memory_limit))
  run_command = run_command.replace("%%{output_memory}%%", errors_memory_time_path)
  run_command = run_command.replace("%%{input_file}%%", input_path)
  run_command = run_command.replace("%%{output_file}%%", output_path)
  run_command = run_command.replace("%%{output}%%", problem_index)
  run_command = run_command.replace("%%{dir_name}%%", path.dirname(input_path))
  
  try:
    returncode = run(run_command, shell=True, check=True).returncode
  except CalledProcessError as err:
    returncode = err.returncode
  finally:
    return returncode

  # def target():
  #   run(run_command, shell=True, check=True)

  # thread = Thread(target=target)
  # thread.start()
  # thread.join(timeout=time_limit)

  # if thread.is_alive():
  #   colored_text(
  #     f"<error>Warning</>: The time limit <bright_text>may be</> exceeded for test case {test_num}."
  #     " Please wait for a more precise result."
  #   )
  #   thread.join()

if __name__ == "__main__":
  pass
