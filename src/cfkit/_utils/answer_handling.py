"""
Documentation
"""
from math import isclose
from collections import Counter

from cfkit._utils.common import (
  english_ending,
  trim_data,
  replace_non_xml_valid_characters,
  fill_checker_log_normal_way,
  fill_checker_log_list,
  remove_empty_lines
)
from cfkit._utils.variables import separator, conf_file

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
      "<wrong>Wrong answer</wrong>:" + (f" {line}{english_ending(line)} line," if line > 0 else '') + ""
      f" {column}{english_ending(column)} numbers - "
      f"expected: '{expected_value}', found: '{observed_value}'"
    ) + (
      f", error = {(abs(expected_value_as_float - observed_value_as_float) / observed_value_as_float):5f}" if (
        int(expected_value_as_float) != expected_value_as_float) else ''
    )

  return (
  "<wrong>Wrong answer</wrong>:" + (f" {line}{english_ending(line)} line," if line > 0 else '') + ""
  f" {column}{english_ending(column)} words - "
  f"expected: '{replace_non_xml_valid_characters(expected_value)}', found: '{replace_non_xml_valid_characters(observed_value)}'"
  )

def compare_values(expected_value, observed_value, line, column) -> bool:
  """
  Compare two values only
  """
  try: # if values are integers
    equal = int(expected_value) == int(observed_value)
    numbers_or_words = 'numbers'
  except ValueError:
    try: # if values are floating point numbers
      equal = isclose(float(expected_value), float(observed_value), rel_tol=1.5E-5 + 1E-15)
      numbers_or_words = 'numbers'
    except ValueError: # if values are strings
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

def check_length(line1_length, line2_length, message: str, err_type: str, one_color: str, err=True) -> str | None:
  """
  Documentation
  """
  if line1_length != line2_length:
    message = message.replace('%1%', f"{str(line1_length)}").replace('%2%', f"{str(line2_length)}")
    if line1_length > 1:
      message = message.replace("(s)", 's')
    else:
      message = message.replace("(s)", '')
    if err:
      raise InterruptedError([err_type, message, one_color])
    return message
  return None

def fill_checker(log, data, data_length, correct_or_wrong, to_color):
  """
  Documentation
  """
  aux = to_color.pop(0)
  err_num = 0
  for i in range(data_length):
    if aux[0] == i:
      err_num += 1
      log += f"<skyblue>{err_num}{'' if err_num >= 10 else ' '}</skyblue>|"
      values = data[i].split(" ")
      for j in range(len(values)):
        if aux[1] == j:
          try:
            aux = to_color.pop(0)
          except IndexError:
            pass
          log += f" <{correct_or_wrong}>{replace_non_xml_valid_characters(values[j])}</{correct_or_wrong}>"
        elif values[j] == "":
          log += " "
        else:
          log += f" {replace_non_xml_valid_characters(values[j])}"
    else:
      log += f" {'' if err_num >= 10 else ' '}| {replace_non_xml_valid_characters(data[i])}"
    log += f"{' ' * (55 - len(data[i]) - 2)}|\n"

  return log

def search_to_color(data, diff):
  """
  Documentation
  """
  to_color = []
  for values in data:
    if values[2] in diff:
      to_color.append((values[0], values[1]))
  return to_color

