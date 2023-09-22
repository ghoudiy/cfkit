"""A simple command line application to interact with Codeforces."""
import argparse
import sys
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


def list_action():
  Contest(sys.argv[1]).problems_list()


def parse_action():
  Problem(sys.argv[1]).parse()


def gen_action():
  Problem(sys.argv[1]).create_problem_file()


def test_action():
  Problem(sys.argv[1]).run_demo()

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