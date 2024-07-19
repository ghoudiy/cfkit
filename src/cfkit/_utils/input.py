"""
Documentation
"""

from typing import Any
from prompt_toolkit.shortcuts import confirm as promptConfirm

from cfkit._utils.check import check_command
from cfkit._utils.print import display_horizontally

def select_option(
    message: str,
    data: list,
    index: bool = True,
    disp_horizontally: bool = True
  ) -> int | Any:
  """
  Documentation
  """
  if disp_horizontally:
    display_horizontally(data)
  else:
    for i in range(len(data)):
      print(f"{i + 1}. {data[i]}")

  choice = enter_number(
    message,
    message,
    range(1, len(data)+1)
  )
  if index:
    return choice
  return data[choice-1]

def retype(data: str, input_type: str, _command: str = None) -> str:
  """
  Documentation
  """
  if not confirm(f"Confirm the {input_type}"):
    if _command is not None:
      return retype(
        check_command(input(f"Please retype the {input_type}:\n"), _command),
        input_type,
        _command
      )
    return retype(input(f"Please retype the {input_type}:\n"), input_type)
  return data

def enter_number(message: str, error_message: str, num_range: range) -> int:
  """
  Documentation
  """
  num = input(message).strip()
  while not num.isdigit() or int(num) not in num_range:
    num = input(error_message).strip()
  return int(num)

def confirm(message: str, default: bool = True):
  """
  Documentation
  """
  if default is True:
    return promptConfirm(message, " [Y/n] ") in ("", True)
  return promptConfirm(message, " [y/N] ") is True
