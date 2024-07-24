from setuptools import setup, find_packages

setup(
  name="cfkit",
  version="0.0.17",
  author="Yassine Ghoudi",
  author_email="ghoudi.dev@gmail.com",
  description="A tool for managing coding competitions.",
  long_description=open("README.md").read(),
  long_description_content_type="text/markdown",
  url="https://github.com/ghoudiy/cfkit",
  project_urls={
    "Issues": "https://github.com/ghoudiy/cfkit/issues",
  },
  package_dir={"": "src"},
  packages=find_packages(where="src"),
  include_package_data=True,
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_requires=">=3.8",
  install_requires=[
    "requests>=2.25.1",
    "MechanicalSoup>=1.3.0",
    "beautifulsoup4>=4.10.0",
    "prompt_toolkit>=3.0.36"
  ],
  entry_points={
    "console_scripts": [
      "cf=cfkit._cmd.cli:main",
    ],
  },
  license_files=("LICENSE.txt",),
  keywords=["CLI", "Python", "competition", "management"],
)
