from shutil import copy
from pathlib import Path
from platform import uname
from setuptools import setup, find_packages


with open("README.md", 'r', encoding="UTF-8") as file:
  long_description = file.read()

# package_data = {
#   "cfkit/json": ["src/cfkit/json/*.json"],
#   "docs": ["docs/*.md"],
#   "examples": ["examples/*.gif"],
#   '': ["README.md", "LICENSE.txt"],

# }
# var = uname()
# arch = var.machine
# operating_sys = var.system
# if arch == 'i386' or arch == 'i686':
#   if operating_sys == "darwin":
#     print("Unfortunately, memory and time tracking features are not supported on your current system configuration.")
#   else:
#     package_data["cfkit/dependencies"] = [f'cfkit/dependencies/memory_time_usage_{operating_sys}_386.exe', "cfkit/dependencies/memory_time_usage.go"]

# elif arch == 'x86_64':
#   package_data["cfkit/dependencies"] = [f'cfkit/dependencies/memory_time_usage_{operating_sys}_amd64.exe', "cfkit/dependencies/memory_time_usage.go"]

# elif arch.startswith('arm'):
#   if operating_sys != "linux":
#     print("Unfortunately, memory and time tracking features are not supported on your current system configuration.")
#   else:
#     package_data["cfkit/dependencies"] = [f'cfkit/dependencies/memory_time_usage_{operating_sys}_arm.exe', "cfkit/dependencies/memory_time_usage.go"]

# elif arch == 'aarch64':
#   package_data["cfkit/dependencies"] = [f'cfkit/dependencies/memory_time_usage_{operating_sys}_arm64.exe', "cfkit/dependencies/memory_time_usage.go"]

# else:
#   print("Unfortunately, memory and time tracking features are not supported on your current system configuration.")


setup(
  name='cfkit',
  version='0.0.1',
  author='Yassine Ghoudi',
  author_email='ghoudi.dev@gmail.com',
  description='A simple Python CLI tool example',
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/ghoudiy/cfkit",
  license="MIT",
  packages=find_packages(where="src"),
  # package_data=package_data,
  include_package_data=True,
  python_requires=">=3.8",
  install_requires=[
    'requests',
    'MechanicalSoup',
    'beautifulsoup4',
    'prompt_toolkit'
  ],
  entry_points={
    'console_scripts': [
      'cf = cfkit.cmd.cli:main',
    ],
  },
  classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI cfkitroved :: MIT License',
    'Operating System :: OS Independent',
  ],
  keywords="CLI, Tool, Python"
)

source_dir = Path('data')
target_dir = Path.home() / '.cfkit_2'

if not target_dir.exists():
  target_dir.mkdir(parents=True)

for item in source_dir.rglob('*'):
  target_item = target_dir / item.relative_to(source_dir)
  if item.is_dir():
    target_item.mkdir(parents=True, exist_ok=True)
  else:
    copy(item, target_item)