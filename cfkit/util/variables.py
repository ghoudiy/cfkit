"""
Documentation
"""

# Standard Library Imports
from sys import platform
from pathlib import Path
from configparser import ConfigParser
from typing import TypeAlias

# Cfkit Imports
from cfkit.util.constants import MACHINE


json_folder = Path(__file__).parent.parent.joinpath("json")

config_folder = Path("~").expanduser().joinpath((

  "AppData", "Roaming") if MACHINE == "win32" else ".config", "cfkit")

template_folder = config_folder.joinpath("templates")

language_conf_path = config_folder.joinpath("languages.json")

conf_file = ConfigParser()

conf_file.read(config_folder.joinpath("cfkit.conf"))

color_conf = ConfigParser()

color_conf.read(config_folder.joinpath("colorschemes", conf_file["cfkit"]["color_scheme"]))

resources_folder = config_folder.joinpath("resources")
