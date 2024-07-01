"""
Documentation
"""

from math import isclose

from cfkit.utils.check import is_number
from cfkit.utils.common import english_ending


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
  if word_or_number == "number":
    expected_value_as_float = float(expected_value)
    observed_value_as_float = float(observed_value)
    return (
      "Wrong answer:" + (f"{line}{english_ending(line)} line," if line > 0 else '') + " "
      f"{column}{english_ending(column)} numbers "
      f"differ - expected: '{expected_value}', found: '{observed_value}'"
    ) + (
      f" error = '{(abs(expected_value_as_float - observed_value_as_float) / observed_value_as_float):5f}'\n\n" if (
        word_or_number == 'numbers' and int(expected_value) != expected_value) else '\n\n'
    )

  return (
  "Wrong answer:" + (f"{line}{english_ending(line)} line," if line > 0 else '') + " "
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

  wrong_answer_message = None
  if not equal:
    wrong_answer_message = wrong_answer_verdict(
      line,
      column,
      numbers_or_words,
      expected_value,
      observed_value
    )
    return False, wrong_answer_message
  return True, wrong_answer_message

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
    check_formatting: bool
  ) -> tuple[bool, str] | tuple[bool, None]:
  """
  Documentation
  """
  wrong_answer_message = None
  if check_formatting:
    check_length(
      expected,
      observed,
      "Wrong answer: expected %1% line(s), found %2%\n\n",
      "Formatting error",
      "error_3"
    )

  equal = False
  if check_formatting:
    for line_number, values in enumerate(zip(expected, observed)):
      expected_line = values[0].split(' ')
      observed_line = values[1].split(' ')
      check_length(
        expected_line,
        observed_line,
        f"Wrong answer: {line_number + 1}{english_ending(line_number + 1)} line, "
        "expected %1% value(s), found %2%\n\n",
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
    data = [[], []]
    if len(observed) == 0 and len(expected) > 0:
      equal, wrong_answer_message = compare_values(expected[0].split(" ")[0], '', 0, 1)

    for line_number, values in enumerate(zip(expected, observed)):
      expected_line = values[0].split(' ')
      observed_line = values[1].split(' ')
      data[0].extend(expected_line)
      data[1].extend(observed_line)
    

    data[0] = [item for item in data[0] if item]
    data[1] = [item for item in data[1] if item]
    print(data[0], data[1])
    check_length(
      data[0], # expected
      data[1], # observed
      "Wrong answer: expected %1% value(s), found %2%\n\n",
      "Wrong answer",
      "wrong"
    )

    for column_num, output in enumerate(zip(data[0], data[1])):
      equal, wrong_answer_message = compare_values(output[0], output[1], 0, column_num + 1)
      if not equal:
        return equal, wrong_answer_message

  # End of check_answer() function
  return True, None
