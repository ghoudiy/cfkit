"""
Documentation
"""

# Standard Library Imports
from sys import platform
from pathlib import Path
from configparser import ConfigParser

MACHINE = platform

# All these variables are editable (only the %%test_case_num%% placeholder is required)
# -------------------------------------------------------------------------
config_folder = Path.home().joinpath(".cfkit")

if MACHINE == "win32":
  INPUT_EXTENSION_FILE = "txt"
  OUTPUT_EXTENSION_FILE = "txt"

  INPUT_FILENAME = "%%problem_code%%_%%test_case_num%%.in." + INPUT_EXTENSION_FILE
  INPUT_FILENAME_PATTERN = r"%%problem_code%%_\d+\.in\." + INPUT_EXTENSION_FILE

  EXPECTED_OUTPUT_FILENAME = "%%problem_code%%_%%test_case_num%%.out." + OUTPUT_EXTENSION_FILE
  EXPECTED_OUTPUT_FILENAME_PATTERN = r"%%problem_code%%_\d+\.out\." + OUTPUT_EXTENSION_FILE

  SHORT_INPUT_FILENAME = "in%%test_case_num%%." + INPUT_EXTENSION_FILE
  SHORT_EXPECTED_OUTPUT_FILENAME = "out%%test_case_num%%." + OUTPUT_EXTENSION_FILE

  # If you change the filename of the custom input/output, please also update the pattern accordingly
  CUSTOM_INPUT_FILENAME = "in%%test_case_num%%." + INPUT_EXTENSION_FILE
  CUSTOM_OUTPUT_FILENAME = "out%%test_case_num%%." + OUTPUT_EXTENSION_FILE

  CUSTOM_INPUT_FILENAME_PATTERN = r"in\d{0,}\." + INPUT_EXTENSION_FILE
  CUSTOM_OUTPUT_FILENAME_PATTERN = r"out\d{0,}\." + OUTPUT_EXTENSION_FILE

else:
  INPUT_EXTENSION_FILE = "in"
  OUTPUT_EXTENSION_FILE = "out"

  INPUT_FILENAME = "%%problem_code%%_%%test_case_num%%." + INPUT_EXTENSION_FILE
  INPUT_FILENAME_PATTERN = r"%%problem_code%%_\d+\." + INPUT_EXTENSION_FILE

  EXPECTED_OUTPUT_FILENAME = "%%problem_code%%_%%test_case_num%%." + OUTPUT_EXTENSION_FILE
  EXPECTED_OUTPUT_FILENAME_PATTERN = r"%%problem_code%%_\d+\." + OUTPUT_EXTENSION_FILE

  SHORT_INPUT_FILENAME = "%%test_case_num%%in"
  SHORT_EXPECTED_OUTPUT_FILENAME = "%%test_case_num%%out"

  # If you change the filename of the custom input/output, please also update the pattern accordingly
  CUSTOM_INPUT_FILENAME = "in%%test_case_num%%"
  CUSTOM_OUTPUT_FILENAME = "out%%test_case_num%%"

  CUSTOM_INPUT_FILENAME_PATTERN = r"in\d{0,}"
  CUSTOM_OUTPUT_FILENAME_PATTERN = r"out\d{0,}"


OUTPUT_FILENAME = "%%problem_code%%" + "_test_case" + "%%test_case_num%%." + OUTPUT_EXTENSION_FILE
OUTPUT_FILENAME_PATTERN = r"%%problem_code%%_test_case\d+\." + OUTPUT_EXTENSION_FILE

ERRORS_MEMORY_TIME_FILENAME = (
  "%%problem_code%%" + "_test_case" + "%%test_case_num%%" + "_err_memory_time." + OUTPUT_EXTENSION_FILE
)
ERRORS_MEMORY_TIME_FILENAME_PATTERN = r"%%problem_code%%_test_case\d+_err_memory_time\." + OUTPUT_EXTENSION_FILE
# -------------------------------------------------------------------------

json_folder = Path(__file__).parent.parent.joinpath("_json")

template_folder = config_folder.joinpath("templates")

language_conf_path = config_folder.joinpath("languages.json")

config_file_path = config_folder.joinpath("cfkit.conf")

conf_file = ConfigParser()

conf_file.read(config_file_path)

color_conf = ConfigParser()

color_conf.read(config_folder.joinpath("colorschemes", conf_file["cfkit"]["color_scheme"]))

resources_folder = config_folder.joinpath("resources")

history_file_path = resources_folder.joinpath("history.json")

# TEST_RESULT_TEXT_WITH_MEM_TIME_USAGE_AND_ANSWER = """
# Test case %%test_case_num%%, time: %%time%%, memory: %%memory%%, verdict: %%verdict%%
# Input
#  '-' * 55
# | %%input%% ' ' * %%columns_num%% - len(line) - 1 |
#  '-' * 55

# Output
#  '-' * 55
# | %%output%% ' ' * %%columns_num%% - len(line) - 1 |
#  '-' * 55

# Answer
#  '-' * 55
# | %%answer%% ' ' * %%columns_num%% - len(line) - 1 |
#  '-' * 55
# """

# TEST_RESULT_TEXT_WITH_MEM_TIME_USAGE_AND_ANSWER_CUSTOM = """
# Test case %%test_case_num%% (Custom '%%filename%%'), time: %%time%%, memory: %%memory%%, verdict: %%verdict%%
# Input
#  '-' * 55
# | %%input%% ' ' * %%columns_num%% - len(line) - 1 |
#  '-' * 55

# Output
#  '-' * 55
# | %%output%% ' ' * %%columns_num%% - len(line) - 1 |
#  '-' * 55

# Answer
#  '-' * 55
# | %%answer%% ' ' * %%columns_num%% - len(line) - 1 |
#  '-' * 55
# """

