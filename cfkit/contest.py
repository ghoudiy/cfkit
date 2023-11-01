"""
Documentation
"""
import sys
import os
from typing import TypeAlias
from requests import get

from cfkit.util.common import (
  get_response,
  check_path_existence,
  file_name,
  colored_text,
  create_file_folder,
  folder_file_exists,
  retrieve_template,
  problems_content,
  # display_horizontally,
  # enter_number,
  samples_dir,
  read_text_from_file,
  fetch_samples,
  wrong_answer_verdict,
  write_text_to_file,
  is_number,
  yes_or_no,
  conf_file,
  config_folder,
  resources_folder,
  # template_folder,
  language_conf,
  extensions
)

Directory: TypeAlias = str


class Contest:
  """
  Documentation
  """
  def __init__(self, contest_id: int) -> None:
    self.name = None
    self._id = contest_id
    self._content = self.__content()
    self.problems = list(map(lambda x: x[0], self._content))

  def __content(self):
    if isinstance(self._id, str) and self._id.isdigit():
      self._id = int(self._id)

    # Debugging
    if isinstance(self._id, int):
      contest_problems_statement_file_path = resources_folder.joinpath("problems",f"{self._id}.txt")
      if not contest_problems_statement_file_path.exists():
        response, self.name = problems_content(
          get_response(
            f"https://codeforces.com/contest/{self._id}/problems",
            self._id,
            self._id
          ).text,
          self._id,
          None,
          True
        )
      else:
        response, self.name = problems_content(contest_problems_statement_file_path, self._id)
      return response
    else:
      colored_text("Contest ID must be an integer", "error 5")
      sys.exit(1)

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

    problems_num = len(self.problems)

    def check_for_undefined_extensions(programming_language_extension: list):
      i = 0
      problems_extensions_length = len(programming_language_extension)
      undefined_extension = False
      while not undefined_extension and i < problems_extensions_length:
        if extensions.get(programming_language_extension[i]) is None:
          undefined_extension = True
        else:
          i += 1

      if undefined_extension:
        print(programming_language_extension[i], "extension is not recognized")
        return enter_extensions()

      if problems_extensions_length > problems_num:
        print(f"expected at most {problems_num} extensions, got {problems_extensions_length}.")
        return enter_extensions()
      return programming_language_extension, problems_extensions_length

    def enter_extensions() -> (list, int):
      # Show availables extensions
      for lang in language_conf:
        print(lang + ":", ", ".join(language_conf[lang]["extensions"]))

      # Get a list of file extensions separated by spaces from the user
      print(
        "To solve problems with multiple programming languages, "
        "enter the extensions separated by spaces.\n"
        "For example, if you enter two extensions, "
        "the program will consider the first extension for most problems and "
        "the last extension for the last problem.")

      programming_language_extension, problems_extensions_length = check_for_undefined_extensions(
        input("Extension(s): ").strip().split()
      )

      # If the user uses one programming language to solve all problems
      if len(programming_language_extension) == 1:
        colored_text(
          "To avoid entering extension every time\n"
          "run <command>'cf config default_language ...'</> command to configure your default programming language"
        )
        # colored_text(
        #   "To avoid entering extension every time\n"
        #   "run <command>'cf set'</> command to configure your default programming language"
        # )
      return programming_language_extension, problems_extensions_length

    if isinstance(programming_language_extension, list):
      programming_language_extension, problems_extensions_length = check_for_undefined_extensions(
        programming_language_extension
      )

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
      for i, problem in enumerate(self.problems):
        pt_pos = problem.find(".")
        problems_files.append(file_name(
          problem[pt_pos+2:],
          f"{self._id}{problem[:pt_pos]}",
          programming_language_extension[
            ((i-problems_num+problems_extensions_length
              ) + abs(i-problems_num+problems_extensions_length)) // 2]))
    else:
      for i, problem in enumerate(self.problems):
        problems_files.append(
          f"{problem[:problem.find('.')].lower()}." +\
          programming_language_extension[
            ((i-problems_num+problems_extensions_length
              ) + abs(i-problems_num+problems_extensions_length)) // 2]
        )

    def create_solution_file(one_extension = True):
      def write_to_multiple_files_at_once(files, template):
        for file in files:
          template_source_code = read_text_from_file(template)
          write_text_to_file(template_source_code, file)

      if one_extension:
        write_to_multiple_files_at_once(problems_files, retrieve_template(problems_files[0]))
      else:
        i = 0
        while i < problems_num:
          aux = problems_num - problems_extensions_length + 1
          if i < aux:
            write_to_multiple_files_at_once(
              problems_files[i:aux],
              retrieve_template(problems_files[i])
            )
            i += aux
          else:
            template_source_code = read_text_from_file(retrieve_template(problems_files[i]))
            write_text_to_file(template_source_code, problems_files[i])
            i += 1

    if problems_extensions_length > 1:
      create_solution_file(False)
    else:
      create_solution_file()

    colored_text("Problems Files Created!", "correct")


  def parse(
      self,
      path: Directory = os.getcwd(),
      create_tests_dir: bool = True,
    ) -> None:
    """
    Documentation
    """
    print(f"Parsing {self._id} contest")
    fetch_samples(
      problem_statement=self._content,
      path_to_save_samples=samples_dir(create_tests_dir,
        path,
        list(map(lambda x: f"{self._id}{x[:x.find('.')]}", self.problems)),
        os.listdir(path)
      ),
      attributes=("contest", self._id, self.name)
    )
    colored_text("All test cases parsed successfully.", "correct")

if __name__ == "__main__":
  Contest("1882")
  # print(contest_one.name)
  # print(contest_one.problems)
  # contest_one.parse()
  # print(one)
  # for i in one._content:
  #   print(i)
  #   print('-' * 50)
  # one.create_problems_files(["cpp", "java", "py", "cxx"], True)
  # print(one.problems_list())
  pass
