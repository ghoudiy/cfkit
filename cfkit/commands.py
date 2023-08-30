from sys import executable
from os import chdir, path
from sys import exit as sysExit, maxsize
from json import load, dump
from subprocess import run
from cfkit.util.util import confirm, check_command, enter_number, machine, config_file


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
make sure to include the execution part as well if necessary.
For instance, if you're using Kotlin, your command should look something like this:
\nkotlinc {file} -d {output}.jar && java -jar {output}.jar\n
The '&& java -jar {output}.jar' part is important for executing the compiled code.
If your compilation process requires additional steps for execution, \
be sure to include them in the command as well.

"""
ANOTERH_NOTE = """
{num}. Do not include any input or output specifications in your command!

{num1}. Please choose carefully, as your selection will become the default option for future use. Thank you!
"""

COMPILING_NOTE = """
There are two types of compilation commands:\n
1. Compile only: Compiles the code without executing.
    Example: g++ -Wall -o {output} {file}
2. Compile and Execute: Compiles and immediately executes the code.
    Example: go run {file}
Choose the appropriate command based on your needs.
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
          command = compiling_commands[lang].replace("{architecture}", "64")

        if not ok or not command:
          command = compiling_commands[lang].replace("{architecture}", "32") \
            if language(check_version_compiler_command.replace("{architecture}", "32")) else None

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

      if not language(check_version_compiler_command):
        print(f"Oops! {lang} {implementation_command[1]} ({check_version_compiler_command[:check_version_compiler_command.find(' ')]}) used in Codeforces isnt't available on your system.")
        implementation_command = None, implementation_command[1]

    elif isinstance(check_version_compiler_command, list): # Python only for now
      tmp = check_installed_implemenations(check_version_compiler_command)
      if any(tmp):
        tmp = check_version_compiler_command[tmp.index(True)]
        implementation_command = interpreting_commands[lang].replace \
          ("{command}", tmp[:tmp.find(" ")]), "interpreter"

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
              return "gcc -Wall -Wextra -Wconversion -fno-strict-aliasing -lm -s -Wl,--stack=268435456 -O2 -o {output}.exe {file} -lstdc++", "compiler"

            return "gcc -Wall -Wextra -Wconversion -fno-strict-aliasing -lm -s -O2 -o {output}.exe {file} -lstdc++", "compiler"

          elif not (implementation_lists[key][0] and implementation_lists[key][1]):
            return None, "compiler"

        elif isinstance(value, str):
          implementation_lists[key] = language(value)
          if lang == "JavaScript":
            implementation = "interpreters"
      for key in implementation_lists.keys():
        implementation_lists[key] = True

      implementation_lists[".NET"] = False
      for key in [key for key, value in implementation_lists.items() if not value]:
        del implementation_lists[key]
 
      implementation_lists = implementation_lists.keys()
      l = len(implementation_lists)
      if l:
        def select_implementation(K: dict):
          def has_versions(x, deep=True) -> bool:
            if isinstance(x, dict):
              value = list(x.values())[0]
              if deep:
                return isinstance(list(value.values())[0], dict) if isinstance(value, dict) else False
              return isinstance(value, dict)
            return False

          if l > 1 or (l == 1 and has_versions(K)):
            print("Multiple compilers are available for the given file:")

            compilers = []
            for implementation in implementation_lists:
              compile_command = K[implementation]

              if has_versions(compile_command, False): # Compiler had multiple versions such as GNU G++, Clang++
                for compi in compile_command.keys():
                  compilers.append((implementation, compi))
                  print(f"{len(compilers)}. {compi}")

              else: # K[implementation] == command
                compilers.append((K[implementation], (implementation,)))
                print(f"{len(compilers)}. {implementation}")

            c = enter_number("Please choose carefully, as your selection will become the default option for future use\nCompiler index: ", "Compiler index: ", range(1, len(compilers) + 1)) - 1

            com = isinstance(compilers[c][1], tuple)
            if com:
              aux = compilers[c][0]
              if compilers[c][1][0] == "PascalABC.NET":
                selected_implementation = change_rename_command(aux)
              else:
                if machine in aux:
                  selected_implementation = aux[machine]
                else:
                  selected_implementation = aux
            else:
              selected_implementation = K[compilers[c][0]][compilers[c][1]][machine]
            return selected_implementation


          elif l:
            key = list(K.keys())[0]
            if machine in K[key]:
              selected_implementation = K[key][machine]
            else:
              selected_implementation = K[key]

          return selected_implementation

        K = {}
        implementation = "compiler"
        for x in implementation_lists:
          if lang in compiling_commands and x in compiling_commands[lang]:
            K.update({x: compiling_commands[lang][x]})
          elif lang in one_line_compiled and x in one_line_compiled[lang]:
            K.update({x: one_line_compiled[lang][x]})
          else:
            K.update({x: interpreting_commands[lang][x]})
            implementation = "interpreter"
        
        implementation_command = select_implementation(K)
        if len(K) == 1 and x == "Mono" or implementation_command == one_line_compiled["C#"]["Mono"]:
          implementation_command = implementation_command, "compile and execute"
        else:
          implementation_command = implementation_command, implementation
      else:
        compilers_interpreters[lang] = list(compilers_interpreters[lang].keys())
        statement = f"{(', '.join(compilers_interpreters[lang][:-2]))} {compilers_interpreters[lang][-2]} and {compilers_interpreters[lang][-1]} {implementation}".lstrip()
        print(f"Oops! {statement} that are used in Codeforces aren't available on your system.",)
        implementation_command = None, implementation[:-1]

    return implementation_command

  command, implementation = get_command(programming_language)
  if command:
     # Add executing command to compiling command and save command to config file
    return command, implementation

  if programming_language == "Python":
    return executable, "interpreter"

  L = ["Please include the following placeholders in your command:",
        "- {file}: This represents the path to the script file.",
        "Your command might look like this:",
        "interpreting-command [options...] {file}"
      ]

  if implementation in ("compiler", "compile and execute"):
    L.insert(2, "- {output}: This represents the compiled code. (Without .exe or .out)",)
    L[-1] =  f"compile-command [options...] {{file}} -o {{output}}"
    print("\n\n" + "\n".join(L))
    print(NOTE)
    print(ANOTERH_NOTE.replace("{num}", "2").replace("{num1}", "3"))
    print(COMPILING_NOTE)
    c = enter_number("Compilation type index: ", "Compilation type index: ", range(1, 3))
    if c == 1:
      implementation = "compiler"
    else:
      implementation = "compile and execute"
  else:
    print("\n\n" + "\n".join(L))
    print("\nPlease choose carefully, as your selection will become the default option for future use. Thank you!")
  
  command = check_command(input("Enter below the command you'd like to use:\n"), L)
  return confirm(command, "command", L), implementation