def compare(
  expected: list[str],
  observed: list[str],
  checker_log_list: list[str],
  test_sample_num: int,
  any_order: bool,
  check_presentation: bool,
  input_string: str,
  ignore_extra_spaces: bool,
  ignore_extra_newlines: bool
):
  """
  Documentation
  """
  if ignore_extra_newlines:
    remove_empty_lines(observed)
    remove_empty_lines(expected)

  #* Compare the results if the output is an integer or a string
  if expected == observed:
    fill_checker_log_normal_way(checker_log_list, test_sample_num, input_string, observed, expected)
    return True, None

  elif (le:=len(expected)) > 0 and (lo:=len(observed)) == 0:
    observed = ["(Empty)"]
    fill_checker_log_normal_way(checker_log_list, test_sample_num, input_string, observed, expected)
    return False, "\n  <wrong>Wrong answer</wrong>: No output was generated"

  if check_presentation:
    check_length(
      le,
      lo,
      "\n  <error_3>Presentation error</error_3>: <u>expected</u> %1% line(s), <u>found</u> %2%",
      "Presentation error",
      "error_3",
      True
    )
    accepted = True
    line_number = 1
    output_log = f" {separator}\n\nOutput\n   {separator}\n"
    expected_log = f"   {separator}\n\nAnswer\n   {separator}\n"
    wrong_answer_messages = ""
    if ignore_extra_spaces:
      func1 = lambda data: [value for value in data if value]
    else:
      func1 = lambda data: data

    for values in zip(expected, observed):
      err_num = 0
      space = (line_number < 10) * ' '
      aux = values[0].strip()
      aux2 = values[1].strip()
      len_val_exp = len(values[0])
      len_val_obs = len(values[1])
      expected_line = func1(aux.strip().split(' '))
      observed_line = func1(aux2.split(' '))
      stripped_spaces_num_exp = len_val_exp - len(aux)
      stripped_spaces_num_obs = len_val_obs - len(aux2)
      del aux, aux2

      observed_length = len(observed_line)
      expected_length = len(expected_line)
      wrong_answer_message = check_length(
        expected_length,
        observed_length,
        f"<error_3>Presentation error</error_3>: {line_number}{english_ending(line_number)} line, "
        "<u>expected</u> %1% value(s), <u>found</u> %2%",
        "Presentation error",
        "error_3",
        False
      )
      out_line = answer_line = ""
      extra_spaces_num = 0
      if wrong_answer_message is not None:
        accepted = False
        err_num += 1
        wrong_answer_messages += f"\n  {wrong_answer_message}"
        if observed_length > expected_length:
          out_line += f" {replace_non_xml_valid_characters(' '.join(observed_line[:expected_length]))} <blue>{replace_non_xml_valid_characters(' '.join(observed_line[expected_length:]))}</blue>"
          answer_line += f" {replace_non_xml_valid_characters(values[0])}"
        else:
          extra_spaces_num = (expected_length - observed_length) * 2
          out_line += f" {replace_non_xml_valid_characters(values[1])}{' <blue>?</blue>' * (expected_length - observed_length)}"
          answer_line += f" {replace_non_xml_valid_characters(values[0])}"
      else:
        if any_order and Counter(expected_line) == Counter(observed_line):
          out_line += f" {replace_non_xml_valid_characters(' '.join(observed_line))}"
          answer_line += f" {replace_non_xml_valid_characters(' '.join(expected_line))}"
          continue

        column_number = 1
        for column_value in zip(expected_line, observed_line):
          # column_value[0] is the exepected value and column_value[1] is the observed value
          equal, wrong_answer_message = compare_values(
            column_value[0],
            column_value[1],
            line_number,
            column_number
          )
          if not equal:
            err_num += 1
            out_line += f" <wrong>{replace_non_xml_valid_characters(column_value[1])}</wrong>"
            answer_line += f" <correct>{replace_non_xml_valid_characters(column_value[0])}</correct>"
            accepted = False
            wrong_answer_messages += f"\n  {wrong_answer_message}"
          else:
            out_line += f" {replace_non_xml_valid_characters(column_value[1])}"
            answer_line += f" {replace_non_xml_valid_characters(column_value[0])}"
          column_number += 1
          
      nr_spaces_exp = (55 - len(values[0]) - 2 + stripped_spaces_num_exp)
      if err_num > 0:
        expected_log += f"<skyblue>{line_number}</skyblue>{space}|{answer_line} {' ' * nr_spaces_exp}|\n"
        output_log += f"<skyblue>{line_number}</skyblue>{space}|{out_line} {' ' * (55 - len(values[1]) - 2 + stripped_spaces_num_obs - extra_spaces_num)}|\n"
      else:
        if conf_file['cfkit']['show_line_number'] == 'yes':
          output_log += f"{line_number}{space}|{out_line} {' ' * (55 - len(values[1]) - 2 + stripped_spaces_num_obs)}|\n"
          expected_log += f"{line_number}{space}|{answer_line} {' ' * nr_spaces_exp}|\n"
        else:
          expected_log += f"  |{answer_line} {' ' * nr_spaces_exp}|\n"
          output_log += f"  |{out_line} {' ' * (55 - len(values[1]) - 2 + stripped_spaces_num_obs)}|\n"

      line_number += 1

    if accepted:
      fill_checker_log_normal_way(checker_log_list, test_sample_num, input_string, observed, expected)
    else:
      checker_log_list[test_sample_num] = f"Input\n {separator}\n"
      fill_checker_log_list(checker_log_list, input_string, test_sample_num)
      checker_log_list[test_sample_num] += f"{output_log}{expected_log}   {separator}\nChecker log: "

  else:
    expected_trimmed_with_index, expected_trimmed = trim_data(expected[:])
    observed_trimmed_with_index, observed_trimmed = trim_data(observed[:])
    expected_length = len(expected_trimmed_with_index)
    observed_length = len(observed_trimmed_with_index)
    check_length(
      expected_length,
      observed_length,
      "  \n<wrong>Wrong answer</wrong>: <u>expected</u> %1% value(s), <u>found</u> %2%",
      "Wrong answer",
      "wrong",
      True
    )
    if any_order:
      expected_trimmed_counter = Counter(expected_trimmed)
      observed_trimmed_counter = Counter(observed_trimmed)

      if expected_trimmed_counter == observed_trimmed_counter:
        fill_checker_log_normal_way(checker_log_list, test_sample_num, input_string, observed, expected)
        return True, None

      accepted = False
      expected_trimmed_counter, observed_trimmed_counter = expected_trimmed_counter - observed_trimmed_counter, observed_trimmed_counter - expected_trimmed_counter
      to_color_in_answer = search_to_color(expected_trimmed_with_index, expected_trimmed_counter)
      to_color_in_output = search_to_color(observed_trimmed_with_index, observed_trimmed_counter)
      wrong_answer_messages = f"\n  <wrong>Wrong answer:</wrong> Expected values: '{replace_non_xml_valid_characters(' '.join(expected_trimmed_counter.elements()))}', found: '{' '.join(observed_trimmed_counter.elements())}'"

    else:
      column_num = 1
      accepted = True
      wrong_answer_messages = ""
      to_color_in_answer = []
      to_color_in_output = []
      for output in zip(expected_trimmed_with_index, observed_trimmed_with_index):
        # output[0] is the expected output and output[1] is the observed output
        equal, wrong_answer_message = compare_values(output[0][2], output[1][2], 0, column_num)
        if not equal:
          accepted = False
          wrong_answer_messages += f"\n  {wrong_answer_message}"
          to_color_in_answer.append((output[0][0], output[0][1]))
          to_color_in_output.append((output[1][0], output[1][1]))
        column_num += 1
    if not accepted:
      expected_log = fill_checker(f'   {separator}\n\nAnswer\n   {separator}\n', expected, le,  'correct', to_color_in_answer)
      output_log = fill_checker(f' {separator}\n\nOutput\n   {separator}\n', observed, lo, 'wrong', to_color_in_output)
      checker_log_list[test_sample_num] = f"Input\n {separator}\n"
      fill_checker_log_list(checker_log_list, input_string, test_sample_num)
      checker_log_list[test_sample_num] += f"{output_log}{expected_log}   {separator}\nChecker log: "
    else:
      fill_checker_log_normal_way(checker_log_list, test_sample_num, input_string, observed, expected)
  return accepted, wrong_answer_messages

