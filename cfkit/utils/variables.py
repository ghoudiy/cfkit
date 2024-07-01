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
  INPUT_EXTENSION_FILE = "txt"
  OUTPUT_EXTENSION_FILE = "txt"
else:
  # config_folder = Path("~").expanduser().joinpath(".config", "cfkit")
  INPUT_EXTENSION_FILE = "in"
  OUTPUT_EXTENSION_FILE = "out"

OUTPUT_FILENAME = "%%problem_code%%_test_case%%test_case_num%%." + OUTPUT_EXTENSION_FILE

ERRORS_MEMORY_TIME_FILENAME = (
  "%%problem_code%%_test_case%%test_case_num%%_err_memory_time." + OUTPUT_EXTENSION_FILE
)
# -------------------------------------------------------------------------

json_folder = Path(__file__).parent.parent.joinpath("json")

template_folder = config_folder.joinpath("templates")

language_conf_path = config_folder.joinpath("languages.json")

conf_file = ConfigParser()

conf_file.read(config_folder.joinpath("cfkit.conf"))

color_conf = ConfigParser()

color_conf.read(config_folder.joinpath("colorschemes", conf_file["cfkit"]["color_scheme"]))

resources_folder = config_folder.joinpath("resources")
