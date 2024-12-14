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
  # parser.add_argument("-c", "--code", action='store_true', dest="letters", help="Problem letters")
  parser.add_argument('-l', '--local', action='store', dest='local', help='Parse from html file')

  args = parser.parse_args()
  contest = Contest(args.contestid, args.local)
  max_width = max(len(name) for name in contest.problems_names) + 1
  print(f"{'Problem name':<{max_width}} {'Time Limit':<12} {'Memory Limit':<15} {'Input':<16} {'Output':<16}\n{'-' * 100}")
  for problem in contest._content:
    for i in range(1, 5):
      problem[i] = problem[i][problem[i].find(": ") + 2:]
    print(f"{problem[0]:<{max_width}} {problem[1]:<12} {problem[2]:<15} {problem[3]:<16} {problem[4]:<16}")

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
  parser.add_argument('-l', '--local', action='store', dest='local', help='Parse from html file')

  args = parser.parse_args()

  problem_index, contest_or_problem = _check_problem_index(args.problem_index)
  
  if contest_or_problem == "problem":
    Problem(problem_index, args.local).parse(args.path, args.create_tests_dir, args.short_names)
  else:
    Contest(int(problem_index), args.local).parse(args.path, args.create_tests_dir)

def gen_action():
  """
  Documentation
  """
  from cfkit.codeforces._contest import Contest
  from cfkit.codeforces._problem import Problem, retrieve_template, insert_placeholders_template, conf_file, colored_text, EXTENSIONS, LANGUAGES_EXTENSIONS

  parser = ArgumentParser(description='Generate options')

  parser.add_argument("code", action='store', help="Problem index (e.g. 4a) or file name (e.g. 4a.py)")
  parser.add_argument('-c', '--create', action='store_true', dest='create_contest_folder', help='Create contest folder')
  parser.add_argument('-e', '--ext', action='store', dest='ext', help='File extension')
  parser.add_argument('-n', '--name', action='store_true', dest='problem_name', help="Add problem name to file name")
  parser.add_argument('-p', '--path', action='store', dest='path', default=None, help='Path where file will be created')
  parser.add_argument('-l', '--local', action='store', dest='local', help='Parse from html file')

  args = parser.parse_args()

  if args.create_contest_folder is False and args.problem_name is False and args.code.isdigit() is False:
    if args.code.find(".") == -1:
      if args.ext is None:
        default_language = conf_file["cfkit"]["default_language"].strip()
        if default_language == "":
          print(
            "You should set a default language so that you don't have to",
            "enter the programming language every time"
          )
          args.ext = input("Extension: ")
          while args.ext not in EXTENSIONS:
            colored_text("Extension is not recognised! Please try again", one_color="error_4")
            args.ext = input("Extension: ")
        else:
          args.ext = LANGUAGES_EXTENSIONS[default_language][0]
      args.code += f".{args.ext}"

    with open(args.code, 'w') as file:
      with open(retrieve_template(args.code), 'r', encoding="UTF-8") as ff:
        file.write(insert_placeholders_template(ff.read()))
        sysExit(0)

  problem_index, contest_problem = _check_problem_index(args.code)

  if contest_problem == "problem":
    Problem(problem_index, args.local).create_solution_file(args.path, args.ext, args.create_contest_folder, args.problem_name)
  else:
    Contest(problem_index, args.local).create_problems_files(args.path, args.ext, args.problem_name, args.create_contest_folder)

