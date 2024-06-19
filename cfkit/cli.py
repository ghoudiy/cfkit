"""A simple command line application to interact with Codeforces."""

from argparse import ArgumentParser
from sys import exit as sysExit, argv
from re import search

from cfkit.util.common import (
  read_json_file,
  problems_content,
  get_response
)
from cfkit.contest import Contest
from cfkit.problem import Problem
from cfkit.util.variables import resources_folder
from cfkit.util.constants import HELP_MESSAGE
from cfkit.util.constants import ALL_ACTIONS


def get_action():
  """Pop first argument, check it is a valid action."""
  if len(argv) <= 1:
    print(HELP_MESSAGE)
    sysExit(1)
  if argv[1] not in ALL_ACTIONS:
    print(HELP_MESSAGE)
    sysExit(1)

  return argv.pop(1)


def _next_previous(next_or_previous, contest_or_problem):
  """
  Documentation
  """
  last_fetched = read_json_file(resources_folder.joinpath("last_fetched_data.json"))
  if contest_or_problem == "contest":
    contest_id = int(last_fetched["last_fetched_contest"]["contest_id"])
    if next_or_previous == "next":
      return contest_id + 1
    if contest_id == 1:
      print("There were no contests before contest 1.")
      sysExit(1)
    return contest_id - 1

  problem_index = last_fetched["last_fetched_problem"]["problem_index"]
  pos_letter = len(problem_index) - 1 if problem_index[-1].isalpha() else len(problem_index) - 2
  contestid = int(problem_index[:pos_letter])
  contest_problems_statement_file_path = resources_folder.joinpath(
    "problems",
    f"{contestid}").with_suffix(".txt")
  if not contest_problems_statement_file_path.exists():
    problems, _ = problems_content(
      get_response(
        f"https://codeforces.com/contest/{contestid}/problems", contestid, contestid),
      contestid, html_page=True
    )
  else:
    problems, _ = problems_content(contest_problems_statement_file_path, contestid)

  i = -1
  test = False
  while not test and i < len(problems) - 1:
    i += 1
    test = problems[i][0].startswith(problem_index[pos_letter:])

  if next_or_previous == "next":
    if i == len(problems):
      print(f"{contestid}{problems[i][0][:problems[i][0].find('.')]} is the last problem in this contest.")
      sysExit(1)
    return f"{contestid}{problems[i+1][0][:problems[i+1][0].find('.')]}"
  if i == 1:
    print(f"{contestid}{problems[i][0][:problems[i][0].find('.')]} is the first problem in this contest.")
    sysExit(1)
  return f"{contestid}{problems[i-1][0][:problems[i-1][0].find('.')]}"


def _check_problem_index(problem_index):
  """
  Documentation
  """
  if problem_index.isdigit() and 1 <= int(problem_index) <= 9999:
    return problem_index, "contest"
  try:

    # if ((i:=search(r"\A\d{1,4}[A-z](\d)?", problem_index)) is not None) or ((j:=search(r"\A[A-z]{1}(\d)?", problem_index)) is not None):
    if ((search(r"\A\d{1,4}[A-z](\d)?", problem_index)) is not None) or ((search(r"\A[A-z]{1}(\d)?", problem_index)) is not None):
      pass

    elif aux := search(r"\A(\d?[A-z])(\d{2,4})", problem_index):
      aux = aux.groups()
      problem_index = (aux[1] + aux[0][::-1], problem_index)

    elif problem_index.isalpha() and argv[2].isdigit():
      problem_index = argv[2] + problem_index

    elif problem_index.isdigit() and argv[2].isalpha():
      problem_index = problem_index + argv[2]

    # elif problem_index in ("next", "previous") and argv[2] == "problem":
    #   problem_index = _next_previous(problem_index, argv[2])

    else:
      print("I need to write a message here to tell the user that he need to enter the problem code or the solution file")
      sysExit(1)

  except IndexError:
    print(HELP_MESSAGE)
    sysExit(1)

  return problem_index, "problem"


def list_action():
  """
  Documentation
  """
  if len(argv) >= 2:
    print(Contest(argv[1]).problems)
  elif len(argv) < 2:
    print(HELP_MESSAGE)


def parse_action():
  """
  Documentation
  """
  parser = ArgumentParser(description='Parse options')

  parser.add_argument("problem_index", action='store', help="Problem index (e.g. 4a)")
  parser.add_argument('-c', '--create', action='store_true', dest='create_tests_dir', help='Create tests directory')
  parser.add_argument('-p', '--path', action='store', dest='path', default=None, help='Path where samples will be created')
  parser.add_argument('-s', '--short', action='store_true', dest='short_names', help="Name samples 'in' and 'out'")
  
  args = parser.parse_args()

  problem_index, contest_problem = _check_problem_index(args.problem_index)
  path_option = args.path
  create_tests_dir_option = args.create_tests_dir
  path_option = args.path
  short_names_option = args.short_names

  if contest_problem == "problem":
    Problem(problem_index).parse(path_option, create_tests_dir_option, short_names_option)
  else:
    Contest(int(problem_index)).parse(path_option, create_tests_dir_option)
  # elif problem_index in ("next", "previous") and argv[2] == "contest":
  #   Contest(_next_previous(problem_index, "contest")).parse(path_option, create_tests_dir_option)


def gen_action():
  """
  Documentation
  """
  parser = ArgumentParser(description='Generate options')

  parser.add_argument("problem_index", action='store', help="Problem index (e.g. 4a)")
  parser.add_argument('-c', '--create', action='store_true', dest='create_contest_folder', help='Create contest folder')
  parser.add_argument('-e', '--ext', action='store', dest='ext', help='File extension')
  parser.add_argument('-n', '--name', action='store_true', dest='problem_name', help="Add problem name to file name")
  parser.add_argument('-p', '--path', action='store', dest='path', default=None, help='Path where file will be created')

  args = parser.parse_args()

  problem_index, contest_problem = _check_problem_index(args.problem_index)
  ext = args.ext
  create_contest_folder = args.create_contest_folder
  problem_name = args.problem_name
  path = args.path

  if contest_problem == "problem":
    Problem(problem_index).create_solution_file(ext, create_contest_folder, problem_name, path)
  else:
    Contest(problem_index).create_problems_files(ext, problem_name, path)

def run_action():
  """
  Documentation
  """
  parser = ArgumentParser(description='Run options')

  parser.add_argument("file", action='store', help="Solution file")
  parser.add_argument("-c", action='store', dest="problem_code", help="Problem code")
  parser.add_argument('-f', '--format', action='store_true', dest='formatting', help='Check formatting')
  parser.add_argument('-r', '--remove', action='store_true', dest='remove', help='Remove samples and output files')
  parser.add_argument('-nv', '--notVerbose', action='store_false', dest='not_verbose', help='Do not print input, output and answer')

  args = parser.parse_args()

  file, _ = _check_problem_index(args.file)
  problem_code = args.problem_code
  check_output_formatting = args.formatting
  remove_test_samples = args.remove
  not_verbose = args.not_verbose

  if problem_code is None:
    Problem(file).run_demo(file, check_output_formatting, False, remove_test_samples, not_verbose)
  else:
    Problem(problem_code).run_demo(file, check_output_formatting, False, remove_test_samples, not_verbose)


def main():
  """
  Documentation
  """
  actions = {
    "list"  : list_action,
    "parse" : parse_action,
    "gen"   : gen_action,
    "run"   : run_action,
  }
  actions[get_action()]()


if __name__ == "__main__":
  pass
