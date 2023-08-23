from os import chdir, path
from sys import exit as sysExit, maxsize
from json import load, dump
from subprocess import run
from cfkit.util.util import machine, confirm

# def add_execute_command(dictionary):
#   for key, value in dictionary.items():
#     if isinstance(value, str):
#       dictionary[key] = f"{value} && {execute_commands[machine]}"
#     elif isinstance(value, dict):
#       add_execute_command(value)
#   return dictionary


def read_file(x):
  with open(x, 'r', encoding="UTF-8") as file:
    return load(file)


chdir(path.join(path.dirname(__file__), "json"))
extensions: dict = read_file("extensions.json")
compilers_interpreters: dict = read_file("compilers_interpreters.json")
compiling_commands: dict = read_file("compiling_commands.json")
one_line_compiled: dict = read_file("one_line_compiled.json")
interpreting_commands: dict = read_file("interpreting_commands.json")

NOTE = """
\nNote:
1. When providing the compilation command, \
please make sure to include the execution part as well if necessary.
For instance, if you're using Kotlin, your command should look something like this:
\nkotlinc {file} -d {output}.jar && java -jar {output}.jar\n
The '&& java -jar {output}.jar' part is important for executing the compiled code.
If your compilation process requires additional steps for execution, \
be sure to include them in the command as well.

2. Please choose carefully, as your selection will become the default option for future use. Thank you!
"""


def detect_implementation(programming_language):
  def language(command: str) -> bool:
    '''
    Check if the specified programming language is installed on the system and added to the PATH.
    '''
    aux = run(command, capture_output=True, shell=True, text=True).returncode
    return aux == 0 if command != "pabcnetc" else aux == 3762504530

  def change_rename_command(x):
    '''
    If the user utilizes a compatibility layer on Linux or macOS to execute Windows applications.
    '''
    return x.replace("&& ren", "&& mv") \
    if x and (machine in ("linux", "darwin")) else x # if the user uses compatibility layer


  def check_installed_implemenations(L):
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
        ok = maxsize > 4294967296
        command = None
        if ok and language(check_version_compiler_command.replace("{architecture}", "64")):
          command = compiling_commands[lang]["win32"].replace("{architecture}", "64")

        if not ok or not command:
          command = compiling_commands[lang]["win32"].replace("{architecture}", "32") \
            if language(check_version_compiler_command.replace("{architecture}", "32")) else None

        implementation_command = change_rename_command(command)
        if implementation_command is None:
          print("Oops! The compiler used in Codeforces isnt't available on your system.")
          return None, "compiler"
        return implementation_command, None

      if lang in interpreting_commands:
        aux = ("interpreter", interpreting_commands[lang])
      elif lang in compiling_commands:
        aux = ("compiler", compiling_commands[lang][machine])
      else:
        aux = ("compiler", one_line_compiled[lang])

      if language(check_version_compiler_command):
        implementation_command = aux[1], None
      else:
        print(f"Oops! The {aux[0]} used in Codeforces isnt't available on your system.")
        implementation_command = None, aux[0]

    elif isinstance(check_version_compiler_command, list): # Python only for now
      tmp = check_installed_implemenations(check_version_compiler_command)
      if any(tmp):
        tmp = check_version_compiler_command[tmp.index(True)]
        implementation_command = interpreting_commands[lang].replace \
          ("{command}", tmp[:tmp.find(" ")]), None
      else:
        print("Oops! You don't have python installed on the system or it may be not added to PATH.")
        sysExit(1)

    elif isinstance(check_version_compiler_command, dict):
      implementation_lists = {}
      implementation = "compilers"
      # Loop through language implementations (copmilers or interpreters)
      # key is the compiler name and value is the check version command of that compiler
      for key, value in check_version_compiler_command.items():

        # isinstance(value, list) -> This condition was written because C++ is notably exceptional in this situation
        # as it remains compatible with both the g++ and gcc compilers
        # within the GCC compiler group.
        if isinstance(value, list):
          implementation_lists[key] = check_installed_implemenations(value)

          if implementation_lists[key][0]: # If g++ is installed
            implementation_lists[key] = True

          elif not implementation_lists[key][0] and implementation_lists[key][1]:
            if machine == "win32":
              return "gcc -Wall -Wextra -Wconversion -fno-strict-aliasing -lm -s -Wl,--stack=268435456 -O2 -o {output}.exe {file} -lstdc++", None

            return "gcc -Wall -Wextra -Wconversion -fno-strict-aliasing -lm -s -O2 -o {output}.exe {file} -lstdc++", None

          elif not (implementation_lists[key][0] and implementation_lists[key][1]):
            return None, "compiler"

        elif isinstance(value, str):
          implementation_lists[key] = language(value)
          if lang == "JavaScript":
            implementation = "interpreters"

      for key in [key for key, value in implementation_lists.items() if not value]:
        del implementation_lists[key]

      implementation_lists = implementation_lists.keys()
      l = len(implementation_lists)
      if l:
        def select_implementation(K: dict):
          def not_a_command(x, func):
            return func(list(x.keys()), ["win32", "linux", "darwin"]) if isinstance(x, dict) \
                else False

          tmp = K[lang]
          if l > 1 or (l == 1 and not_a_command(tmp, lambda x, y: x != y)):
            print("Multiple compilers are available for the given file:")

            compilers = []
            for implementation in implementation_lists:
              compile_command = K[lang][implementation]

              if not_a_command(compile_command, lambda x, y: x != y): # Compiler had multiple versions such as GNU G++, Clang++
                for compi in compile_command.keys():
                  compilers.append((implementation, compi))
                  print(f"{len(compilers)}. {compi}")

              else: # K[lang][implementation] == command
                compilers.append((K[lang][implementation], (implementation,)))
                print(f"{len(compilers)}. {implementation}")

            c = input("Please choose carefully, as your selection will become the default option for future use\nCompiler index: ")

            while not c.isdigit() or int(c) not in range(1, len(compilers) + 1):
              c = input("Compiler index: ")
            c = int(c)

            com = isinstance(compilers[c-1][1], tuple)
            if com:
              aux = compilers[c-1][0]
              if not_a_command(aux, lambda x, y: x == y): # If the selected implementation had different executing commands across platforms
                if compilers[c-1][1][0] == "PascalABC.NET":
                  selected_implementation = change_rename_command(aux[machine])
                else:
                  selected_implementation = aux[machine]
              else:
                selected_implementation = aux
            else:
              selected_implementation = K[lang][compilers[c-1][0]][compilers[c-1][1]][machine]
            return selected_implementation


          elif l:
            if machine in tmp:
              selected_implementation = tmp[machine]
            else:
              selected_implementation = tmp

          return selected_implementation, None

        K = {lang: {}}
        for x in implementation_lists:
          if lang in compiling_commands and x in compiling_commands[lang]:
            K[lang].update(compiling_commands[lang])
          elif lang in one_line_compiled and x in one_line_compiled[lang]:
            K[lang].update(one_line_compiled[lang])
          else:
            K[lang].update(interpreting_commands[lang])

        implementation_command = select_implementation(K), None

      else:
        compilers_interpreters[lang] = list(compilers_interpreters[lang].keys())
        statement = f"{(', '.join(compilers_interpreters[lang][:-2]))} {compilers_interpreters[lang][-2]} and {compilers_interpreters[lang][-1]} {implementation}".lstrip()
        print(f"Oops! {statement} that are used in Codeforces aren't available on your system.",)
        implementation_command = None, implementation[:-1]

    return implementation_command

  command = get_command(programming_language)
  if command[0]:
     # Add executing command to compiling command and save command to config file
    return command

  L = ["Please include the following placeholders in your command:",
        "- {file}: This represents the path to the script file.",
        "Your command might look like this:",
        "interpreting-command [options...] {file}"
      ]

  if command[1] == 'compiler':
    L.insert(2, "- {output}: This represents the compiled code.",)
    L[-1] =  f"compile-command [options...] {{file}} -o {{output}}.{'exe' if machine == 'win32' else 'out'}"
    print("\n\n" + "\n".join(L))
    print(NOTE)
  else:
    print("\n\n" + "\n".join(L))

  def check_command(x):
    while x.find("{output}") == -1 or x.find("{file}") == -1:
      print("\n" + "\n".join(L[:-2]))
      x = input("Command: ") + " < {input_file} > {output_file}"
    return x
  command = check_command(input("\nPlease enter below the command you'd like to use:\n"))
  return check_command(confirm(command, "command"))


