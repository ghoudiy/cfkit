# from pathlib import Path

# my_path = Path("/home/ghoudiy")
# print(list(filter(lambda x: x[0] != "_", dir(my_path))))
# help(my_path.as_uri)

from cfkit.util.common import select_option
file_or_dir = "file"

user_choice = select_option(
  message="What do you want to do?",
  data=[
    "Write in the same directory" if file_or_dir == "directory" else "Override the file",
    f"Replace the old {file_or_dir} with the new one",
    f"Create a new {file_or_dir} with another name",
    "Abort"
  ],
  index=True,
  use_shortcuts=True
)
print(user_choice+1)