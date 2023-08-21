import sys
import os
from json import load
from subprocess import run


def read_json_file(x):
  with open(f"{x}.json", 'r', encoding="UTF-8") as file:
    return load(file)


os.chdir(f"{os.path.abspath(os.path.dirname(__file__))}/json")
extensions: dict = read_json_file("extensions")
compilers_interpreters: dict = read_json_file("compilers_interpreters")
compiling_commands: dict = read_json_file("compiling_commands")
one_line_compiled: dict = read_json_file("one_line_compiled")
interpreting_commands: dict = read_json_file("interpreting_commands")


executing_commands = {
 "win32": "{output}.exe < {input_file} > {output_file}", 
 "linux": "./{output}.out < {input_file} > {output_file}",
 "darwin": "./{output}.out < {input_file} > {output_file}",
}


def detect_implementation(ext, inputPath, outputPath):
  language = lambda command: run(command, capture_output=True, shell=True, text=True).returncode ==0
  machine = sys.platform
  change_rename_command = lambda x: x.replace("&& ren", "&& mv") \
    if x and (machine in ("linux", "darwin")) else x # if the user uses compatibility layer

  def check_installed_compilers(L):
    i = -1
    ok = False
    R = [False] * len(L)
    while not ok and i < len(L) - 1:
      i += 1
      R[i] = language(L[i])
    return R

  def get_command(lang):
    check_version_compiler_command = compilers_interpreters[lang]

    if isinstance(check_version_compiler_command, str): # If there is only one command of execution
      if lang == "Delphi 7":
        ok = sys.maxsize > 4294967296
        command = None
        if ok and language(check_version_compiler_command.replace("{architecture}", "64")):
          command = compiling_commands[lang]["win32"].replace("{architecture}", "64")

        if not ok or not command:
          command = compiling_commands[lang]["win32"].replace("{architecture}", "32") \
            if language(check_version_compiler_command.replace("{architecture}", "32")) else None

        implementation_command =  change_rename_command(command)

      elif language(check_version_compiler_command):
        if lang in interpreting_commands:
          implementation_command =  interpreting_commands[lang]

        elif lang in compiling_commands:
          implementation_command =  compiling_commands[lang][machine]

        else:
          implementation_command =  one_line_compiled[lang]

      else:
        implementation_command =  None

    elif isinstance(check_version_compiler_command, list): # Python only for now
      tmp = check_installed_compilers(check_version_compiler_command)
      if any(tmp):
        tmp = check_version_compiler_command[tmp.index(True)]
        implementation_command = interpreting_commands[lang].replace \
          ("{command}", tmp[:tmp.find(" ")])
      else:
        implementation_command =  None

    elif isinstance(check_version_compiler_command, dict):
      compilers_list = {}
      for key, value in check_version_compiler_command.items():

        # isinstance(value, list) -> C++ is notably exceptional in this situation
        # as it remains compatible with both the g++ and gcc compilers
        # within the GCC compiler group.
        if isinstance(value, list):
          compilers_list[key] = check_installed_compilers(value)

          if compilers_list[key][0]:
            compilers_list[key] = True

          elif not compilers_list[key][0] and compilers_list[key][1]:
            if machine == "win32":
              return "gcc -Wall -Wextra -Wconversion -fno-strict-aliasing -lm -s \
                -Wl,--stack=268435456 -O2 -o {output}.exe {file} -lstdc++"

            return "gcc -Wall -Wextra -Wconversion -fno-strict-aliasing -lm -s \
              -O2 -o {output}.exe {file} -lstdc++"

          elif not (compilers_list[key][0] and compilers_list[key][1]):
            return None

        elif isinstance(value, str):
          compilers_list[key] = language(value)

      for key in [key for key, value in compilers_list.items() if not value]:
        del compilers_list[key]

      compilers_list = compilers_list.keys()
      l = len(compilers_list)
      if l:
        def select_implementation(K: dict):
          tmp = K[lang]
          not_a_command = lambda x, func: func(list(x.keys()), ["win32", "linux", "darwin"]) \
            if isinstance(x, dict) else False
          diff = lambda x, y: x != y
          if l > 1 or (l == 1 and not_a_command(tmp, diff)):
            print("Multiple compilers are available for the given file:")

            compilers = []
            for implementation in compilers_list:
              compile_command = K[lang][implementation]

              if not_a_command(compile_command, diff): # Compiling commands only
                for compi in compile_command.keys():
                  compilers.append((implementation, compi))
                  print(f"{len(compilers)}. {compi}")

              else:
                compilers.append((K[lang][implementation], (implementation,)))
                print(f"{len(compilers)}. {implementation}")

            c = int(input("Please choose carefully, \
                          as your selection will become the default option for future use \
                          \nCompiler index: "))
            while c not in range(1, len(compilers) + 1):
              c = int(input("Compiler index: "))

            com = isinstance(compilers[c-1][1], tuple)
            if com:
              aux = compilers[c-1][0]
              if not_a_command(aux, lambda x, y: x == y):
                if compilers[c-1][1][0] == "PascalABC.NET":
                  selected_implementation = change_rename_command(aux[machine])
                selected_implementation = aux[machine]
              selected_implementation = aux

            selected_implementation = K[lang][compilers[c-1][0]][compilers[c-1][1]][machine]

          elif l:
            if machine in tmp:
              selected_implementation = tmp[machine]
            selected_implementation = tmp

          return selected_implementation

        K = {lang: {}}
        for x in compilers_list:
          if lang in compiling_commands and x in compiling_commands[lang]:
            K[lang].update(compiling_commands[lang])
          elif lang in one_line_compiled and x in one_line_compiled[lang]:
            K[lang].update(one_line_compiled[lang])
          else:
            K[lang].update(interpreting_commands[lang])

        implementation_command = select_implementation(K)

      else:
        implementation_command = None
        # print("Oops! The compilers used in Codeforces aren't available on your system.")

    return implementation_command


  if ext not in extensions.keys():
    print("Please add the appropriate file extension to the file name.\
          This ensures accurate language identification.")
    sys.exit(1)

  else:
    lang = extensions[ext]

    command = get_command(lang)
    if command:

      return command.replace("{input_file}", inputPath)\
        .replace("{output_file}", outputPath) # Add executing command to compiling command and save command to config file

    print("Oops! The desired compiler is not installed on the system\
           or it may be not added to the PATH")
      # prompt and add programming language name and an executing command
