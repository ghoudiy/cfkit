from prompt_toolkit import print_formatted_text, HTML
# from prompt_toolkit.styles import Style
# from prompt_toolkit.formatted_text import to_plain_text, to_formatted_text
# from prompt_toolkit import prompt
# from cfkit.utils.variables import color_conf
# from cfkit.utils.input import select_option
from cfkit.utils.print import colored_text
# print("Yassine" + HTML("<i>Ghoudi</i>"))
# style = Style([(key, value) for key, value in color_conf["theme"].items()])
# a = prompt(HTML("<error_4>Hello, World!</error_4>"), style=style)
# print(a)
# print(to_plain_text(colored_text("<red>I</red>. Please include the following placeholders in your command:",return_statement=True)))

# Example usage:
# formatted_text = color_text("Enter some data >", "ansigray")
# print(formatted_text)
# NOTE = """
# <red>II.</red> Do not include any input or output specifications in your command! (i.e. &apos;&lt; in &gt; out&apos;)
# """
# colored_text(NOTE)

COMPILING_NOTE = """\
<red>III.</red> When providing the compilation command, \
make sure to include the execution part as well if necessary.
For instance, if you&apos;re using Kotlin, your command should look something like this:

<command>kotlinc %%{file}%% -d %%{output}%%.jar &amp;&amp; java -jar %%{output}%%.jar</command>

The &apos;<command>&apos;&apos; java -jar %%{output}%%.jar</command>&apos; part is important for executing the compiled code.
If your compilation process requires additional steps for execution, \
be sure to include them in the command as well


There are two types of compilation commands:\n
1. Compile only: Compiles the code without executing.
    Example: g++ -Wall -o %%{output}%% %%{file}%%
2. Compile and Execute: Compiles and immediately executes the code.
    Example: go run %%{file}%%

Choose the appropriate command based on your needs."""
colored_text(COMPILING_NOTE)