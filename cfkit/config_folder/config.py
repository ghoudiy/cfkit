L = [
  "GNU GCC C11 5.1.0",
  "Clang++20 Diagnostics",
  "Clang++17 Diagnostics",
  "GNU G++14 6.4.0",
  "GNU G++17 7.3.0",
  "GNU G++20 11.2.0 (64 bit, winlibs)",
  "Microsoft Visual C++ 2017",
  "GNU G++17 9.2.0 (64 bit, msys 2)",
  "C# 8, .NET Core 3.1",
  "C# 10, .NET SDK 6.0",
  "C# Mono 6.8",
  "D DMD32 v2.101.2",
  "Go 1.19.5",
  "Haskell GHC 8.10.1",
  "Java 11.0.6",
  "Java 17 64bit",
  "Java 1.8.0_241",
  "Kotlin 1.6.10",
  "Kotlin 1.7.20",
  "OCaml 4.02.1",
  "Delphi 7",
  "Free Pascal 3.0.2",
  "PascalABC.NET 3.8.3",
  "Perl 5.20.1",
  "PHP 8.1.7",
  "Python 2.7.18",
  "Python 3.8.10",
  "PyPy 2.7.13 (7.3.0)",
  "PyPy 3.6.9 (7.3.0)",
  "PyPy 3.9.10 (7.3.9, 64bit)",
  "Ruby 3.0.0",
  "Rust 1.66.0 (2021)",
  "Scala 2.12.8",
  "JavaScript V8 4.8.0",
  "Node.js 12.16.3"
]
l = len(L)
R = [22, 35, 19, 15, 20, 27, 20]
from os import get_terminal_size
max_columns = get_terminal_size().columns
i = 1
ok = True
S = R[0]
while i < len(R) and ok:
  if S + R[i] <= max_columns:
    S += R[i]
    i += 1
  else:
    ok = False
max_length = 0
for k in range(i):
    print(k * l, (l // i) * (k + 1))
    for j in range(k * l, (l // i) * (k + 1)):
        print(j)
        # print(len(max(L[j], key=len)), len(L[j][k]))
        # print(max(L[j]), "=", len(max(L[j])))
        # if k:
        #     pass
        # else:
        #   print(f"{L[j][k]}", end=' ' * (len(max(L[j], key=len)) - len(L[j][k]) + 1))
        #   R.append(len(L[j][k]) + len(' ' * (len(max(L[j], key=len)) - len(L[j][k]) + 1)))
    print()
# print(R)
# print(sum(R))
