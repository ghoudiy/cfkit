"""
Documentation
"""

from sys import exit as sysExit
from os import get_terminal_size

from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style
from cfkit._utils.variables import color_conf

def colored_text(
  message: str,
  one_color: str = "",
  input_statement: bool = False,
  exit_code_after_print_statement: int = 0,
  **kwargs
) -> str:
  """
  Documentation
  """

  style = Style(list(color_conf["theme"].items()))

  if one_color:
    message = f"<{one_color}>{message}</{one_color}>"

  if input_statement:
    return prompt(HTML(message), style=style)

  elif exit_code_after_print_statement == 0:
    print_formatted_text(HTML(message), style=style, **kwargs)

  else:
    print_formatted_text(HTML(message), style=style, **kwargs)
    sysExit(exit_code_after_print_statement)

def display_horizontally(data: tuple) -> None:
  """
  Display data horizontally
  """
  data = tuple(map(lambda x: f"{x[0]}. {x[1]}", enumerate(data, 1)))
  terminal_width = get_terminal_size().columns
  max_item_width = max(len(item) for item in data)
  # Add some padding between columns
  num_columns = max(1, terminal_width // (max_item_width + 2))

  # Distribute items into columns
  items_per_column = -(-len(data) // num_columns)  # Ceiling division
  columns = [data[i:i + items_per_column] for i in range(0, len(data), items_per_column)]

  # Calculate the number of rows needed to accommodate the columns
  num_rows = max(len(col) for col in columns)

  # Format and print the output using textwrap
  for row in range(num_rows):
    formatted_row = "  ".join(col[row].ljust(max_item_width) if row < len(
      col) else ' ' * max_item_width for col in columns)

    print(formatted_row)
