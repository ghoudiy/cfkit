"""A simple command line application to interact with Codeforces."""
import argparse
import sys
from re import search

from cfkit.contest import Contest
from cfkit.problem import Problem

ALL_ACTIONS = ("list", "parse", "gen", "test")
help_msg = """
Available commands:

    list    list all problems of the contest
    parse   parse input and output samples from problem statement
    gen     generate solution file with the default template if found
    test    test solution file against samples and print the verdict response

Type cf <command> --help for usage help on a specific command.
For example, cf test --help will list all testing options.
"""


def get_action():
  """Pop first argument, check it is a valid action."""
  if len(sys.argv) <= 1:
    print(help_msg)
    sys.exit(1)
  if not sys.argv[1] in ALL_ACTIONS:
    print(help_msg)
    sys.exit(1)

  return sys.argv.pop(1)


def get_problem_index():
  problem_index = sys.argv[1]
  if search(r"\d{1,4}[A-z]", problem_index):
    return problem_index
  
  elif search(r"[A-z]\d{1,4}", problem_index):
    problem_index = problem_index[1:] + problem_index[0]
  
  elif problem_index.isalpha() and sys.argv[2].isdigit():
    problem_index = sys.argv[2] + problem_index

  elif problem_index.isdigit() and sys.argv[2].isalpha():
    problem_index = problem_index + sys.argv[2]
  
  elif problem_index == "next":
    pass

  elif problem_index == "previous":
    pass

  return problem_index

def list_action():
  Contest(sys.argv[1]).problems_list()


def parse_action():
  Problem(get_problem_index()).parse()


def gen_action():
  Problem(get_problem_index()).create_problem_file()


def test_action():
  Problem(get_problem_index()).run_demo()

def main():

  actions = {
    "list"  : list_action,
    "parse"  : parse_action,
    "gen" : gen_action,
    "test"   : test_action,
  }
  actions[get_action()]()


if __name__ == "__main__":
  main()