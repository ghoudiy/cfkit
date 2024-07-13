from cfkit.utils.parse_samples import problems_content
from cfkit.client.fetch import get_response
from time import sleep

from os import listdir

a = listdir("/home/ghoudiy/.cfkit/resources/problems")
for contestid in range(1, 1990):
  if f"{contestid}.txt" not in a:
    try:
      response, name = problems_content(
          get_response(
          f"https://codeforces.com/contest/{contestid}/problems",
          contestid,
          contestid
          ),
          contestid,
          html_page=True
      )
      print(f"contest id: {contestid}")
      print(f"contest name: {name = }")
      print("-" * 50)
      sleep(7)
    except InterruptedError as err:
      print(err)
      continue
