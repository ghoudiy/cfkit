"""
Documentation
"""

# from inspect import currentframe
# from json import dump#, load
from getpass import getpass
from datetime import datetime, timedelta
from requests.utils import dict_from_cookiejar
from requests.cookies import RequestsCookieJar
from mechanicalsoup import StatefulBrowser

from cfkit._utils.file_operations import write_json_file
from cfkit._utils.variables import resources_folder


def login() -> tuple[str, RequestsCookieJar]:
  """
  Documentation
  """
  def valid_username(username: str):
    username_length = len(username)
    is_alnum = username.isalnum()
    bounds = 3 <= username_length <= 24
    if bounds:
      if is_alnum:
        return True

      i = 0
      test = True
      while test and i < username_length:
        test = username[i].isalnum() or username[i] in ("_", "-")
        i += 1
      return test
    return False

  browser = StatefulBrowser()
  session_path = resources_folder.joinpath("session.json")

  browser.open('https://codeforces.com/enter')
  form = browser.select_form('form[id="enterForm"]')

  username = input("Username: ")
  while not valid_username(username):
    username = input("Please type your username correctly.\nUsername: ")

  password = getpass()
  while len(password) < 5:
    password = getpass("Please type your password correctly.\nPassword: ")

  form.set("handleOrEmail", username)
  form.set("password", password)
  form.set('remember', True)

  browser.submit_selected()

  # Convert cookies to a dictionary
  cookie_dict = dict_from_cookiejar(browser.session.cookies)
  # Save the cookies to a JSON file
  session = {
    "cookies": cookie_dict,
    "cookies_expiration_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
    "username": username,
  }
  write_json_file(session, session_path)
  return username, cookie_dict
