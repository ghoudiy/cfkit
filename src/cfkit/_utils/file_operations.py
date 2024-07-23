"""
Documentation
"""
# Standard Library Imports
from sys import exit as sysExit
from json import dump
from json import load
from typing import Any
from pathlib import Path
from shutil import rmtree
from os import remove as osRemove

# Cfkit Imports
from cfkit._utils.check import raise_error_if_path_exists
from cfkit._utils.input import enter_number


def read_json_file(json_file_path: str | Path) -> dict[Any, Any]:
  """
  Documentation
  """
  with open(json_file_path, 'r', encoding="UTF-8") as file:
    content = load(file)
  return content

def read_text_from_file(file_path: str) -> str:
  """
  Documentation
  """
  with open(file_path, 'r', encoding="UTF-8") as file:
    content = file.read()
  return content

def write_json_file(data: object, file_path: str, spaces: int = 4) -> None:
  """
  Write data to a json file
  """
  with open(file_path, 'w', encoding="UTF-8") as file:
    dump(data, file, indent=spaces)

def write_text_to_file(data: str, file_path: str):
  """
  Write text to a file
  """
  with open(file_path, 'w', encoding="UTF-8") as file:
    file.write(data)

def create_file_folder(
    path_to_file: str,
    file_or_dir: str = 'f',
    skip_existence: bool = False
  ) -> Path:
  """
  Documentation
  """
  path_to_file: Path = Path(path_to_file)
  if skip_existence:
    # Empty the file
    with path_to_file.open('w', encoding="UTF-8"):
      pass

  elif not path_to_file.exists():
    if file_or_dir == 'd':
      path_to_file.mkdir()
    else:
      path_to_file.touch()

  else:
    path_to_file = folder_file_exists(path_to_file, "directory" if file_or_dir == "d" else "file")

  return path_to_file

def remove_files(file_list) -> None:
  """
  Documentation
  """
  for file in file_list:
    osRemove(file)

def folder_file_exists(name: str, file_or_dir: str) -> str:
  """
  Documentation
  """
  print(
    f"\nAnother {file_or_dir} with the name '{name}' already exists.\n"
    "1. Write in the same directory" if file_or_dir == "directory" else "Override the file",
    f"2. Replace the old {file_or_dir} with the new one",
    f"3. Create a new {file_or_dir} with another name",
    "4. Abort"
  )
  user_choice = enter_number("What do you want to do? ", "What do you want to do? ", range(1, 5))

  if user_choice == 3:
    name = input(f"{file_or_dir.capitalize()} name: ").strip()
    raise_error_if_path_exists(name, file_or_dir[0])
    folder_path = create_file_folder(name, file_or_dir[0])

  elif user_choice == 2:
    rmtree(name)
    folder_path = create_file_folder(name, file_or_dir[0])

  elif user_choice == 1:
    folder_path = name

  else:
    sysExit(1)

  return folder_path
