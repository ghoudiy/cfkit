"""
Documentation
"""

# Standard Library Imports
from sys import platform
from pathlib import Path
from configparser import ConfigParser

MACHINE = platform

# -------------------------------------------------------------------------
# Editable
config_folder = Path("~").expanduser().joinpath(".cfkit")
if MACHINE == "win32":

  # config_folder = Path("~").expanduser().joinpath("AppData", "Roaming", "cfkit")
  input_extension_file = "txt"
  output_extension_file = "txt"
else:
  # config_folder = Path("~").expanduser().joinpath(".config", "cfkit")
  input_extension_file = "in"
  output_extension_file = "out"

output_filename = "%%problem_code%%_test_case%%test_case_num%%." + output_extension_file

errors_memory_time_filename = "%%problem_code%%_test_case%%test_case_num%%_err_memory_time." + output_extension_file
# -------------------------------------------------------------------------

json_folder = Path(__file__).parent.parent.joinpath("json")

template_folder = config_folder.joinpath("templates")

language_conf_path = config_folder.joinpath("languages.json")

conf_file = ConfigParser()

conf_file.read(config_folder.joinpath("cfkit.conf"))

color_conf = ConfigParser()

color_conf.read(config_folder.joinpath("colorschemes", conf_file["cfkit"]["color_scheme"]))

resources_folder = config_folder.joinpath("resources")