def execute_file(file: str, inputPath: str, outputPath: str, memory_limit: float, sample_id) -> None:
  extension = file[file.rfind('.')+1:]
  if extension == file:
    print("\nPlease add the appropriate file extension to the file name. This ensures accurate language identification.")
    sysExit(1)

  configuration = read_file(config_file)
  execute_command = configuration["execute_command"]
  if execute_command is None:
    if extension not in extensions:
      print("Oops! The desired language is not supported on Codeforces.")
      sysExit(1)

    run_command = path.join(path.dirname(__file__), "util", "memory_usage.exe " if machine == "win32" else "./memory_usage.exe")
    programming_language = extensions[extension]
    execute_command, implementation = detect_implementation(programming_language)
    if implementation == "compiler":
      run_command += f" {'./' if machine != 'win32' else ''}%%{{output}}%%.exe %%{{memory_limit}}%% %%{{output_memory}}_memory.out%% %%{{input_file}}%% %%{{output_file}}%% \"%%{{sample_id}}%%\"" + execute_command
    else:
      run_command += f" {'./' if machine != 'win32' else ''}\"{execute_command}\" %%{{memory_limit}}%% %%{{output_memory}}_memory.out%% %%{{input_file}}%% %%{{output_file}}%% \"%%{{sample_id}}%%\""
    configuration["execute_command"] = execute_command
    configuration["default_language"] = programming_language
    with open(config_file, 'w', encoding="UTF-8") as platforms_file:
      dump(configuration, platforms_file, indent=4)

  else:
    run_command += f" {'./' if machine != 'win32' else ''}%%{{output}}%%.exe %%{{memory_limit}}%% %%{{output_memory}}_memory.out%% %%{inputPath}%% {outputPath} \"{sample_id}\"" + execute_command
    output = inputPath[:inputPath.find("_")]
  # run(run_command, shell=True, check=True)
  # print(run_command)
  return None

pp = "/home/ghoudiy/Documents/Programming/Python/CP/Codeforces/B_Problems"
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
for ext in my_dict:
  print("=" * 50)
  execute_file(f"{pp}/200B_Drinks.{ext}", f"{pp}/tests/200B_1.in", f"{pp}/tests/200B_1_test_case.out", 256000000, "test 1")