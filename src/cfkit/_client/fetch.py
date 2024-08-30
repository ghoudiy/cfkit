"""
Documentation
"""

from requests import get, exceptions as requestsExceptions

from cfkit._utils.print import colored_text


def get_response_text(url: str, seconds: float = 15) -> str:
  """
  Send HTTP request to url with timeout
  """
  try:
    response = get(f"https://mirror.{url}", timeout=seconds)
    try:
      response.raise_for_status()
    except requestsExceptions.HTTPError as err:
      raise requestsExceptions.Timeout
    else:
      return response.text

  except requestsExceptions.Timeout:
    try:
      return get(f"https://{url}").text
    except:
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
  html_source_code = get_response_text(url)

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
