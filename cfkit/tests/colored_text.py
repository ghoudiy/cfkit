from sys import exit as sysExit
from colorama import init
from colorama import Fore
from colorama import Back
from colorama import Style
from configparser import NoOptionError
from cfkit.utils.variables import color_conf
from re import reCompile


def colored_text(
    *message: object,
    one_color='',
    input_statement: bool = False,
    return_statement: bool = False,
    exit_code_after_print_statement: int = 0
  ) -> str | None:
  """
  Documentation
  """
  init(autoreset=True)

  def generate_color_code_from_components(part: str) -> str:
    ORDER = ["\x1b[", "s-bright", "s-dim", "light"]
    background = part.find("bg")
    if background != -1:
      bg_light_color = part.find("(") != -1
      if bg_light_color:
        background_color = part[background:].find("+") + len(part[:background])
        part = part[:background_color] + part[background_color+1:]
        bg_index = part[:background].count("+")
        part = part.replace(" ", '').split("+")
        part.insert(0, (part[bg_index][4:-1].upper() + "_EX"))
        part[0] = Back.__dict__.get(
              ("LIGHT" + part[0][:-8] + "_EX")
          if part[0][-8:] == "LIGHT_EX" else
              part[0].upper(), '')
        part[bg_index+1] = ""

      else:
        bg_index = part[:background].count("+")
        part = part.replace(" ", '').split("+")
        part.insert(0, part[bg_index][3:].upper())
        part[0] = Back.__dict__.get(part[0].upper(), '')
        part[bg_index+1] = ""

    else:
      part = part.replace(" ", '').split("+")

    components = [None] * 4
    for style in part:
      i = 0
      test = False
      while not test and i < 4:
        test = style[:2] == ORDER[i][:2]
        i += 1
      if not test:
        components.append(style)
      else:
        components[i-1] = style

    colors = ""
    components = filter(bool, components)
    light = False
    for style in components:
      if style == "light":
        light = True
      if style[0] == 's':
        color = Style.__dict__.get(style[2:].upper(), '')
      else:
        style = f"LIGHT{style.upper()}_EX" if light else style
        color = Fore.__dict__.get(style.upper(), style if style[:2] == "\x1b[" else '')
      colors += color
    return colors

  message = " ".join(map(str, message))

  if one_color:
    try:
      pos_color = one_color.find("color=")
      if pos_color != -1:
        one_color = one_color[6:]
      else:
        one_color = color_conf.get("theme", one_color.replace(" ", "_"))
      message = generate_color_code_from_components(one_color) + message + Style.RESET_ALL
    except NoOptionError:
      pass
  else:
    color_pattern = reCompile(r'<(\w{5,}|/)>')
    # Split the message using the color tags as delimiters
    def replace(match):
      color_key = match.group(1)
      if color_key == "/":
        return Style.RESET_ALL
      pos_color = color_key.find("color_")
      if pos_color != -1:
        color_value = color_key[6:]
      else:
        color_value = color_conf.get('theme', color_key)

      return generate_color_code_from_components(color_value)
    message = color_pattern.sub(replace, message)

  if return_statement:
    return message

  elif input_statement:
    return input(message).strip()

  elif exit_code_after_print_statement == 0:
    print(message)

  else:
    print(message)
    sysExit(exit_code_after_print_statement)
exit