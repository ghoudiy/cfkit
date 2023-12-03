"""A simple command line application to interact with Codeforces."""

import argparse
import sys
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
  if len(sys.argv) <= 1:
    print(HELP_MESSAGE)
    sys.exit(1)
  if sys.argv[1] not in ALL_ACTIONS:
    print(HELP_MESSAGE)
    sys.exit(1)

  return sys.argv.pop(1)


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
      sys.exit(1)
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
        f"https://codeforces.com/contest/{contestid}/problems", contestid, contestid).text,
      contestid, None, True
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
      sys.exit(1)
    return f"{contestid}{problems[i+1][0][:problems[i+1][0].find('.')]}"
  if i == 1:
    print(f"{contestid}{problems[i][0][:problems[i][0].find('.')]} is the first problem in this contest.")
    sys.exit(1)
  return f"{contestid}{problems[i-1][0][:problems[i-1][0].find('.')]}"

def _get_problem_index():
  """
  Documentation
  """
  try:

    problem_index = sys.argv[1]
    if search(r"\d{1,4}[A-z]", problem_index):
      pass

    elif search(r"[A-z]\d{1,4}", problem_index):
      problem_index = problem_index[1:] + problem_index[0]

    elif problem_index.isalpha() and sys.argv[2].isdigit():
      problem_index = sys.argv[2] + problem_index

    elif problem_index.isdigit() and sys.argv[2].isalpha():
      problem_index = problem_index + sys.argv[2]

    elif problem_index in ("next", "previous") and sys.argv[2] == "problem":
      problem_index = _next_previous(problem_index, sys.argv[2])

    else:
      print("I need to write a message here to tell the user that he need to enter the problem code or the solution file")
      sys.exit(1)

  except IndexError:
    print(HELP_MESSAGE)
    sys.exit(1)

  return problem_index


def list_action():
  """
  Documentation
  """
  parser = argparse.ArgumentParser(description='Description')
  parser.add_argument("")
  if len(sys.argv) >= 2:
    print(Contest(sys.argv[1]).problems)
  elif len(sys.argv) < 2:
    print(HELP_MESSAGE)

def parse_action():
  """
  Documentation
  """
  if sys.argv[1].isdigit() and 1 <= int(sys.argv[1]) <= 9999:
    Contest(int(sys.argv[1])).parse()
  elif sys.argv[1] in ("next", "previous") and sys.argv[2] == "contest":
    Contest(_next_previous(sys.argv[1], "contest"))
  else:
    Problem(_get_problem_index()).parse()

def gen_action():
  """
  Documentation
  """
  Problem(_get_problem_index()).create_solution_file()


def run_action():
  """
  Documentation
  """
  Problem(_get_problem_index()).run_demo()

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
  # args =
  pass
