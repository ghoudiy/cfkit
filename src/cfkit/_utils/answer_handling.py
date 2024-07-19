"""
Documentation
"""
from math import isclose
from collections import Counter

from cfkit._utils.check import is_number
from cfkit._utils.common import english_ending, trim_data


def wrong_answer_verdict(
    line: int,
    column: int,
    word_or_number: str,
    expected_value: str,
    observed_value: str
  ) -> str:
  '''
  verdict wrong answer message
  '''
  if word_or_number == "numbers":
    expected_value_as_float = float(expected_value)
    observed_value_as_float = float(observed_value)
    return (
      "Wrong answer:" + (f"{line}{english_ending(line)} line," if line > 0 else '') + " "
      f"{column}{english_ending(column)} numbers "
      f"differ - expected: '{expected_value}', found: '{observed_value}' "
    ) + (
      f"error = '{(abs(expected_value_as_float - observed_value_as_float) / observed_value_as_float):5f}'" if (
        int(expected_value) != float(expected_value)) else ''
    )

  return (
  "Wrong answer:" + (f"{line}{english_ending(line)} line, " if line > 0 else '') + " "
  f"{column}{english_ending(column)} words "
  f"differ - expected: '{expected_value}', found: '{observed_value}'"
  )

def compare_values(expected_value, observed_value, line, column) -> bool:
  """
  Compare two values only
  """
  if is_number(expected_value) and is_number(observed_value):
    num1 = float(expected_value)
    num2 = float(observed_value)
    equal = isclose(num1, num2, rel_tol=1.5E-5 + 1E-15)
    numbers_or_words = 'numbers'
  else:
    equal = expected_value == observed_value
    numbers_or_words = 'words'

  if not equal:
    wrong_answer_message = wrong_answer_verdict(
      line,
      column,
      numbers_or_words,
      expected_value,
      observed_value
    )
    return False, wrong_answer_message
  return True, None

def check_length(line1, line2, message, err_type: str, one_color: str) -> None:
  """
  Documentation
  """
  if (line1_length:=len(line1)) != (line2_length:=len(line2)):
    message = message.replace('%1%', str(line1_length)).replace('%2%', str(line2_length))
    if line1_length > 1:
      message = message.replace("(s)", 's')
    else:
      message = message.replace("(s)", '')

    raise InterruptedError([err_type, message, one_color])

def check_answer(
    expected: list[str],
    observed: list[str],
    any_order: bool,
    multiple_answers: bool,
    check_formatting: bool,
    expected_str: str
  ) -> tuple[bool, str | bool, None]:
  """
  Documentation
  """
  def compare(expected):
    if check_formatting:
      check_length(
        expected,
        observed,
        "Wrong answer: expected %1% line(s), found %2%",
        "Formatting error",
        "error_3"
      )
      for line_number, values in enumerate(zip(expected, observed)):
        expected_line = values[0].split(' ')
        observed_line = values[1].split(' ')
        check_length(
          expected_line,
          observed_line,
          f"Wrong answer: {line_number + 1}{english_ending(line_number + 1)} line, "
          "expected %1% value(s), found %2%",
          "Formatting error",
          "error_3"
        )
        for column_number, column_value in enumerate(zip(expected_line, observed_line)):
          # column_value[0] is the exepected value and column_value[1] is the observed value
          equal, wrong_answer_message = compare_values(
            column_value[0],
            column_value[1],
            line_number + 1,
            column_number + 1
          )
          if not equal:
            return False, wrong_answer_message

    else:
      expected_trimmed = trim_data(expected)
      observed_trimmed = trim_data(observed)
        #* Compare the results if the output is an integer or a string
      if expected_trimmed == observed_trimmed or (
        any_order and
        Counter(expected_trimmed) == Counter(observed_trimmed)
      ):
        return True, None

      check_length(
        expected_trimmed,
        observed_trimmed,
        "Wrong answer: expected %1% value(s), found %2%",
        "Wrong answer",
        "wrong"
      )

      for column_num, output in enumerate(zip(expected_trimmed, observed_trimmed)):
        equal, wrong_answer_message = compare_values(output[0], output[1], 0, column_num + 1)
        if not equal:
          return equal, wrong_answer_message

    return True, None

  if multiple_answers:
    accpeted = None
    expected_str = expected_str.split("\n# another answer\n")
    equal = False
    wrong_answer_messages = "The output doesn't match any of the answers. Errors:\n"
    for i in range(len(expected_str)):
      try:
        equal, wrong_answer_message = compare(expected_str[i].split("\n"))
        wrong_answer_messages += (f"Answer {i + 1}: {wrong_answer_message}" + "\n") if not equal else ''
      except InterruptedError as err:
        wrong_answer_messages += f"Answer {i + 1}: {err.args[0][1]}" + "\n"
      finally:
        accpeted = accpeted or equal

    if not accpeted:
      return False, wrong_answer_messages
    return True, None

  return compare(expected)