def check_answer(
  expected: list[str],
  observed: list[str],
  checker_log_list: list[str] | list[list],
  test_sample_num: int,
  any_order: bool,
  multiple_answers: bool,
  check_presentation: bool,
  expected_str: str,
  input_string: str,
  ignore_extra_spaces: bool,
  ignore_extra_newlines: bool
) -> tuple[bool, str | bool, None]:
  """
  Documentation
  """

  if multiple_answers:
    accpeted = None
    expected_str = expected_str.split("\n# another answer\n")
    equal = False
    wrong_answer_messages = "<wrong>The output doesn't match any of the answers.</wrong>\n"
    for i in range(len(expected_str)):
      try:
        equal, wrong_answer_message = compare(
          expected_str[i].split("\n"),
          observed,
          checker_log_list,
          test_sample_num,
          any_order,
          check_presentation,
          input_string,
          ignore_extra_spaces,
          ignore_extra_newlines
        )
        wrong_answer_messages += (f"Answer {i + 1}: {wrong_answer_message}" + "\n") if not equal else ''
      except InterruptedError as err:
        wrong_answer_messages += f"Answer {i + 1}: {err.args[0][1]}" + "\n"
      finally:
        accpeted = accpeted or equal

    if not accpeted:
      return False, wrong_answer_messages
    return True, None
  try:
    return compare(
      expected,
      observed,
      checker_log_list,
      test_sample_num,
      any_order,
      check_presentation,
      input_string,
      ignore_extra_spaces,
      ignore_extra_newlines
    )
  except InterruptedError as err:
    fill_checker_log_normal_way(checker_log_list, test_sample_num, input_string, observed, expected)
    raise InterruptedError(*err.args)