def run_action():
  """
  Documentation
  """
  from cfkit.codeforces._problem import Problem
  from cfkit._utils.variables import conf_file

  parser = ArgumentParser(description='Run options')

  parser.add_argument("file", action='store', help="Solution file")
  parser.add_argument("-p", "--problem", action='store', dest="problem_code", help="Problem code")
  parser.add_argument("-o", "--order", action='store_true', dest="order", help="Any order")
  parser.add_argument("-c", "--custom", action='store_true', dest="custom", help="Run custom samples only")
  parser.add_argument('-r', '--remove', action='store_true', dest='remove', help='Remove samples and output files')
  parser.add_argument('-m', '--multiple-answers', action='store_true', dest='multiple_answers', help='There are multiple correct answers')
  parser.add_argument('-s', '--space', action='store_false', dest='ignore_extra_spaces', help='Does not ignore extra spaces')
  parser.add_argument('-n', '--newline', action='store_false', dest='ignore_extra_newlines', help='Does not ignore extra new lines')
  parser.add_argument('-v', '--verbose-off', action='store_false', dest='not_verbose', help='Does not print input, output and answer')
  parser.add_argument('-a', '--no-answers', action='store_false', dest='print_answers', help='Does not print answers')
  parser.add_argument('-l', '--local', action='store', dest='local', help='Parse from html file')

  args = parser.parse_args()

  if args.problem_code is None:
    Problem(args.file, args.local).run_demo(
      args.file,
      args.order,
      args.multiple_answers,
      conf_file["cfkit"]["always_check_presentation"].lower() == "yes",
      args.custom,
      args.print_answers,
      args.remove,
      None,
      args.not_verbose,
      args.ignore_extra_spaces,
      args.ignore_extra_newlines
    )
  else:
    Problem(args.problem_code, args.local).run_demo(
      args.file,
      args.order,
      args.multiple_answers,
      conf_file["cfkit"]["always_check_presentation"].lower() == "yes",
      args.custom,
      args.print_answers,
      args.remove,
      None,
      args.not_verbose,
      args.ignore_extra_spaces,
      args.ignore_extra_newlines
    )

def config_action():
  """
  Documentation
  """
  from pathlib import Path
  from shutil import copy
  from platform import uname
  from subprocess import run
  var = uname()
  arch = var.machine.lower()
  operating_sys = var.system.lower()
  if argv[1] == "edit":
    try:
      if operating_sys == "windows":
        run(f"notepad \"{Path.home().joinpath('.cfkit', 'cfkit.conf')}\"", shell=True)  # macOS
      elif operating_sys == "darwin":
        run(f"open \"{Path.home().joinpath('.cfkit', 'cfkit.conf')}\"", shell=True)  # macOS
      else:
        run(f"xdg-open \"{Path.home().joinpath('.cfkit', 'cfkit.conf')}\"", shell=True)  # Linux
    except Exception as e:
      print(f"An error occurred: {e}")
      sysExit(1)

  elif argv[1] == "all":
    source_dir = Path(__file__).parent.parent

    data_dir = source_dir.joinpath("_data")
    target_dir = Path.home() / '.cfkit'

    if not target_dir.exists():
      target_dir.mkdir(parents=True)

    print("Starting to copy important files...")
    for item in data_dir.rglob('*'):
      target_item = target_dir / item.relative_to(data_dir)
      if item.name != "__pycache__":
        if item.is_dir():
          target_item.mkdir(parents=True, exist_ok=True)
        elif not item.name.endswith(".pyc"):
          copy(item, target_item)
    print("All important files have been successfully copied.")

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

    def configure_mem_time_usage(mem_time_calc_exec):
      conf_file["cfkit"]["calculate_memory_usage_and_execution_time"] = "yes" if confirm(
        "Do you want to calculate memory usage and execution time?"
      ) else "no"
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

    elif arch in ('aarch64', 'arm64'):
      configure_mem_time_usage(f"{operating_sys}_arm64.exe")

    elif arch.startswith('arm'):
      if operating_sys != "linux":
        print("Unfortunately, memory and time tracking features are not supported on your current system configuration.")
      else:
        configure_mem_time_usage(f"{operating_sys}_arm.exe")

    else:
      print("Unfortunately, memory and time tracking features are not supported on your current system configuration.")

    with open(config_file_path, 'w', encoding="UTF-8") as file:
      conf_file.write(file)

  else:
    print("There are only two options: `cf config all`, `cf config edit`")
    sysExit(1)

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
