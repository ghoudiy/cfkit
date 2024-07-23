"""
Documentation
"""
from os import getcwd, chdir, path as osPath
from typing import Optional

from cfkit._utils.check import raise_error_if_path_missing
from cfkit._client.fetch import get_response
from cfkit._utils.common import file_name, retrieve_template
from cfkit._utils.file_operations import (
  create_file_folder,
  read_json_file,
  read_text_from_file,
  write_text_to_file
)
from cfkit._utils.parse_samples import fetch_samples, samples_dir, problems_content
from cfkit._utils.print import colored_text

from cfkit._utils.variables import conf_file, resources_folder, language_conf_path
from cfkit._utils.constants import Directory, EXTENSIONS

class Contest:
  """
  Documentation
  """
  def __init__(self, contest_id: int) -> None:
    self.name = None
    self.contest_id = contest_id
    self._content = self.__content()
    self.problems = list(map(lambda x: x[0], self._content))
    self.problems_letters = list(map(lambda x: x[:x.find('.')], self.problems))

  def __content(self):
    if isinstance(self.contest_id, str) and self.contest_id.isdigit():
      self.contest_id = int(self.contest_id)

    if isinstance(self.contest_id, int):
      contest_problems_statement_file_path = resources_folder.joinpath("problems",f"{self.contest_id}.txt")
      if not contest_problems_statement_file_path.exists():
        response, self.name = problems_content(
          get_response(
            f"https://codeforces.com/contest/{self.contest_id}/problems",
            self.contest_id,
            self.contest_id
          ),
          self.contest_id,
          html_page=True
        )
      else:
        response, self.name = problems_content(contest_problems_statement_file_path, self.contest_id)
      return response
    colored_text(
      "Contest ID must be an integer",
      one_color="error_4",
      exit_code_after_print_statement=4
    )

  def create_problems_files(
      self,
      path: Optional[Directory] = None,
      programming_language_extension: Optional[str] | Optional[tuple] | Optional[list] = None,
      add_problem_name_to_file_name: bool = False
    ) -> None:
    """
    Documentation
    """
    if path is None:
      path = getcwd()

    if path != getcwd():
      raise_error_if_path_missing(path, 'd')
    chdir(path)

    if osPath.basename(path) != str(self.contest_id):
      folder_name = create_file_folder(str(self.contest_id), 'd')
    chdir(folder_name)

    problems_num = len(self.problems)

    def enter_extensions(language_conf: dict) -> tuple[list, int]:
      # Show availables extensions
      for lang in language_conf:
        print(lang + ":", ", ".join(language_conf[lang]["extensions"]))

      # Get a list of file extensions separated by spaces from the user
      print(
        "To solve problems with multiple programming languages,",
        "enter the extensions separated by spaces.\n"
        "For example, if you enter two extensions,",
        "the program will consider the first extension for most problems and",
        "the last extension for the last problem."
      )

      programming_language_extension, problems_extensions_length = check_for_undefined_extensions(
        input("Extension(s): ").strip().split()
      )

      # If the user uses one programming language to solve all problems
      if len(programming_language_extension) == 1:
        colored_text(
          "To avoid entering extension every time\n"
          "run <command>&apos;cf config default_language ...&apos;</command> "
          "command to configure your default programming language"
        )
        # colored_text(
        #   "To avoid entering extension every time\n"
        #   "run <command>'cf set'</command> command to configure your default programming language"
        # )
      return programming_language_extension, problems_extensions_length

    def check_for_undefined_extensions(programming_language_extension: list):
      i = 0
      problems_extensions_length = len(programming_language_extension)
      undefined_extension = False
      while not undefined_extension and i < problems_extensions_length:
        undefined_extension = EXTENSIONS.get(programming_language_extension[i]) is None
        i += 1

      if undefined_extension:
        colored_text(f"&apos;{programming_language_extension[i]}&apos; extension is not recognized")
        return enter_extensions(language_conf)

      if problems_extensions_length > problems_num:
        print(f"expected at most {problems_num} extensions, got {problems_extensions_length}.")
        return enter_extensions(language_conf)
      return programming_language_extension, problems_extensions_length

    if isinstance(programming_language_extension, (list, tuple)):
      programming_language_extension, problems_extensions_length = check_for_undefined_extensions(
        programming_language_extension
      )

    elif isinstance(programming_language_extension, str):
      if EXTENSIONS.get(programming_language_extension) is None:
        colored_text("Extension is not recognized", one_color="error")
        programming_language_extension, problems_extensions_length = enter_extensions(
          read_json_file(language_conf_path)
        )
      else:
        programming_language_extension = [programming_language_extension]
        problems_extensions_length = 1

    else:
      language_conf = read_json_file(language_conf_path)
      default_language = conf_file["cfkit"]["default_language"]
      if not default_language:
        programming_language_extension, problems_extensions_length = enter_extensions(language_conf)
      else:
        programming_language_extension = [language_conf[default_language]["extensions"][0]]
        problems_extensions_length = 1

    # Comment
    problems_files = []
    if add_problem_name_to_file_name:
      for i, problem_name in enumerate(self.problems):
        pt_pos = problem_name.find(".")
        problem_name = problem_name[pt_pos+2:]
        index = (
          (i-problems_num+problems_extensions_length)+abs(i-problems_num+problems_extensions_length)
        )
        index //= 2 # since (i - problems_num + problems_extensions_length) was added twice

        problems_files.append(
          file_name(self.problems_letters[i], problem_name, programming_language_extension[index])
        )

    else:
      for i, problem_name in enumerate(self.problems):
        index = (
          (i-problems_num+problems_extensions_length)+abs(i-problems_num+problems_extensions_length)
        )
        index //= 2 # since (i - problems_num + problems_extensions_length) was added twice
        problems_files.append(
          f"{self.problems_letters[i].lower()}.{programming_language_extension[index]}"
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

    colored_text("Problems Files Created!", one_color="correct")

  def parse(
      self,
      path: Optional[Directory] = None,
      create_tests_dir: bool = True,
    ) -> None:
    """
    Documentation
    """
    if path is None:
      path = getcwd()

    print(f"Parsing contest {self.contest_id}")
    fetch_samples(
      problem_statement=self._content,
      path_to_save_samples=samples_dir(
        create_tests_dir,
        path
      ),
      attributes=("contest", self.contest_id, self.name),
    )
    colored_text("All test cases parsed successfully.", one_color="correct")
