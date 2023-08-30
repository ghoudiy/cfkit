from .util.util import *
from typing import TypeAlias
Directory: TypeAlias = str


class contest:
  def __init__(self, contestId: int) -> None:
    self._id = contestId
    check_contest_id(contestId)
    self._content = self.__content_contest()
  

  def __content_contest(self):
    response = get(f"https://codeforces.com/contest/{self._id}")
    response.raise_for_status()
    s = response.text
    s = s[s.find('<td class="id">') + 16:]
    return s[:s.find('</table>')].split("\n")


  def create_problems_files(self, ext: str, path: Directory = None, addProblemNameToFileName: bool = False):
    if path == None: path = os.getcwd()
    else: check_path_existence(path, 'd')
    os.chdir(path)
    S = set()
    N = []
    ok = 0
    for line in self._content:
      p = line.find('<a href="/contest/')
      p1 = line.find('!--')
      p2 = line.find("    -->")
      if p != -1 and p1 == -1 and line.find('<img src="') == -1:
        S.add(line[p+19:])
      if ok % 2 == 1:
        name = f"<!-- {line[p2+4:]} -->"
        name = BeautifulSoup(name, "html.parser").stripped_strings
        N.append(next(name))
        ok += 1
      if p1 != -1 and p2 == -1:
        ok += 1
    
    if os.path.basename(path) != self._id:
      os.mkdir(f"{self._id}")
    os.chdir(f"{self._id}")
    S = sorted(S)
    for i, code in enumerate(S):
      letter = code[code.find('/problem/')+9:code.find('"')]
      if addProblemNameToFileName:
        aux = file_name(self, N[i], f"{letter}_") + f".{ext}"
      else:
        aux = letter
      # if ext == "py":
      #   with open(aux, 'a') as file:
      #     with open(os.path.join(os.path.dirname(__file__), "templates", ""), f"{os.path.dirname(__file__)}{}python_template.py", 'r') as ff:
      #       file.write(ff.read())
      # else: open(aux, 'x').close()
