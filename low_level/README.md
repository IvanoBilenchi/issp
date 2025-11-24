# Low-level security

Low-level security exercises and lab materials for the
**Information Systems Security and Privacy** course at the
[Polytechnic University of Bari](https://www.poliba.it).

### Important notes

Examples and exercises are designed to learn the basics of the C programming language,
especially with respect to concepts such as pointers, addresses, and memory management.

It goes without saying that anything available in this repository, including any cryptographic
primitive, is highly insecure and only has educational value.

### Setting up the project

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
