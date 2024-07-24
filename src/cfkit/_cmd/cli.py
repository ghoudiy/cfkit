"""A simple command line application to interact with Codeforces."""

from argparse import ArgumentParser
from sys import exit as sysExit, argv
from re import search

from cfkit._utils.constants import LANGUAGES, HELP_MESSAGE, ALL_ACTIONS


def get_action():
  """Pop first argument, check it is a valid action."""
  if len(argv) <= 1:
    print(HELP_MESSAGE)
    sysExit(1)
  if argv[1] not in ALL_ACTIONS:
    print(HELP_MESSAGE)
    sysExit(1)

  return argv.pop(1)

def _check_problem_index(problem_index):
  """
  Documentation
  """
  from cfkit._utils.print import colored_text

  if problem_index.isdigit() and 1 <= int(problem_index) <= 9999:
    return problem_index, "contest"
  try:

    if ((search(r"\A\d{1,4}[A-z]\d{,2}", problem_index)) is not None) or ((search(r"\A[A-z]{1}\d{,2}", problem_index)) is not None):
      pass

    elif aux := search(r"\A(\d{,2}[A-z])(\d{2,4})", problem_index):
      aux = aux.groups()
      problem_index = aux[1] + aux[0][::-1]

    else:
      colored_text(
        "Please provide either the problem code or the solution file",
        one_color="error_4",
        exit_code_after_print_statement=4
      )
      sysExit(1)

  except IndexError:
    print(HELP_MESSAGE)
    sysExit(1)

  return problem_index, "problem"

def list_action():
  """
  Documentation
  """
  from cfkit.codeforces._contest import Contest

  parser = ArgumentParser(description='list options')

  parser.add_argument("contestid", action='store', help="ContestId")
  parser.add_argument("-l", "--letters", action='store_true', dest="letters", help="Problem letters")

  args = parser.parse_args()
  if args.letters:
    print(*Contest(args.contestid).problems_letters, sep="\n")
  else:
    print(*Contest(args.contestid).problems, sep="\n")

def parse_action():
  """
  Documentation
  """
  from cfkit.codeforces._contest import Contest
  from cfkit.codeforces._problem import Problem

  parser = ArgumentParser(description='Parse options')

  parser.add_argument("problem_index", action='store', help="Problem index (e.g. 4a)")
  parser.add_argument('-c', '--create', action='store_true', dest='create_tests_dir', help='Create tests directory')
  parser.add_argument('-p', '--path', action='store', dest='path', default=None, help='Path where samples will be created')
  parser.add_argument('-s', '--short', action='store_true', dest='short_names', help="Names samples as 'in' and 'out' (Works only when parsing a problem)")

  args = parser.parse_args()

  problem_index, contest_or_problem = _check_problem_index(args.problem_index)
  path_option = args.path
  create_tests_dir_option = args.create_tests_dir
  path_option = args.path
  short_names_option = args.short_names

  if contest_or_problem == "problem":
    Problem(problem_index).parse(path_option, create_tests_dir_option, short_names_option)
  else:
    Contest(int(problem_index)).parse(path_option, create_tests_dir_option)

def gen_action():
  """
  Documentation
  """
  from cfkit.codeforces._contest import Contest
  from cfkit.codeforces._problem import Problem

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
    Problem(problem_index).create_solution_file(path, ext, create_contest_folder, problem_name)
  else:
    Contest(problem_index).create_problems_files(path, ext, problem_name)

def run_action():
  """
  Documentation
  """
  from cfkit.codeforces._problem import Problem

  parser = ArgumentParser(description='Run options')

  parser.add_argument("file", action='store', help="Solution file")
  parser.add_argument("-p", "--problem", action='store', dest="problem_code", help="Problem code")
  parser.add_argument("-o", "--order", action='store_true', dest="order", help="Any order")
  parser.add_argument("-c", "--custom", action='store_true', dest="custom", help="Run custom samples only")
  parser.add_argument('-f', '--format', action='store_true', dest='formatting', help='Check formatting')
  parser.add_argument('-r', '--remove', action='store_true', dest='remove', help='Remove samples and output files')
  parser.add_argument('-nv', '--notVerbose', action='store_false', dest='not_verbose', help='Do not print input, output and answer')
  parser.add_argument('-m', '--multiple-answers', action='store_true', dest='multiple_answers', help='There are multiple correct answers')
  parser.add_argument('-a', '--no-answers', action='store_false', dest='print_answers', help='Do not print answers')

  args = parser.parse_args()

  if args.problem_code is None:
    Problem(args.file).run_demo(
      args.file,
      args.order,
      args.multiple_answers,
      args.formatting,
      args.custom,
      args.print_answers,
      args.remove,
      None,
      args.not_verbose
    )
  else:
    Problem(args.problem_code).run_demo(
      args.file,
      args.order,
      args.multiple_answers,
      args.formatting,
      args.custom,
      args.print_answers,
      args.remove,
      None,
      args.not_verbose
    )

