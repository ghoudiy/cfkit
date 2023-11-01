from pathlib import Path

my_path = Path("/home/ghoudiy")
print(list(filter(lambda x: x[0] != "_", dir(my_path))))
help(my_path.as_uri)