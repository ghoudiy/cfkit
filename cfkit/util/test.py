# import re
from colorama import init, Fore, Style, Back

# init()

# color_mapping = {
#     "black": Fore.BLACK,
#     "red": Fore.RED,
#     "green": Fore.GREEN,
#     "yellow": Fore.YELLOW,
#     "blue": Fore.BLUE,
#     "magenta": Fore.MAGENTA,
#     "cyan": Fore.CYAN,
#     "white": Fore.WHITE,
# }

# def colorize_text(message):
#   # Define a regular expression pattern to match color tags like <blue> and </blue>
#   color_pattern = re.compile(r'<(.*?)>')

#   # Split the message using the color tags as delimiters
#   parts = color_pattern.split(message)

#   s = ""
#   for part in parts:
#     if part.startswith('/'):
#       color = Style.RESET_ALL
#     else:
#       color = color_mapping.get(part.lower())
#     s += color if color is not None else part
#   print(s)

# message = "Please run <blue>'cf config'</blue> in order to add favorite language"
# colorize_text(message)
init(autoreset=True)
def plus_color(message):
  return Fore.BLACK + Style.BRIGHT + Back.RED +  message

print(plus_color("hello"))
print("Hey")