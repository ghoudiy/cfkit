from colorama import init, Fore, Style, Back


init()

# Available styles
dim    = Style.DIM
bright = Style.BRIGHT


# Available text colors

# Base colors
black   = Fore.BLACK
red     = Fore.RED
green   = Fore.GREEN
yellow  = Fore.YELLOW
blue    = Fore.BLUE
magenta = Fore.MAGENTA
cyan    = Fore.CYAN
white   = Fore.WHITE

# Light colors
light_black   = Fore.LIGHTBLACK_EX
light_red     = Fore.LIGHTRED_EX
light_green   = Fore.LIGHTGREEN_EX
light_yellow  = Fore.LIGHTYELLOW_EX
light_blue    = Fore.LIGHTBLUE_EX
light_magenta = Fore.LIGHTMAGENTA_EX
light_cyan    = Fore.LIGHTCYAN_EX
light_white   = Fore.LIGHTWHITE_EX

# Dim colors
dim_black   = black   + dim
dim_red     = red     + dim
dim_green   = green   + dim
dim_yellow  = yellow  + dim
dim_blue    = blue    + dim
dim_magenta = magenta + dim
dim_cyan    = cyan    + dim
dim_white   = white   + dim

# Bright colors
bright_black   = black   + bright
bright_red     = red     + bright
bright_green   = green   + bright
bright_yellow  = yellow  + bright
bright_blue    = blue    + bright
bright_magenta = magenta + bright
bright_cyan    = cyan    + bright
bright_white   = white   + bright

# Bright and light colors
bright_light_black   = light_black   + bright
bright_light_red     = light_red     + bright
bright_light_green   = light_green   + bright
bright_light_yellow  = light_yellow  + bright
bright_light_blue    = light_blue    + bright
bright_light_magenta = light_magenta + bright
bright_light_cyan    = light_cyan    + bright
bright_light_white   = light_white   + bright

# Configuration
color_configuration = {
  "accepted"            : bright_light_green,
  "wrong answer"        : light_red,
  "Compilation error"   : blue,
  "Runtime error"       : light_blue,
  "Memory limit error"  : light_yellow,
  "user input errors"   : light_magenta,
  "site errors"         : light_cyan,
  "configuration errors": light_magenta,
  "text"                : light_white
}
