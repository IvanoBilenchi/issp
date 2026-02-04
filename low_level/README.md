# ☣️ Low-level security

Low-level security exercises and lab materials for the
**Information Systems Security and Privacy** course at the
[Polytechnic University of Bari](https://www.poliba.it).

### 🔎 Contents

This directory is structured as follows:

- [`/exercises`](exercises): Simple incomplete C programs designed to learn the basics of the C
  programming language.
- [`/examples`](examples): Programs presented during the theoretical lectures to illustrate
  key C language features and common systems programming pitfalls.
- [`/hackmes`](hackmes): Intentionally vulnerable programs designed for exploitation via crafted
  malicious inputs. Refer to the included `README.md` file for further guidance.

### ⚠️ Important note

Everything in this repository, including all cryptographic and security primitives,
is fundamentally insecure. This code is intended strictly for educational purposes.

### 🛠️ Requirements

- Any reasonably up-to-date C compiler:
    - **Windows:** [Visual Studio](https://visualstudio.microsoft.com) (for the MSVC compiler).
    - **macOS:** [Xcode](https://developer.apple.com/xcode) (for the clang compiler).
    - **Linux:** [GCC](https://gcc.gnu.org).
- [CMake](https://cmake.org) 3.24 or later.

### 📌 Instructions

- Move into the `low_level` dir and generate the build system:
  ```console
  $ cd issp/low_level
  $ cmake -B build
  ```
- Build the executables:
  ```console
  $ cmake --build build
  ```
- The built executables will be located in the `build` directory.
  ```console
  $ build/hackme_00_admin_pass_flag  # Or any other executable.
  ```
