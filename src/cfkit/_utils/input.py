"""
Documentation
"""

from typing import Any, Optional
from prompt_toolkit.shortcuts import confirm as promptConfirm

from cfkit._utils.print import display_horizontally, colored_text

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

def retype(data: str, input_type: str, _command: Optional[str] = None) -> str:
  """
  Documentation
  """
  from cfkit._utils.check import check_command
  if not confirm(f"\nConfirm the {input_type}"):
    if _command is not None:
      return retype(
        check_command(input(f"\nPlease retype the {input_type}:\n"), _command),
        input_type,
        _command
      )
    return retype(input(f"\nPlease retype the {input_type}:\n"), input_type)
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

def prompt(message, **kwargs):
  """
  Documentation
  """
  colored_text(message, end="", **kwargs)
  return input()
