"""
Documentation
"""

from pathlib import Path
from typing import TypeAlias


Directory: TypeAlias = Path

PROBLEM_CODE_PATTERN = r"\A[1-9]{1}\d{,3}[A-z]\d{,2}"

NOTE = """
<red>II.</red> Do not include any input or output specifications in your command! (i.e. &apos;&lt; in &gt; out&apos;)
"""

COMPILING_NOTE = """\
<red>III.</red> When providing the compilation command, \
make sure to include the execution part as well if necessary.
For instance, if you&apos;re using Kotlin, your command should look something like this:

<command>kotlinc %%{file}%% -d %%{output}%%.jar &amp;&amp; java -jar %%{output}%%.jar</command>

The &apos;<command>&amp;&amp; java -jar %%{output}%%.jar</command>&apos; part is important for executing the compiled code.
If your compilation process requires additional steps for execution, \
be sure to include them in the command as well


There are two types of compilation commands:\n
1. Compile only: Compiles the code without executing.
    Example: g++ -Wall -o %%{output}%% %%{file}%%
2. Compile and Execute: Compiles and immediately executes the code.
    Example: go run %%{file}%%

Choose the appropriate command based on your needs."""

HELP_MESSAGE = """
Available commands:

    list    list all problems of the contest
    parse   parse input and output samples from problem statement
    gen     generate solution file with the default template if found
    run     test solution file against samples and print the verdict response

Type cf <command> --help for usage help on a specific command.
For example, cf run --help will list all testing options.
"""

EXTENSIONS = {
  "c": "C",
  "cpp": "C++",
  "cxx": "C++",
  "C": "C++",
  "cc": "C++",
  "c++": "C++",
  "cs": "C#",
  "d": "D",
  "go": "Go",
  "hs": "Haskell",
  "java": "Java",
  "kt": "Kotlin",
  "ml": "OCaml",
  "dpr": "Delphi",
  "pas": "Pascal",
  "pl": "Perl",
  "php": "PHP",
  "py": "Python",
  "rb": "Ruby",
  "rs": "Rust",
  "scala": "Scala",
  "js": "JavaScript"
}

LANGUAGES = [
  'C',
  'C++',
  'C#',
  'D',
  'Go',
  'Haskell',
  'Java',
  'Kotlin',
  'OCaml',
  'Delphi',
  'Pascal',
  'Perl',
  'PHP',
  'Python',
  'Ruby',
  'Rust',
  'Scala',
  'JavaScript'
]

LANGUAGES_EXTENSIONS = {
  'C': ['c'],
  'C++': ['cpp', 'cxx', 'C', 'cc', 'c++'],
  'C#': ['cs'],
  'D': ['d'],
  'Go': ['go'],
  'Haskell': ['hs'],
  'Java': ['java'],
  'Kotlin': ['kt'],
  'OCaml': ['ml'],
  'Delphi': ['dpr'],
  'Pascal': ['pas'],
  'Perl': ['pl'],
  'PHP': ['php'],
  'Python': ['py'],
  'Ruby': ['rb'],
  'Rust': ['rs'],
  'Scala': ['scala'],
  'JavaScript': ['js']
}

ALL_ACTIONS = (
  "list", 
  "parse", 
  "gen", 
  "run",
  "config"
)