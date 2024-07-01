"""
Documentation
"""
from datetime import datetime
from requests.utils import cookiejar_from_dict
from mechanicalsoup import StatefulBrowser

from cfkit.client.login import login
from cfkit.utils.common import read_json_file
from cfkit.utils.print import colored_text
from cfkit.config.config import set_default_compiler
from cfkit.utils.variables import resources_folder
from cfkit.utils.constants import EXTENSIONS

def submit(contest_id, problem_code, file_path):
  """
  Documentation
  """
  browser = StatefulBrowser()

  session_path = resources_folder.joinpath("session.json")

  if not session_path.exists():
    username, cookies = login()

  else:
    session = read_json_file(session_path)
    if session["cookies_expiration_date"] == datetime.now().strftime("%Y-%m-%d"):
      print("The session is expired. Please log in again.")
      username, cookies = login()
    else:
      print("Hello from file")
      username = session["username"]
      # Convert the dictionary back to a CookieJar
      cookies = cookiejar_from_dict(session["cookies"])

    # Set the loaded cookies in browser
    browser.set_cookiejar(cookies)

  browser.open('https://codeforces.com/profile')
  if f'<a href="/profile/{username}">{username}</a>' in list(map(str, browser.links()[:30])):
    print(f"Welcome, {username}!")

  else:
    colored_text(
      "Login failed. Please check your credentials.",
      one_color="error_4",
      exit_code_after_print_statement=1
    )

  browser.open(f'https://codeforces.com/contest/{contest_id}/submit')
  form = browser.select_form('form[class="submit-form"]')

  # Fill out the form fields
  form.set("submittedProblemIndex", problem_code)
  form.set(
    "programTypeId",
    set_default_compiler(False, EXTENSIONS[file_path[file_path.rfind(".") + 1:]])
  )
  # Add the source file for submission
  with open(file_path, "rb") as file:
    form.set("sourceFile", file.read())

  # Submit the form
  browser.submit_selected()

  # def check_verdict():
  #   response = browser.get_current_page()
  #   # See where the site goes to after submitting the solution
  #   # Check show unofficial checkbox


if __name__ == "__main__":
  submit(
    '4',
    "A",
    "/home/ghoudiy/Documents/Programming/Python/CP/Codeforces/A_Problems/"
    "144A_Arrival_of_the_General.py"
  )