def config_action():
  """
  Documentation
  """
  from pathlib import Path
  from shutil import copy
  from platform import uname
  if argv[1] != "all":
    print("Please run `cf config all`")
    sysExit(1)
  else:
    source_dir = Path(__file__).parent.parent

    data_dir = source_dir.joinpath("_data")
    target_dir = Path.home() / '.cfkit'

    if not target_dir.exists():
      target_dir.mkdir(parents=True)

    for item in data_dir.rglob('*'):
      target_item = target_dir / item.relative_to(data_dir)
      if item.name != "__pycache__":
        if item.is_dir():
          target_item.mkdir(parents=True, exist_ok=True)
        elif not item.name.endswith(".pyc"):
          copy(item, target_item)

    from cfkit._utils.print import colored_text
    from cfkit._utils.input import confirm, select_option
    from cfkit._config.config import set_language_attributes#, set_default_submission_language
    from cfkit._utils.variables import conf_file, config_file_path

    conf_file["cfkit"]["user"] = input("Your username: ")
    if len(conf_file["cfkit"]["user"]) == 0:
      colored_text("Username cannot be empty", one_color="error_4", exit_code_after_print_statement=4)
      conf_file["cfkit"]["default_language"] = select_option(
        "Please select the default programming language you will use to solve problems: ",
        LANGUAGES,
        index=False,
        disp_horizontally=False
    )
    conf_file["cfkit"]["default_language"] = select_option(
      "Please select the default programming language you will use to solve problems: ",
      LANGUAGES,
      index=False,
      disp_horizontally=False
    )

    set_language_attributes(conf_file["cfkit"]["default_language"])

    var = uname()
    arch = var.machine.lower()
    operating_sys = var.system.lower()

    def configure_mem_time_usage(mem_time_calc_exec):
      conf_file["cfkit"]["calculate_memory_usage_and_execution_time"] = str(confirm(
        "Do you want to calculate memory usage and execution time?"
      ))
      dst = source_dir.joinpath("_dependencies", "memory_time_usage.exe")
      if operating_sys != "windows":
        mem_time_calc_exec = mem_time_calc_exec[:-4]
        dst = source_dir.joinpath("_dependencies", "memory_time_usage")

      mem_time_calc_exec = source_dir.joinpath("_dependencies", f"memory_time_usage_{mem_time_calc_exec}")
      copy(mem_time_calc_exec, dst)

    if arch in ('i386', 'i686'):
      if operating_sys == "darwin":
        print("Unfortunately, memory and time tracking features are not supported on your current system configuration.")
      else:
        configure_mem_time_usage(f"{operating_sys}_386.exe")

    elif arch in ('x86_64', "amd64"):
      configure_mem_time_usage(f"{operating_sys}_amd64.exe")

    elif arch.startswith('arm'):
      if operating_sys != "linux":
        print("Unfortunately, memory and time tracking features are not supported on your current system configuration.")
      else:
        configure_mem_time_usage(f"{operating_sys}_arm.exe")

    elif arch in ('aarch64', 'arm64'):
      configure_mem_time_usage(f"{operating_sys}_arm64.exe")

    else:
      print("Unfortunately, memory and time tracking features are not supported on your current system configuration.")

    with open(config_file_path, 'w', encoding="UTF-8") as file:
      conf_file.write(file)

def main():
  """
  Documentation
  """
  actions = {
    "list"   : list_action,
    "parse"  : parse_action,
    "gen"    : gen_action,
    "run"    : run_action,
    "config" : config_action,
  }
  actions[get_action()]()
