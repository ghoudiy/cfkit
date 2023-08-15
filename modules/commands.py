import sys
import os
from json import load
from subprocess import run

def read_json_file(x):
  with open(f"{x}.json", 'r') as file:
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


def compiler(file: str, stack_size: int):
  language = lambda command: run(command, capture_output=True, shell=True, text=True).returncode == 0

  def check(L):
    i = -1
    ok = False
    R = [False] * len(L)
    while not ok and i < len(L) - 1:
      i += 1
      R[i] = language(L[i])
    return R

  def select_compiler(lang):
    compiler_check_version_command = compilers_interpreters[lang]
    ans = type(compiler_check_version_command)
    
    if ans == str: # If there is only one command of execution
      if lang == "Delphi 7":
        
        if sys.maxsize > 4294967296:
          ok = language(compiler_check_version_command.replace("{architecture}", "64")) or language(compiler_check_version_command.replace("{architecture}", "32"))
        else:
          ok = language(compiler_check_version_command.replace("{architecture}", "32"))

      else:
        ok = language(compiler_check_version_command)
      if ok:
        if lang in interpreting_commands:
          return interpreting_commands[lang]
        elif lang in compiling_commands:
          return compiling_commands[lang][machine]
        else:
          return one_line_compiled[lang]

      return None
    
    # Python only for now
    elif ans == list: # Done
      tmp = check(compiler_check_version_command)
      if any(tmp):
        tmp = compiler_check_version_command[tmp.index(True)]
        return interpreting_commands[lang].replace("{command}", tmp[:tmp.find(" ")])
      else:
        return None
      
    elif ans == dict:
      compilers_list = {}
      for key, value in compiler_check_version_command.items():
        # G++ and GCC
        if type(value) == list: # Done
          compilers_list[key] = check(value) # key: GNU G++, value = g++ --version or gcc --version

          if compilers_list[key][0]:
            compilers_list[key] = True
    
          elif not compilers_list[key][0] and compilers_list[key][1]:
            if machine == "win32":
              return "gcc -Wall -Wextra -Wconversion -fno-strict-aliasing -lm -s -Wl,--stack={stack_size} -O2 -o {output}.exe {file} -lstdc++"
            elif machine == "linux" or machine == "darwin":
              return "gcc -Wall -Wextra -Wconversion -fno-strict-aliasing -lm -s -O2 -o {output}.exe {file} -lstdc++"
          
          elif not (compilers_list[key][0] and compilers_list[key][1]):
            return None

        elif type(value) == str:
          compilers_list[key] = language(value)

      # TEMP
      for key in compilers_list.keys():
        compilers_list[key] = True

      for key in [key for key, value in compilers_list.items() if not value]:
        del compilers_list[key]

      compilers_list = compilers_list.keys()
      l = len(compilers_list)
      if l:
        def choose_compiler(K: dict):
          tmp = K[lang]
          not_a_command = lambda x: list(x.keys()) != ["win32", "linux", "darwin"] if type(x) == dict else False
          if l > 1 or (l == 1 and not_a_command(tmp)):
            print("Multiple compilers are available for the given file:")

            compilers = []
            for compi in compilers_list:
              compile_command = K[lang][compi]
              aux = not_a_command(compile_command)

              if type(compile_command) == dict and aux:
                for key in compile_command.keys():
                  compilers.append((compi, key))
                  print(f"{len(compilers)}. {key}")
              
              else:
                print(compile_command)
                compilers.append((K[lang][compi], None))
                print(f"{len(compilers)}. {compi}")

            print("-" * 50)
            print(f"{compilers = }")
            exit()
            c = int(input("Please choose carefully, as your selection will become the default option for future use\nCompiler index: "))
            while c not in range(1, len(compilers) + 1):
              c = int(input("Compiler index: "))
            print(compilers[c-1])
            com = compilers[c-1][1] == None
            if com: return K[lang][compilers[c-1][0]][compilers[c-1][1]][machine]
            else: return compilers[c-1][0]
          
          elif l:
            if machine in tmp:
              return tmp[machine]
            return tmp
      
        K = {lang: {}}
        for x in compilers_list:
          if lang in compiling_commands and x in compiling_commands[lang]:
            K[lang].update(compiling_commands[lang])
          elif lang in one_line_compiled and x in one_line_compiled[lang]:
            K[lang].update(one_line_compiled[lang])
          else:
            K[lang].update(interpreting_commands[lang])

        return choose_compiler(K)

      else:
        return None
  

  p = file.rfind(".")
  machine = sys.platform
  if p == -1:
    print("Please add the appropriate file extension to the file name. This ensures accurate language identification.")
    sys.exit(1)
  
  else: 
    ext = file[file.rfind(".")+1:]
    lang = extensions[ext]
    aux = select_compiler(lang)
    if aux:
      return aux
    else:
      print("Oops! The desired compiler is not installed on the system or it may be not added to the PATH")
      # prompt and add a command and a compiler



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
# for x in my_dict.keys():
#   print('-' * 50)
#   print(extensions[x])
#   print(compiler(f"test.{x}"))


# print(compiler("test.cpp"))
# print(compiler("test.cs"))
print(compiler("test.d"))
# print(compiler("test.dpr"))

# print(compiler("test.py"))
# print(compiler("test.js"))


# interpreter = lambda x: run(f"{command} {x} < {self.__Li[i]} > {test_case}", shell=True) if False else None