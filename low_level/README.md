# Low-level security

Low-level security exercises and lab materials for the
**Information Systems Security and Privacy** course at the
[Polytechnic University of Bari](https://www.poliba.it).

### Repo structure

The repository is structured as follows:

- `/exercises`: simple incomplete C programs designed to learn the basics of the C
  programming language.
- `/examples`: programs presented during the theoretical lectures to illustrate key C language
  features and common systems programming pitfalls.
- `/hackmes`: intentionally vulnerable programs designed for exploitation via crafted
  malicious inputs. Refer to `/hackmes/README.md` for further guidance.

### Important notes

Everything in this repository, including all cryptographic and security primitives, is fundamentally
insecure. This code is intended strictly for educational purposes.

### Compiling the programs

- Install any reasonably up-to-date C compiler.
    - **Windows:** [Visual Studio](https://visualstudio.microsoft.com) (for the MSVC compiler).
    - **macOS:** [Xcode](https://developer.apple.com/xcode) (for the clang compiler).
    - **Linux:** [GCC](https://gcc.gnu.org).
- Install [CMake](https://cmake.org) (3.24 or later).
- Clone this repository (or download it as a zip):
    ```console
    $ git clone https://github.com/IvanoBilenchi/issp.git
    ```
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
