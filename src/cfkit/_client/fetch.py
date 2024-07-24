"""
Documentation
"""

from requests import get, exceptions as requestsExceptions

from cfkit._utils.print import colored_text
from cfkit._utils.check import check_status
from cfkit._utils.file_operations import write_json_file
from cfkit._utils.variables import config_folder


def get_url_with_timeout(url: str, seconds: float = 15):
  """
  Send HTTP request to url with timeout
  """
  try:
    return get(url, timeout=seconds)
  except requestsExceptions.Timeout:
    colored_text(
      "Unable to fetch data from Codeforces server. "
      "This may be due to one of the following reasons:\n"
      "   • The server is currently <bright_text>experiencing a high volume of requests.</bright_text>\n"
      "   • The server is <bright_text>temporarily down or unreachable.</bright_text>\n"
      "Please try again later or check the status of the Codeforces server.\n",
      exit_code_after_print_statement=5
    )


def get_response(url: str, code, contest_id: int = 0) -> str:
  """
  Documentation
  """
  response = get_url_with_timeout(url)
  check_status(response)
  html_source_code = response.text

  problems = html_source_code.find('<div class="problem-statement">') != -1
  contest_started = html_source_code.find(
    '<div class="contest-state-phase">'
    'Before the contest</div>'
  ) == -1

  if not problems:
    # Check if the contest is not public
    if html_source_code.find('Fill in the form to login into Codeforces.') != -1:
      colored_text(
        f"<error_5>You are not allowed to participate in this contest</error_5> "
        f"&apos;{contest_id}&apos;",
        exit_code_after_print_statement=403
      )
    else:
      colored_text(
        f"<error_4>No such contest</error_4> &apos;{code}&apos;",
        exit_code_after_print_statement=4
      )

  elif not contest_started:
    colored_text(
      "Contest has not started yet",
      one_color="error_5",
      exit_code_after_print_statement=5
    )
    raise InterruptedError

  return html_source_code

def download_contests_json_file() -> None:
  """
  Documentation
  """
  contests_json_file = config_folder.joinpath("resources", "contests.json")
  if not contests_json_file.exists():
    response = get_url_with_timeout("https://codeforces.com/api/contest.list")
    check_status(response)
    contest_list = response.json()
    contest_list: list[dict] = sorted(contest_list["result"], key=lambda x: x["id"], reverse=True)

    contests = {}
    for contest in contest_list:
      contest.pop("relativeTimeSeconds")
      contest_id = contest.pop("id")
      contests[contest_id] = dict(contest.items())

    response = get_url_with_timeout("https://codeforces.com/api/problemset.problems")
    check_status(response)
    problem_list = response.json()
    problem_list: list[dict] = sorted(
      problem_list["result"]["problems"], key=lambda x: x["contestId"], reverse=True
    )
    problems = {}
    for problem in problem_list:
      contest_id = problem.pop("contestId")
      problem_index = {problem.pop("index"): dict(problem.items())}
      if problems.get(contest_id) is None:
        problems[contest_id] = {}
        problems[contest_id].update(problem_index)
      else:
        problems[contest_id].update(problem_index)
    write_json_file(contests, contests_json_file, 2)
    write_json_file(problems, config_folder.joinpath("resources", "problems.json"), 2)
