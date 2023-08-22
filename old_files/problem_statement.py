import os
def problem_statement(self, saveInFile: bool = False, note: bool = True, examples: bool = True, time_limit: bool = True, memory_limit: bool = True, IO: bool = True) -> str:

  L = self._content[9:]
  # Printing the note and examples
  note_test = True
  if note:
    try:

      if examples:
        L[self.__pex-9] = "\n\nExamples"
        L[self.__pex-8] = "\nInput\n"
        L[L[self.__pex-8:].index("Output") + (self.__pex - 8)] = "\n\nOutput\n"
        L[self.__pn-9] = "\n\nNote\n"

      elif not examples:
        L[self.__pn-9] = "\n\nNote\n"
        L = L[:self.__pex-9] + L[self.__pn-9:]
    except TypeError:
      note_test = False
  
  elif not note and examples:
    try:
      L = self._content[9:self._content.index("Note")]
    except ValueError:
      L = self._content[9:]
  else:
    L = self._content[9:self.__pex]

  L[L.index("Input")] = "\n\nInput\n"
  L[L.index("Output")] = "\n\nOutput\n"
  L[0] = "\n" + L[0]
  if not note_test:
    L.append("\nNote section is not available")
  def tmp(x) -> None:
    if saveInFile:
      aux = 9
    else:
      aux = os.get_terminal_size().columns - 5
    if x != 0:
      return f"{(self._content[x] + ': ' + self._content[x+1]).center(aux - 9)}"
    else:
      return f"{self._content[x].center(aux - 9)}"

  R = []
  R.append(f"{tmp(0)}\n") # Problem Name
  if time_limit: R.append(f"{tmp(1)}\n")
  if memory_limit: R.append(f"{tmp(3)}\n")
  if IO: R.append(f"{tmp(5)}\n"); R.append(f"{tmp(7)}\n")

  if saveInFile:
    path = input("Path to save problem statement text in: ")
    if path == "":
      path = os.getcwd()
    else:
      contest._check_path_existence(path, 'd')
    with open(f"{path}{self.__slash}{self._code}.txt", 'w') as file:
      file.write(" ".join(" ".join(R + L).split("$$$")))
    return f"Problem statement saved in {path}{self.__slash}{self._code}.txt"
  else:
    print(*R)
    return " ".join(" ".join(L).split("$$$"))
