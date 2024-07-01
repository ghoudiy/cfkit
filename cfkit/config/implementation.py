"""
Detect the implementation type (compiler or interpreter) from the provided file
and execute it with sample input and output while managing memory usage.
"""

from sys import exit as sysExit, maxsize
from subprocess import run
from webbrowser import open as webOpen

from cfkit.utils.common import read_json_file
from cfkit.utils.print import colored_text
from cfkit.utils.input import retype, enter_number, select_option, confirm
from cfkit.utils.check import check_command

from cfkit.utils.variables import json_folder
from cfkit.utils.variables import MACHINE
from cfkit.utils.constants import COMPILING_NOTE
from cfkit.utils.constants import NOTE


def detect_implementation(programming_language: str):
  '''
  Identify programming language implementations available on the system and supported by Codeforces.
  '''

  compilers_interpreters: dict = read_json_file(json_folder.joinpath("compilers_interpreters.json"))
  compiling_commands: dict = read_json_file(json_folder.joinpath("compiling_commands.json"))
  one_line_compiled: dict = read_json_file(json_folder.joinpath("one_line_compiled.json"))
  interpreting_commands: dict = read_json_file(json_folder.joinpath("interpreting_commands.json"))

  def language(command: str) -> bool:
    '''
    Check if the specified programming language is installed on the system and added to the PATH.
    '''
    aux = run(command, capture_output=True, shell=True, text=True, check=False).returncode
    return aux == 0 if command != "pabcnetc" else aux == 3762504530

  def change_rename_command(command):
    '''
    If the user utilizes a compatibility layer on Linux or macOS to execute Windows applications.
    '''
    return command.replace("&& ren", "&& mv")\
    if command and (MACHINE != "win32") else command

  def check_installed_implementation(check_implementations_availability_list):
    '''
    Loop through implementation check version command
    (i.e. "g++ --version", "gcc --version", "python -V"...)
    '''
    i = -1
    test = False
    installed_implementations_list_bool = [False] * len(check_implementations_availability_list)
    while not test and i < len(check_implementations_availability_list) - 1:
      i += 1
      installed_implementations_list_bool[i] = language(check_implementations_availability_list[i])
    return installed_implementations_list_bool

  def get_command(lang):

    check_implementation_version_command = compilers_interpreters[lang]
    save_command = True

    # If there is only one command of execution
    if isinstance(check_implementation_version_command, str):
      if lang == "Delphi":
        test = maxsize > 4294967296
        command = None
        if test and language(check_implementation_version_command.replace("{architecture}", "64")):
          command = compiling_commands[lang].replace("{architecture}", "64")

        if not test or not command:
          command = compiling_commands[lang].replace("{architecture}", "32")\
            if language(check_implementation_version_command.replace\
            ("{architecture}", "32")) else None

        implementation_command = change_rename_command(command), "compiler"
        if implementation_command[0] is None:
          print(
            f"Oops! Delphi compiler (dcc{'64' if test else '32'})",
            "used in Codeforces isn't available on your system."
          )

      else:
        # Check if the language is interpreted or compiled language
        if lang in interpreting_commands:
          implementation_command = interpreting_commands[lang], "interpreter"

        elif lang in compiling_commands:
          # Because C is the only language between (Rust, Delphi, OCaml)
          # that have multiple compilitation command across platform
          if lang == "C":
            implementation_command = compiling_commands[lang][MACHINE], "compiler"

          else:
            implementation_command = compiling_commands[lang], "compiler"

        else: # Also compiled language but it can be compiled and executed in the same time
          implementation_command = one_line_compiled[lang], "compile and execute"

        if not language(check_implementation_version_command):
          implementation_command = None, implementation_command[1]
          if implementation_command[1] == "compile and execute":
            implementation_command = None, "compiler"
          print(
            f"Oops! {lang} {implementation_command[1]} (",
            check_implementation_version_command[:check_implementation_version_command.find(' ')],
            ") used in Codeforces isn't available on your system.", sep='')

    # This condition was written because Python has multiple executing commands
    # In Windows for example you execute a python (python2 or python3) file using "python"
    # But in Linux you have to specify the version i.e. python3 or python2
    elif isinstance(check_implementation_version_command, list):
      tmp = check_installed_implementation(check_implementation_version_command)
      if any(tmp):
        tmp = check_implementation_version_command[tmp.index(True)]
        implementation_command = interpreting_commands[lang].replace\
          ("{command}", tmp[:tmp.find(" ")]), "interpreter"

      else:
        print("Oops! You don't have python installed on the system or it may be not added to PATH.")
        return None, "interpreter"

    else: # A dictionary of multiple compilers
      implementation_lists = {}
      implementation = "compilers"
      # Loop through language implementations
      # 'key' is the compiler name and 'value' is the check version command of that implementation
      for key, value in check_implementation_version_command.items():

        # This condition was written because C++ is notably exceptional in this situation
        # as it remains compatible with both g++ and gcc compilers within the GCC compiler group.
        if isinstance(value, list):
          implementation_lists[key] = check_installed_implementation(value)

          if implementation_lists[key][0]: # If g++ is installed
            implementation_lists[key] = True

          elif not implementation_lists[key][0] and implementation_lists[key][1]:
            if MACHINE == "win32":
              return (
                "gcc -Wall -Wextra -Wconversion -fno-strict-aliasing -lm -s "
                "-Wl,--stack=268435456 -O2 -o {output}.exe {file} -lstdc++", "compiler"
              )

            return (
              "gcc -Wall -Wextra -Wconversion -fno-strict-aliasing -lm -s -O2 -o "
              "{output}.exe {file} -lstdc++", "compiler"
            )

          elif not (implementation_lists[key][0] and implementation_lists[key][1]):
            return None, "compiler"

        else:
          implementation_lists[key] = language(value)
          if lang == "JavaScript":
            implementation = "interpreters"

      #! Debugging
      for key in implementation_lists:
        implementation_lists[key] = False

      implementation_lists[".NET"] = False
      for key in [key for key, value in implementation_lists.items() if not value]:
        del implementation_lists[key]

      implementation_lists = implementation_lists.keys()
      implementation_lists_length = len(implementation_lists)
      if implementation_lists_length:
        def select_implementation(list_of_implementations: dict, save_command: bool):
          def has_versions(compiler, deep=True) -> bool:
            if isinstance(compiler, dict):
              value = list(compiler.values())[0]
              if deep:
                if isinstance(value, dict):
                  return isinstance(list(value.values())[0], dict)
                return False

              return isinstance(value, dict)
            return False

          if implementation_lists_length > 1 or (
            implementation_lists_length == 1 and has_versions(list_of_implementations)):

            print("Multiple compilers are available for the given file:")

            compilers = []
            choices = []
            for implementation in implementation_lists:
              compile_command = list_of_implementations[implementation]

              # Compiler had multiple versions such as GNU G++, Clang++
              if has_versions(compile_command, False):
                for compi in compile_command.keys():
                  compilers.append((implementation, compi))
                  choices.append(compi)
                  print(f"{len(compilers)}. {compi}") # Demo

              else: # list_of_implementations[implementation] == command
                compilers.append((list_of_implementations[implementation], (implementation,)))
                choices.append(implementation)
                print(f"{len(compilers)}. {implementation}") # Demo

            compiler_index = enter_number(
              "Compiler index: ",
              "Compiler index: ",
              range(1, len(compilers) + 1)
            ) - 1 # Demo
            # compiler_index = select_option("Choose one compiler:", choices, True) - 1

            com = isinstance(compilers[compiler_index][1], tuple)
            if com:
              aux = compilers[compiler_index][0]
              if compilers[compiler_index][1][0] == "PascalABC.NET":
                selected_implementation = change_rename_command(aux)
              else:
                if MACHINE in aux:
                  selected_implementation = aux[MACHINE]
                else:
                  selected_implementation = aux
            else:
              selected_implementation = list_of_implementations[
                compilers[compiler_index][0]][
                compilers[compiler_index][1]][MACHINE]

            save_command = confirm(
              "Would you like to save your implementation choice for future use?"
            )

          elif implementation_lists_length:
            key = list(list_of_implementations.keys())[0]
            if MACHINE in list_of_implementations[key]:
              selected_implementation = list_of_implementations[key][MACHINE]
            else:
              selected_implementation = list_of_implementations[key]

          return selected_implementation, save_command

        list_of_implementations = {}
        implementation = "compiler"
        for imp in implementation_lists:
          if lang in compiling_commands and imp in compiling_commands[lang]:
            list_of_implementations.update({imp: compiling_commands[lang][imp]})

          elif lang in one_line_compiled and imp in one_line_compiled[lang]:
            list_of_implementations.update({imp: one_line_compiled[lang][imp]})

          else:
            list_of_implementations.update({imp: interpreting_commands[lang][imp]})
            implementation = "interpreter"

        implementation_command, save_command = select_implementation(
          list_of_implementations,
          save_command
        )

        if len(list_of_implementations) == 1 and imp == "Mono" or (
          implementation_command == one_line_compiled["C#"]["Mono"]):

          implementation_command = implementation_command, "compile and execute"

        else:
          implementation_command = implementation_command, implementation

      else:
        compilers_interpreters[lang] = list(compilers_interpreters[lang].keys())
        statement = (
          f"{(', '.join(compilers_interpreters[lang][:-1]))} and "
          f"{compilers_interpreters[lang][-1]} {implementation}".lstrip()
        )
        print(f"Oops! {statement} that are used in Codeforces aren't available on your system.",)
        implementation_command = None, implementation[:-1]

    return implementation_command, save_command


  command, save_command = get_command(programming_language)
  command, implementation = command[0], command[1]
  if command:
    return (command, implementation), save_command

  implementation_type = implementation if implementation != 'compile and execute' else 'compiler'

  action_index = select_option(
    "What do you want to do? ",
    data=[
      f"Open official download page of the {implementation_type}",
      f"Enter a custom command for an already installed {implementation_type}"
    ],
    index=True,
    disp_horizontally=False
  )

  if action_index == 1:
    sites = {
      "C": "https://gcc.gnu.org/",
      "C++": {
        "GNU G++": "https://gcc.gnu.org/",
        "Clang++": "https://github.com/llvm/llvm-project/releases/latest",
        "Microsoft Visual Studio C++": "https://visualstudio.microsoft.com/downloads/"
      },
      "C#": {
        "Mono": "https://www.mono-project.com/download/stable/",
        ".NET": "https://dotnet.microsoft.com/en-us/download"
      },
      "D": "https://dlang.org/download.html",
      "Go": "https://go.dev/doc/install",
      "Haskell": "https://www.haskell.org/downloads/",
      "Java": "https://www.java.com/en/download/",
      "Kotlin": "https://kotlinlang.org/docs/getting-started.html#install-kotlin",
      "OCaml": "https://ocaml.org/install",
      "Delphi": "https://www.embarcadero.com/products/delphi/starter/free-download",
      "Pascal": {
        "Free Pascal": "https://www.freepascal.org/download.html",
        "PascalABC.NET": "https://pascalabc.net/en/download",
      },
      "Perl": "https://www.perl.org/get.html",
      "PHP": "https://www.php.net/downloads.php",
      "Python": "https://www.python.org/downloads/",
      "Ruby": "https://www.ruby-lang.org/en/downloads/",
      "Rust": "https://www.rust-lang.org/tools/install",
      "Scala": "https://www.scala-lang.org/download/",
      "JavaScript": {
        "JavaScipt d8": "https://v8.dev/docs/build-gn",
        "Node.js": "https://nodejs.org/en/download"
      }
    }
    site = sites[programming_language]
    if isinstance(site, dict):
      print()
      implementation_key = select_option(
        f"{implementation_type.capitalize()} index: ",
        list(site.keys()),
        index=False,
        disp_horizontally=False
      )
      webOpen(sites[programming_language][implementation_key])
    else:
      webOpen(site)

    sysExit(0)

  placeholders = [
    "\n<bright_text>Notes:</bright_text>\n",
    "<red>I</red>. Please include the following placeholders in your command:",
    "- %%{file}%%: This represents the path to the script file.",
    "Your command might look like this:",
    "interpreting-command [options...] %%{file}%%"
  ]

  if implementation in ("compiler", "compile and execute"):
    placeholders.insert(3, "- %%{output}%%: This represents the compiled code. (Without .exe or .out)")
    placeholders[-1] =  "compile-command [options...] %%{file}%% -o %%{output}%%"
    colored_text(
      "\n".join(placeholders) + "\n" + NOTE + "\n" + COMPILING_NOTE + "\n"
    )
    compilation_type = enter_number(
      "Compilation type index: ",
      "Compilation type index: ",
      range(1, 3))
    if compilation_type == 1:
      implementation = "compiler"
      message = f"{placeholders[1]}\n{placeholders[2]}\n{placeholders[3]}", None
      command = retype(
        check_command(
          input("\nEnter below the command you'd like to use:\n").strip(),
          message
        ),
        "command",
        message
      )
    else:
      implementation = "compile and execute"
      message = f"{placeholders[1][3:]}\n{placeholders[2]}"
      command = retype(
        check_command(
          input("\nEnter below the command you'd like to use:\n").strip(),
          message
        ),
        "command",
        message
      )

  else:
    colored_text("\n".join(placeholders) + "\n" + NOTE)
    implementation = "interpreter"
    message = f"{placeholders[1][3:]}\n{placeholders[2]}"
    command = retype(
      check_command(
        input("\nEnter below the command you'd like to use:\n").strip(),
        message
      ),
      "command",
      message
    )

  save_command = confirm(
    "Would you like to save your implementation command for future use?"
  )
  return (command, implementation), save_command

if __name__ == "__main__":
  print(detect_implementation("C++"))
