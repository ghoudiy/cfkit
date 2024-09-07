### 1\. Introduction

#### Overview:

cfkit is a **fast, cross-platform (Windows, macOS, Linux) command-line interface (CLI)** tool built for Codeforces users to simplify competitive programming. It focuses on **result comparison, fetching problem samples, and automating routine contest tasks**, allowing users to focus more on problem-solving.

#### Features:

*   **Efficient Result Comparison:** Compare floating-point numbers, allow any-order comparison, or use strict comparison.
  
*   **High Traffic Resilience:** Parses problem data even under server load.
  
*   **Language Support:** Compatible with all programming languages used on Codeforces.
  
*   **Fetch Problem Samples:** Retrieves sample test cases for problems.
  
*   **Local Compilation and Testing:** Compile and test solutions locally.
  
*   **Template-Based Code Generation:** Generate code with templates, including timestamps and author info.
  
*   **Contest Problem Stats:** Lists problem statistics for specific contests.
  
*   **Enhanced CLI Output:** Distinguish correct and incorrect results easily with colored output.
  

### 2\. Installation

Ensure [Python](https://www.python.org/) is installed on your system. Then, run these commands in your terminal:  
`pip install cfkit`  
`cf config all`

#### And your are ready to go!

### 3\. Usage
```
cf run 2000a.cpp    Compiles and tests your solution locally,
                    fetching and parsing missing sample test cases,
                    then comparing your output to the expected results with highlighted differences.
```

#### Options:

`-o`: Accept answers in any order.  
`-c`: Run only custom samples or use custom input without comparing results.  
`-s`: Do not ignore extra spaces during comparison.  
`-n`: Do not ignore extra new lines during comparison.  

```
cf gen 2000a    Generates a code file from the default (or chosen) template.
```
cf parse 2000   Fetch all sample test cases from a contest.

### 4\. FAQ
**Q:** How do I add a new test case?  
**A:** To add a new test case, create two files: `inK.txt` and `outK.txt`, where **K** is a number. If you're using **Linux or MacOs**, omit the **.txt** extension (e.g., `in1`, `ou1`, `in2`, `out2`). You can create additional test cases by increasing the value of K (e.g., `in1.txt`, `out1.txt`, `in2.txt`, `out2.txt`).

### 5\. Contact
I’m always open to feedback, suggestions, and collaboration! If you have any questions or want to get in touch, feel free to reach out:

Email: ghoudi.dev@gmail.com  
GitHub: [my github account](https://github.com/ghoudiy/) — check out my other projects or contribute to ongoing ones.  
Support: If you’d like to support my work and help me continue creating cool programs, you can do so [here](https://www.patreon.com/ghoudiy/membership).  
Looking forward to hearing from you! :)
