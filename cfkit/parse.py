from typing import TypeAlias
from shutil import rmtree
from .util.util import *
Directory: TypeAlias = str

def extract(self, path: Directory = None, CreateTestsDir: bool = True, __check_path: bool = True):

  if path == None: path = os.getcwd()
  elif path != None and __check_path: 
    check_path_existence(path, 'd')

  os.chdir(path)
  
  if CreateTestsDir:

    def tmp(x): os.mkdir(x); return f"{x}"
    
    if os.path.exists("tests"):
      L = os.listdir("tests")
      self.__Lo = sorted([file for file in L if re.search(rf"{self._code}_\d.out", file) != None])
      self.__Li = sorted([file for file in L if re.search(rf"{self._code}_\d.in", file) != None])
      if len(self.__Lo) != len(self.__Li):
      
        c = input("Another folder with the same name already exists\n\[W]rite in the same folder or [R]eplace the folder or [C]reate a new one with another name? ").lower()
        while c != 'r' and c != 'c' and c != "w":
          c = input("[W/r/c]")
      
        if c == 'r':
          rmtree(os.path.join(path, "tests"))
          self.__data_path = tmp("tests")
      
        elif c == 'c':
          name = input("Folder name: ")
          path_exist_error(name, "d")
          self.__data_path = tmp(name)
      
        else: self.__data_path = "tests"
      
      else: self.__data_path = "tests"
    
    else: self.__data_path = tmp("tests")
  
  else: self.__data_path = path

  R = self._content[self.__pex+1:] if self.__pn == None else self._content[self.__pex+1:self.__pn]
  nr = R.count("Input")
  aux = nr
  while nr > 0:

    def in_out_files(nr1, nr2, ext, start, end):
      sample = os.path.join(self.__data_path, f"{self._code}_{nr1 - nr2 + 1}.{ext}")
      if not os.path.exists(sample):
        with open(sample, 'w') as ff:
          for data in R[start+1:end]:
            ff.write(f"{data}\n")

    pi = R.index("Input")
    po = R.index("Output")
    in_out_files(aux, nr, "in", pi, po) # in
    R[pi] = "input-done"
    pi = R.index("Input") if "Input" in R else len(R)
    in_out_files(aux, nr, "out", po, pi) # out
    R[po] = "output-done"
    nr -= 1
