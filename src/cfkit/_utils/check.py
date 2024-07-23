"""
Documentation
"""

from os import path as osPath
from requests import HTTPError

from cfkit._utils.print import colored_text

def raise_error_if_path_exists(file_path: str, file_or_dir: str):
  """
  Documentation
  """
  if osPath.exists(file_path):
    colored_text(
      f"<error_4>File exists</error_4> &apos;{file_path}&apos;"
        if file_or_dir == 'f' else
      f"<error_4>Directory exists</error_4> &apos;{file_path}&apos;",
      exit_code_after_print_statement=4
    )

def raise_error_if_path_missing(file_path: str, file_or_dir):
  """
  Documentation
  """
  if not osPath.exists(file_path):
    colored_text(
      f"<error_4>No such file</error_4>: &apos;{file_path}&apos;"
        if file_or_dir == 'f' else
      f"<error_4>No such directory</error_4> '{file_path}'",
      exit_code_after_print_statement=4
    )

def check_status(response):
  """
  Documentation
  """
  try:
    response.raise_for_status()
  except HTTPError as err:
    colored_text(f"<error_5>HTTP Error</error_5>: {err}", exit_code_after_print_statement=5)

def check_command(command: str, message: str | tuple) -> str:
  """
  Documentation
  """
  if isinstance(message, tuple):
    while command.find("%%{output}%%") == -1 or command.find("%%{file}%%") == -1:
      colored_text(message[0])
      command = input("Please enter your command correctly:\n")
  else:
    while command.find("%%{file}%%") == -1:
      colored_text(message)
      command = input("Please enter your command correctly:\n")
  return command

def is_number(text: str) -> bool:
  """
  Documentation
  """
  try:
    float(text)
    return True
  except ValueError:
    return False

def check_file(file_path) -> str:
  """
  Documentation
  """
  raise_error_if_path_missing(file_path, 'f')
  while not osPath.isfile(file_path):
    file_path = colored_text(
      "The path you provided is not a file path"
      "\nPlease provide <bright_text>an existing file path</bright_text> instead: ",
      input_statement=True
    )
    raise_error_if_path_missing(file_path, 'f')
  return file_path
