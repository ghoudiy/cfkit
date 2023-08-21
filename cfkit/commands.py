from os import chdir, path
from sys import exit as sysExit, maxsize
from json import load, dump, dumps
from time import sleep
from subprocess import run
from cfkit.util.util import machine


execute_commands = {
 "win32": "{output}.exe < {input_file} > {output_file}", 
 "linux": "./{output}.out < {input_file} > {output_file}",
 "darwin": "./{output}.out < {input_file} > {output_file}",
}


def add_execute_command(dictionary):
  for key, value in dictionary.items():
    if isinstance(value, str):
      dictionary[key] = f"{value} && {execute_commands[machine]}"
    elif isinstance(value, dict):
      add_execute_command(value)
  return dictionary


def read_file(x):
  with open(x, 'r', encoding="UTF-8") as file:
    return load(file)


chdir(path.join(path.abspath(path.dirname(__file__)), "json"))
extensions: dict = read_file("extensions.json")
compilers_interpreters: dict = read_file("compilers_interpreters.json")
compiling_commands: dict = add_execute_command(read_file("compiling_commands.json"))
one_line_compiled: dict = read_file("one_line_compiled.json")
interpreting_commands: dict = read_file("interpreting_commands.json")

# print(dumps(add_execute_command(compiling_commands), indent=4))
# print(dumps(compiling_commands, indent=4))
# exit()
note = """
\nNote: When providing the compilation command, \
please make sure to include the execution part as well if necessary.\n\
For instance, if you're using Kotlin, your command should look something like this:\n\
\nkotlinc {file} -d {output}.jar && java -jar {output}.jar\n\n\
The '&& java -jar {output}.jar' part is important for executing the compiled code.\n\
If your compilation process requires additional steps for execution, \
be sure to include them in the command as well. Thank you!\n
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


  def check_installed_compilers(L):
    i = -1
    ok = False
    R = [False] * len(L)
    while not ok and i < len(L) - 1:
      i += 1
      R[i] = language(L[i])
    return R


  def identify_implementation(lang):
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

        # C++ is notably exceptional in this situation
        # as it remains compatible with both the g++ and gcc compilers
        # within the GCC compiler group.
        if isinstance(value, list):
          compilers_list[key] = check_installed_compilers(value)

          if compilers_list[key][0]:
            compilers_list[key] = True

          elif not compilers_list[key][0] and compilers_list[key][1]:
            if machine == "win32":
              return "gcc -Wall -Wextra -Wconversion -fno-strict-aliasing -lm -s -Wl,--stack=268435456 -O2 -o {output}.exe {file} -lstdc++" + f" && {execute_commands['win32']}"

            return "gcc -Wall -Wextra -Wconversion -fno-strict-aliasing -lm -s -O2 -o {output}.exe {file} -lstdc++" + f" && {execute_commands[machine]}"

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
          def not_a_command(x, func):
            return func(list(x.keys()), ["win32", "linux", "darwin"]) if isinstance(x, dict) \
                else False
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

            c = int(input("Please choose carefully, as your selection will become the default option for future use\nCompiler index: "))
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

  command = identify_implementation(programming_language)
  if command:
     # Add executing command to compiling command and save command to config file
    return command
  
  implementation = 'compiler' if programming_language in compiling_commands or programming_language in one_line_compiled else 'interpreter'
  print(f"\nOops! The desired {implementation} is not installed on the system or it may be not added to the PATH")

  L = ["Please include the following placeholders in your command:",
        "- {file}: This represents the path to the script file.",
        "Your command might look like this:",
        "interpreting-command [options...] {file}"
      ]
  
  if implementation == 'compiler':
    L.insert(2, "- {output}: This represents the compiled code.",)
    L[-1] =  f"compiler-command [options...] {{file}} -o {{output}}.{'exe' if machine == 'win32' else 'out'}"
    print(note)

  print("\n".join(L))
  return input("\nPlease enter below the command you'd like to use:\n") + " < {input_file} > {output_file}"


def get_command(file: str, inputPath, outputPath):
  extension = file[file.rfind('.')+1:]
  if extension == file:
    print("Please add the appropriate file extension to the file name. This ensures accurate language identification.")
    sysExit(1)

  platform = "codeforces.com" # Codeforces only for now
  # config_file = path.join(path.expanduser("~", "AppData\Local" if machine == "win32" else ".config", "cfkit", "config"))
  config_file = path.join(path.dirname(__file__), "config_folder", "platform.json")
  configuration = read_file(config_file)
  execute_command = configuration[platform]["execute_command"]
  if execute_command == None:
    if extension not in extensions:
      print("Oops! The desired language is not supported on Codeforces.")
      sysExit(1)

    programming_language = extensions[extension]
    command = detect_implementation(programming_language)
    configuration[platform]["execute_command"] = command
    configuration[platform]["default_language"] = programming_language
    with open(config_file, 'w') as file:
      dump(configuration, file, indent=4)
    return command.replace("{input_file}", inputPath).replace("{output_file}", outputPath)
  else:
    return execute_command.replace("{input_file}", inputPath).replace("{output_file}", outputPath)

if __name__ == "__main__":
  from time import sleep
  hello = path.join(path.dirname(__file__), "config_folder", "platform.json")
  copie = read_file(hello)
  my_dict = {
    "c": "C",
    "cpp": "C++",
    "cs": "C#",
    "d": "D",
    "go": "Go",
    "hs": "Haskell GHC",
    "java": "Java",
    "kt": "Kotlin",
    "ml": "OCaml",
    "dpr": "Delphi 7",
    "pas": "Pascal",
    "pl": "Perl",
    "php": "PHP",
    "py": "Python",
    "rb": "Ruby",
    "rs": "Rust",
    "scala": "Scala",
    "js": "JavaScript"
  }
  for ext in extensions:
    print("-" * 50)
    print(f"Language = {extensions[ext]}")
    print(f"extension = {ext}")
    print(get_command(f"test.{ext}", "in", "out"))
    sleep(5)
    with open(hello, 'w') as file:
      dump(copie, file, indent=4)
  