"""
Documentation
"""
from os import getcwd, chdir

from cfkit.utils.check import raise_error_if_path_missing
from cfkit.client.fetch import get_response
from cfkit.utils.common import (
  file_name,
  create_file_folder,
  retrieve_template,
  problems_content,
  samples_dir,
  read_text_from_file,
  read_json_file,
  fetch_samples,
  write_text_to_file
)
from cfkit.utils.print import colored_text
from cfkit.utils.variables import conf_file
from cfkit.utils.variables import resources_folder
from cfkit.utils.variables import language_conf_path
from cfkit.utils.constants import Directory
from cfkit.utils.constants import EXTENSIONS

class Contest:
  """
  Documentation
  """
  def __init__(self, contest_id: int) -> None:
    self.name = None
    self._id = contest_id
    self._content = self.__content()
    self.problems = list(map(lambda x: x[0], self._content))
    self._problems_letters = list(map(lambda x: x[:x.find('.')], self.problems))

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
          ),
          self._id,
          html_page=True
        )
      else:
        response, self.name = problems_content(contest_problems_statement_file_path, self._id)
      return response
    colored_text(
      "Contest ID must be an integer",
      one_color="error_4",
      exit_code_after_print_statement=1
    )

  def create_problems_files(
      self,
      programming_language_extension: str | list | tuple | None = None,
      add_problem_name_to_file_name: bool = False,
      path: Directory = None
    ) -> None:
    """
    Documentation
    """
    if path is None:
      path = getcwd()

    if path != getcwd():
      raise_error_if_path_missing(path, 'd')
    chdir(path)

    if path.basename(path) != str(self._id):
      folder_name = create_file_folder(str(self._id), 'd')
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
          file_name(self._problems_letters[i], problem_name, programming_language_extension[index])
        )

    else:
      for i, problem_name in enumerate(self.problems):
        index = (
          (i-problems_num+problems_extensions_length)+abs(i-problems_num+problems_extensions_length)
        )
        index //= 2 # since (i - problems_num + problems_extensions_length) was added twice
        problems_files.append(
          f"{self._problems_letters[i].lower()}.{programming_language_extension[index]}"
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
      path: Directory = None,
      create_tests_dir: bool = True,
    ) -> None:
    """
    Documentation
    """
    if path is None:
      path = getcwd()

    print(f"Parsing {self._id} contest")
    fetch_samples(
      problem_statement=self._content,
      path_to_save_samples=samples_dir(
        create_tests_dir,
        path,
        None,
        False
      ),
      attributes=("contest", self._id, self.name)
    )
    colored_text("All test cases parsed successfully.", one_color="correct")

if __name__ == "__main__":
  # Contest("1882")?
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