def execute_file(file: str, inputPath: str, outputPath: str, memory_limit: float, sample_id) -> None:
  extension = file[file.rfind('.')+1:]
  if extension == file:
    print("Please add the appropriate file extension to the file name. This ensures accurate language identification.")
    sysExit(1)

  platform = "codeforces.com" # Codeforces only for now
  config_file = path.join(path.expanduser("~", "" if machine == "win32" else ".config", "cfkit", "platforms.json"))
  configuration = read_file(config_file)
  execute_command = configuration[platform]["execute_command"]
  if execute_command is None:
    if extension not in extensions:
      print("Oops! The desired language is not supported on Codeforces.")
      sysExit(1)

    programming_language = extensions[extension]
    execute_command = detect_implementation(programming_language)
    configuration[platform]["execute_command"] = execute_command
    configuration[platform]["default_language"] = programming_language
    with open(config_file, 'w', encoding="UTF-8") as platforms_file:
      dump(configuration, platforms_file, indent=4)
    run_command = path.join(path.dirname(__file__), "util", "memory_usage.exe " if machine == "win32" else "./memory_usage.exe ")
    run_command += f" {'./' if machine != 'win32' else ''}{outputPath}.exe {memory_limit} {outputPath}_memory.out {inputPath} {outputPath}.out {sample_id}" + (execute_command.replace("{output}", outputPath))
    run(run_command, shell=True, check=True)
 
  run(execute_command.replace("{input_file}", inputPath).replace("{output_file}", outputPath), shell=True, check=True)
