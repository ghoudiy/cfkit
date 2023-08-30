# import os
# from re import search
# from shutil import rmtree
# from typing import TypeAlias

# from cfkit.util.util import check_path_existence, path_exist_error
# from cfkit.__main__ import Problem

# Directory: TypeAlias = str


# class Parse(Problem):

#   def extract(self, path: Directory = None, CreateTestsDir: bool = True, __check_path: bool = True):

#     if path is None:
#       path = os.getcwd()

#     elif path is not None and __check_path:
#       check_path_existence(path, 'd')

#     os.chdir(path)

#     if CreateTestsDir:

#       def create_new_dir(x):
#         os.mkdir(x)
#         return f"{x}"

#       if os.path.exists("tests"):
#         L = os.listdir("tests")
#         self._expected_output_list = sorted([file for file in L if search(rf"{self._code}_\d.out", file) is not None])
#         self._input_samples = sorted([file for file in L if search(rf"{self._code}_\d.in", file) is not None])
#         if len(self._expected_output_list) != len(self._input_samples):

#           c = input("Another folder with the same name already exists\n[W]rite in the same folder or [R]eplace the folder or [C]reate a new one with another name? ").lower()
#           while c not in ('w', 'r', 'c'):
#             c = input("[W]rite/[R]eplace/[C]reate]").lower()

#           if c == 'r':
#             rmtree(os.path.join(path, "tests"))
#             self._data_path = create_new_dir("tests")

#           elif c == 'c':
#             name = input("Folder name: ")
#             path_exist_error(name, "d")
#             self._data_path = create_new_dir(name)

#           else: self._data_path = "tests"

#         else: self._data_path = "tests"

#       else: self._data_path = create_new_dir("tests")

#     else: self._data_path = path

#     R = self._response[self._example_index+1:] if self._note_index is None else self._response[self._example_index+1:self._note_index]
#     nr = R.count("Input")
#     aux = nr
#     while nr > 0:

#       def in_out_files(nr1, nr2, ext, start, end):
#         sample = os.path.join(self._data_path, f"{self._code}_{nr1 - nr2 + 1}.{ext}")
#         if not os.path.exists(sample):
#           with open(sample, 'w', encoding="UTF-8") as ff:
#             for data in R[start+1:end]:
#               ff.write(f"{data}\n")

#       pi = R.index("Input")
#       po = R.index("Output")
#       in_out_files(aux, nr, "in", pi, po)
#       R[pi] = "input-done"
#       pi = R.index("Input") if "Input" in R else len(R)
#       in_out_files(aux, nr, "out", po, pi)
#       R[po] = "output-done"
#       nr -= 1
