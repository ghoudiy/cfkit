"""
Detect the implementation type (compiler or interpreter) from the provided file
and execute it with sample input and output while managing memory usage.
"""

from sys import exit as sysExit, maxsize, executable
from os import path
from subprocess import run

from cfkit.util.util import (
  confirm,
  check_command,
  enter_number,
  read_json_file,
  machine,
  json_folder
  )

NOTE = """
2. Do not include any input or output specifications in your command! (i.e. '< in > out')

3. Please choose carefully, as your selection will become the default option for future use.
"""

COMPILING_NOTE = """\
4. When providing the compilation command, \
make sure to include the execution part as well if necessary.
For instance, if you're using Kotlin, your command should look something like this:
{colored_text("kotlinc {file} -d {output}.jar && java -jar {output}.jar", "command", False, False)}
The '&& java -jar {{output}}.jar' part is important for executing the compiled code.
If your compilation process requires additional steps for execution, \
be sure to include them in the command as well


There are two types of compilation commands:\n
1. Compile only: Compiles the code without executing.
    Example: g++ -Wall -o {output} {file}
2. Compile and Execute: Compiles and immediately executes the code.
    Example: go run {file}

Choose the appropriate command based on your needs."""

def detect_implementation(programming_language: str):
  '''
  Identify programming language implementations available on the system and supported by Codeforces.
  '''

  compilers_interpreters: dict = read_json_file(path.join(json_folder, "compilers_interpreters.json"))
  compiling_commands: dict = read_json_file(path.join(json_folder, "compiling_commands.json"))
  one_line_compiled: dict = read_json_file(path.join(json_folder, "one_line_compiled.json"))
  interpreting_commands: dict = read_json_file(path.join(json_folder, "interpreting_commands.json"))

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
    if command and (machine in ("linux", "darwin")) else command

  def check_installed_implementation(check_implementations_availability_list):
    i = -1
    test = False
    installed_implementations_list_bool = [False] * len(check_implementations_availability_list)
    while not test and i < len(check_implementations_availability_list) - 1:
      i += 1
      installed_implementations_list_bool[i] = language(check_implementations_availability_list[i])
    return installed_implementations_list_bool

  def get_command(lang):
    check_implementation_version_command = compilers_interpreters[lang]

    # If there is only one command of execution
    if isinstance(check_implementation_version_command, str):
      if lang == "Delphi 7":
        test = maxsize > 4294967296
        command = None
        if test and language(check_implementation_version_command.replace("{architecture}", "64")):
          command = compiling_commands[lang].replace("{architecture}", "64")

        if not test or not command:
          command = compiling_commands[lang].replace("{architecture}", "32")\
            if language(check_implementation_version_command.replace\
            ("{architecture}", "32")) else None

        implementation_command = change_rename_command(command)
        if implementation_command is None:
          print("Oops! Delphi 7 (dcc) compiler used in Codeforces isn't available on your system.")
          return None, "compiler"
        return implementation_command, "compiler"

      if lang in interpreting_commands:
        implementation_command = interpreting_commands[lang], "interpreter"

      elif lang in compiling_commands:
        if lang == "C":
          implementation_command = compiling_commands[lang][machine], "compiler"
        
        else:
          implementation_command = compiling_commands[lang], "compiler"

      else:
        implementation_command = one_line_compiled[lang], "compile and execute"

      if not language(check_implementation_version_command):
        print(
          f"Oops! {lang} {implementation_command[1] if implementation_command[1] != 'compile and execute' else 'compiler'} (",
          check_implementation_version_command[:check_implementation_version_command.find(' ')],
          ") used in Codeforces isnt't available on your system.", sep='')
        implementation_command = None, implementation_command[1]

    # Python only for now
    elif isinstance(check_implementation_version_command, list):
      tmp = check_installed_implementation(check_implementation_version_command)
      if any(tmp):
        tmp = check_implementation_version_command[tmp.index(True)]
        implementation_command = interpreting_commands[lang].replace\
          ("{command}", tmp[:tmp.find(" ")]), "interpreter"

      else:
        print("Oops! You don't have python installed on the system or it may be not added to PATH.")
        sysExit(1)

    elif isinstance(check_implementation_version_command, dict):
      implementation_lists = {}
      implementation = "compilers"
      # Loop through language implementations
      # key is the compiler name and value is the check version command of that compiler
      for key, value in check_implementation_version_command.items():

        if isinstance(value, list):
        # This condition was written because C++ is notably exceptional in this situation
        # as it remains compatible with both g++ and gcc compilers within the GCC compiler group.
          implementation_lists[key] = check_installed_implementation(value)

          if implementation_lists[key][0]: # If g++ is installed
            implementation_lists[key] = True

          elif not implementation_lists[key][0] and implementation_lists[key][1]:
            if machine == "win32":
              return "gcc -Wall -Wextra -Wconversion -fno-strict-aliasing -lm -s " +\
                "-Wl,--stack=268435456 -O2 -o {output}.exe {file} -lstdc++", "compiler"

            return "gcc -Wall -Wextra -Wconversion -fno-strict-aliasing -lm -s -O2 -o " +\
              "{output}.exe {file} -lstdc++", "compiler"

          elif not (implementation_lists[key][0] and implementation_lists[key][1]):
            return None, "compiler"

        elif isinstance(value, str):
          implementation_lists[key] = language(value)
          if lang == "JavaScript":
            implementation = "interpreters"

      # Debugging
      for key in implementation_lists:
        implementation_lists[key] = True

      implementation_lists[".NET"] = False
      for key in [key for key, value in implementation_lists.items() if not value]:
        del implementation_lists[key]

      implementation_lists = implementation_lists.keys()
      implementation_lists_length = len(implementation_lists)
      if implementation_lists_length:
        def select_implementation(list_of_implementations: dict):
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
            for implementation in implementation_lists:
              compile_command = list_of_implementations[implementation]

              # Compiler had multiple versions such as GNU G++, Clang++
              if has_versions(compile_command, False):
                for compi in compile_command.keys():
                  compilers.append((implementation, compi))
                  print(f"{len(compilers)}. {compi}")

              else: # list_of_implementations[implementation] == command
                compilers.append((list_of_implementations[implementation], (implementation,)))
                print(f"{len(compilers)}. {implementation}")

            compiler_index = enter_number(
              "\nPlease choose carefully, as your selection " +
              "will become the default option for future use.\nCompiler index: ",
              "Compiler index: ", range(1, len(compilers) + 1)) - 1

            com = isinstance(compilers[compiler_index][1], tuple)
            if com:
              aux = compilers[compiler_index][0]
              if compilers[compiler_index][1][0] == "PascalABC.NET":
                selected_implementation = change_rename_command(aux)
              else:
                if machine in aux:
                  selected_implementation = aux[machine]
                else:
                  selected_implementation = aux
            else:
              selected_implementation = list_of_implementations[
                compilers[compiler_index][0]][
                compilers[compiler_index][1]][machine]

          elif implementation_lists_length:
            key = list(list_of_implementations.keys())[0]
            if machine in list_of_implementations[key]:
              selected_implementation = list_of_implementations[key][machine]
            else:
              selected_implementation = list_of_implementations[key]

          return selected_implementation

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

        implementation_command = select_implementation(list_of_implementations)

        if len(list_of_implementations) == 1 and imp == "Mono" or (
          implementation_command == one_line_compiled["C#"]["Mono"]):

          implementation_command = implementation_command, "compile and execute"

        else:
          implementation_command = implementation_command, implementation

      else:
        compilers_interpreters[lang] = list(compilers_interpreters[lang].keys())

        statement = f"{(', '.join(compilers_interpreters[lang][:-2]))} " +\
        f"{compilers_interpreters[lang][-2]} and " +\
        f"{compilers_interpreters[lang][-1]} {implementation}".lstrip()

        print(f"Oops! {statement} that are used in Codeforces aren't available on your system.",)
        implementation_command = None, implementation[:-1]

    return implementation_command

  command, implementation = get_command(programming_language)
  if command:
     # Add executing command to compiling command and save command to config file
    return command, implementation

  if programming_language == "Python":
    return executable, "interpreter"

  placeholders = [
    "Notes:",
    "1. Please include the following placeholders in your command:",
    "- {file}: This represents the path to the script file.",
    "Your command might look like this:",
    "interpreting-command [options...] {file}"
  ]

  if implementation in ("compiler", "compile and execute"):
    placeholders.insert(3, "- {output}: This represents the compiled code. (Without .exe or .out)")
    placeholders[-1] =  "compile-command [options...] {file} -o {output}"
    print("\n\n" + "\n".join(placeholders))
    print(NOTE)
    print(COMPILING_NOTE)
    compilation_type = enter_number(
      "Compilation type index: ",
      "Compilation type index: ",
      range(1, 3))
    if compilation_type == 1:
      implementation = "compiler"
      message = f"{placeholders[1][3:]}\n{placeholders[2:4]}", "compiler"
      command = confirm(
        check_command(
          input("\nEnter below the command you'd like to use:\n"),
          (message,)
        ),
        "command",
        message
      )
    else:
      implementation = "compile and execute"
      message = f"{placeholders[1][3:]}\n{placeholders[2]}"
      command = confirm(
        check_command(
          input("\nEnter below the command you'd like to use:\n"),
          message
        ),
        "command",
        message
      )

  else:
    print("\n\n" + "\n".join(placeholders))
    print(NOTE)
    implementation = "interpreter"
    message = f"{placeholders[1][3:]}\n{placeholders[2]}"
    command = confirm(
      check_command(
        input("\nEnter below the command you'd like to use:\n"),
        message
      ),
      "command",
      message
    )

  return command, implementation

L = ['C', 'C++', 'C#', 'D', 'Go', 'Haskell GHC', 'Java', 'Kotlin', 'OCaml', 'Delphi 7', 'Pascal', 'Perl', 'PHP', 'Python', 'Ruby', 
'Rust', 'Scala', 'JavaScript d8', 'Node.js']

for prog in L:
  a = detect_implementation(prog)
  print(f"Programming Language = '{prog}'")
  print(type(a))
  print(a)
  print('-' * 50)
