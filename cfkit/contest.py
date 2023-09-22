"""
Documentation
"""
import sys
import os
from typing import TypeAlias
from requests import get

from cfkit.util.util import (
  check_url,
  check_status,
  check_path_existence,
  file_name,
  colored_text,
  create_file_folder,
  folder_file_exists,
  retrieve_template,
  # display_horizontally,
  # enter_number,
  read_text_from_file,
  wrong_answer_verdict,
  is_number,
  yes_or_no,
  conf_file,
  config_folder,
  # template_folder,
  language_conf,
  extensions
)
from cfkit.problem import Problem

Directory: TypeAlias = str


class Contest:
  """
  Documentation
  """
  def __init__(self, contest_id: int) -> None:
    self._id = contest_id
    self._content = self.__contest_content()

  def __contest_content(self):
    if isinstance(self._id, str) and self._id.isdigit():
      self._id = int(self._id)

    if isinstance(self._id, int):
      # API json
      # response = check_url(f"https://codeforces.com/contest/{self._id}", self._id)
      with open("response.html", 'r', encoding="UTF-8") as file:
        return file.read()
      # return response

    colored_text("Contest ID must be an integer", "error_5")
    sys.exit(1)

  def __list_problems(self, list_of_problems = None, func = None) -> (list | None):
    if list_of_problems is None:
      # Debugging
      # list_of_problems = self._content[self._content.find('">Choose problem</option>') + 25:
      #                                      self._content.find("</select>")].split("\r")[1:-1]
      list_of_problems = self._content[self._content.find('">Choose problem</option>') + 25:
                                        self._content.find("</select>")].split("\n")[1:-1]

    def fetch_problems(func):
      for i, line in enumerate(list_of_problems):
        problem_index = line[line.find('<option value="')+15:][0]
        problem_name = line[line.find(" - ")+3:line.find("</option>")]
        print(f"Problem {i+1}: {problem_index}. {problem_name}")
        func(problem_index, problem_name, i)

    if func is None:
      contest_problems_indexes = []
      fetch_problems(lambda problem_index, __, ___: contest_problems_indexes.append(problem_index))
      return contest_problems_indexes
    fetch_problems(func)

  def create_problems_files(
      self,
      programming_language_extension: str | list | None = None,
      add_problem_name_to_file_name: bool = False,
      path: Directory = os.getcwd()
    ) -> None:
    """
    Documentation
    """

    if path != os.getcwd():
      check_path_existence(path, 'd')
    os.chdir(path)
    if os.path.basename(path) != str(self._id):
      folder_name = create_file_folder(str(self._id), 'd')
    os.chdir(folder_name)
    # Debugging
    # problems_list = self._content[self._content.find('">Choose problem</option>'
    #                               ) + 25:self._content.find("</select>")].split("\r")[1:-1]
    problems_list = self._content[self._content.find('">Choose problem</option>'
                                  ) + 25:self._content.find("</select>")].split("\n")[1:-1]
    problems_num = len(problems_list)

    def enter_extensions() -> (list, int):
      for lang in language_conf:
        print(lang + ":", *language_conf[lang]["extensions"])
      programming_language_extension = input("Extension(s): ").strip().split()
      problems_extensions_length = len(programming_language_extension)

      while problems_extensions_length > problems_num:
        print(f"expected at most {problems_num} extensions, got {problems_extensions_length}.")
        programming_language_extension = input("Extensions: ").strip().split()
        problems_extensions_length = len(programming_language_extension)

      if len(programming_language_extension) == 1:
        colored_text(
          "To avoid entering extension every time\n"
          "run <command>'cf config'</> command to configure your default programming language"
        )
      return programming_language_extension, problems_extensions_length

    if isinstance(programming_language_extension, list):
      i = 0
      undefined_extension = False
      while not undefined_extension and i < len(programming_language_extension):
        if extensions.get(programming_language_extension[i]) is None:
          undefined_extension = True
        else:
          i += 1
      if undefined_extension:
        print(programming_language_extension[i], "extension is not recognized")
        programming_language_extension, problems_extensions_length = enter_extensions()
      else:
        problems_extensions_length = len(programming_language_extension)
        if problems_extensions_length > problems_num:
          print(f"expected at most {problems_num} extensions, got {problems_extensions_length}.")
          programming_language_extension, problems_extensions_length = enter_extensions()

    elif isinstance(programming_language_extension, str):
      if extensions.get(programming_language_extension) is None:
        print("Extension is not recognized")
        programming_language_extension, problems_extensions_length = enter_extensions()
      else:
        programming_language_extension = [programming_language_extension]
        problems_extensions_length = 1

    else:
      default_language = conf_file["cfkit"]["default_language"]
      if not default_language:
        programming_language_extension, problems_extensions_length = enter_extensions()
      else:
        programming_language_extension = [language_conf[default_language]["extensions"][0]]
        problems_extensions_length = 1

    # Comment
    problems_files = []
    if add_problem_name_to_file_name:
      self.__list_problems(
        problems_list,
        lambda problem_index, problem_name, i:
          problems_files.append(file_name(
            problem_name,
            f"{self._id}{problem_index}",
            programming_language_extension[
              ((i-problems_num+problems_extensions_length
                ) + abs(i-problems_num+problems_extensions_length)) // 2
            ]
          )
        )
      )
    else:
      self.__list_problems(
      problems_list,
      lambda problem_index, _, i:
        problems_files.append(f"{problem_index.lower()}." + programming_language_extension[
          ((i-problems_num+problems_extensions_length
            ) + abs(i-problems_num+problems_extensions_length)) // 2])
      )

    def create_solution_file(one_extension = True):
      def write_to_multiple_files_at_once(files, template):
        for file in files:
          template_source_code = read_text_from_file(template)
          with open(file, 'w', encoding="UTF-8") as solution_file:
            solution_file.write(template_source_code)

      if one_extension:
        write_to_multiple_files_at_once(problems_files, retrieve_template(problems_files[0]))

      else:
        i = 0
        while i < problems_num:
          aux = problems_num-problems_extensions_length+1
          if i < aux:
            write_to_multiple_files_at_once(
              problems_files[i:aux],
              retrieve_template(problems_files[i])
            )
            i += aux
          else:
            template_source_code = read_text_from_file(retrieve_template(problems_files[i]))
            with open(problems_files[i], 'w', encoding="UTF-8") as file:
              file.write(template_source_code)
            i += 1

    if problems_extensions_length > 1:
      create_solution_file(False)
    else:
      create_solution_file()

    print("Problems Files Created!")


  def parse_problems(self):
    """
    Documentation
    """
    pass


  def problems_list(self) -> list:
    """
    Documentation
    """
    return self.__list_problems()

if __name__ == "__main__":
  # Problem("1846D").parse()
  # one = Contest("4")
  # one.create_problems_files(["cpp", "java", "py", "cxx"], True)
  # print(one.problems_list())
  pass