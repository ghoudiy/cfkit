compiled_languages = {
  "GNU GCC C11": {
      "win32": "gcc.exe -fno-strict-aliasing -lm -s -Wl,--stack={stack_size} -O2 -o {output}.exe {file}",
      "linux": "gcc -fno-strict-aliasing -lm -s -O2 -o {output}.exe {file}",
      "darwin": "g++ -Wall -Wextra -Wconversion -O2 -std=c++20 -o {output}.exe {file}"
      },
  
  "Clang++20 Diagnostics": {
      "win32": "clang++ -Wall -Wextra -Wconversion -O2 -std=c++20 -Wl,-stack_size,{stack_size} -o {output}.exe {file}",
      "linux": "clang++ -Wall -Wextra -Wconversion -O2 -std=c++20 -o {output}.exe {file}",
      "darwin": "g++ -Wall -Wextra -Wconversion -O2 -std=c++20 -o {output}.exe {file}"},
  
  "Clang++17 Diagnostics": {
      "win32": "clang++ -Wall -Wextra -Wconversion -O2 -std=c++17 -Wl,-stack_size,{stack_size} -o {output}.exe {file}",
      "linux": "clang++ -Wall -Wextra -Wconversion -O2 -std=c++17 -o {output}.exe {file}",
      "darwin": "g++ -Wall -Wextra -Wconversion -O2 -std=c++20 -o {output}.exe {file}"},
  
  "GNU G++ 14": {
    "win32": "g++.exe -Wall -Wextra -Wconversion -Wl,--stack,{stack_size} -O2 -std=c++14 -o {output}.exe {file}",
    "linux": "g++ -Wall -Wextra -Wconversion -O2 -std=c++14 -o {output}.exe {file}",
    "darwin": "g++ -Wall -Wextra -Wconversion -O2 -std=c++20 -o {output}.exe {file}"
    },
  
  "GNU G++ 17": {
    "win32": "g++.exe -Wall -Wextra -Wconversion -Wl,--stack={stack_size} -O2 -std=c++17 -o {output}.exe {file}",
    "linux": "g++ -Wall -Wextra -Wconversion -O2 -std=c++17 -o {output}.exe {file}",
    "darwin": "g++ -Wall -Wextra -Wconversion -O2 -std=c++20 -o {output}.exe {file}",
    },
  
  "GNU G++ 20": {
    "win32": "g++.exe -Wall -Wextra -Wconversion -Wl,--stack={stack_size} -O2 -std=c++20 -o {output}.exe {file}",
    "linux": "g++ -Wall -Wextra -Wconversion -O2 -std=c++20 -o {output}.exe {file}",
    "darwin": "g++ -Wall -Wextra -Wconversion -O2 -std=c++20 -o {output}.exe {file}",
    },

  "Microsoft Visual Studio C++ 2017": {
      "win32": "cl /std:c++17 /W4 /F268435456 /EHsc /O2 /Fe:{output}.exe {file}",
      "linux": None,
      "darwin": None
      }, # To check if possible
  
  "C# .NET": {
      "win32": "csc.exe /o+ /out:{output}.exe {file}",
      "linux": None,
      "darwin": None
      }, # To check if possible

  "D": {
    "dmd": {
      "win32": "dmd -L/STACK:268435456 -O -release {file} -of={output}.exe",
      "linux": "dmd -O -release {file} -of={output}.exe",
      "darwin": "dmd -O -release {file} -of={output}.exe",}, # Working on

    "gdc": {
      "win32": "gdc -Wall -Wextra -Wl,-stack_size,{stack_size} -O2 -o {output}.exe {file}",
      "linux": "gdc -Wall -Wextra -O2 -o {output}.exe {file}",
      "darwin": "gdc -Wall -Wextra -O2 -o {output}.exe {file}"
    }},

  "OCaml ": {"XP": "ocamlopt nums.cmxa str.cmxa -pp camlp4o -o {output}.exe -ocaml {file}"},

  "Delphi": {
      "win32": "dcc -Q -$M1048576,67107839 -cc {file} && ren {file}.exe",
      "linux": None,
      "darwin": None
      },
  
  "Free Pascal": {
      "win32": "fpc -n -O2 -Xs -viwn -Cs67107839 -Mdelphi {file} -o {output}.exe",
      "linux": None,
      "darwin": None
      },

  "PascalABC.NET": {
      "win32": "pabcnetc {file} && ren {file}.exe {output}.exe && ren {file}.dpr {output}.dpr",
      "linux": None,
      "darwin": None
      },

  "Rust": {"XP": "rustc -C opt-level=2 -o {output}.exe filename.rs"},

}

executing_commands = {
 "win32": "{output}.exe < {input_file} > {output_file}", 
 "linux": "./{output}.exe < {input_file} > {output_file}",
 "darwin": "./{output}.exe < {input_file} > {output_file}",
}

interpreted_languages = {
  "PHP": {"php -n -d display_errors=On -d error_reporting=E_ALL {file} < {input_file} > {output_file}"}, # To check if possible
  
  "Python": {
      "win32": "python {file} < {input_file} > {output_file}",
      "linux": "python3 {file} < {input_file} > {output_file}",
      "darwin": "python3 {file} < {input_file} > {output_file}"},
  
  "Perl": "perl {file} < {input_file} > {output_file}", # To check if possible
  
  "Ruby": "ruby {file} < {input_file} > {output_file}", # To check if possible 
  
  "JavaScript 8": {None}, # Working on

  "Node.js": {"node {file} < {input_file} > {output_file}}"}, # Working on


}

one_line_compiled = {
  "C# Mono": {"XP": "mcs -o+ -out:{output}.exe {file} && mono {output}.exe"}, # Done (Have to check if it work on windows and macOs)
  
  "Go": {"go run {file}"}, # Working on
  
  "Haskell GHC": {"runghc {file}"}, # To check if possible

  "Java": {"XP": "java -Xmx512M -Xss64M -Duser.language=en -Duser.region=US -Duser.variant=US {file} < {input_file} > {output_file}"}, # Done (Have to check if it work on windows and macOs)

  "Kotlin": {"kotlinc {file} -include-runtime -d {output}.jar && java -jar {output}.jar"}, # To check if possible
  

  "Scala": {"scala {file}"}, # To check if possible

}

