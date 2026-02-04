# 🔒 High-level Security

High-level security exercises and lab materials for the
**Information Systems Security and Privacy** course at the
[Polytechnic University of Bari](https://www.poliba.it).

### 🔎 Contents

This directory is structured by specific subtopics, each housed within its own directory
containing both the designated exercises and a `solutions` subdirectory for reference.

The exercises are provided as incomplete Python programs. Students are expected to implement
the missing logic as specified in the assignment requirements, which are documented
in a comment block at the top of each file.

The `src` directory contains the source code of the `issp` library, upon which all exercises
are based. You can ignore its contents.

### 🛠️ Requirements

- [Python](https://python.org) 3.12 or later.
- Any IDE of your choice:
  - [Pycharm](https://www.jetbrains.com/pycharm) is simple to setup and get started with.
  - [Visual Studio Code](https://code.visualstudio.com) is another popular option.

### 📌 Instructions

- Move into the `high_level` dir and create a new virtual environment:
  ```console
  $ cd issp/high_level
  $ python -m venv .venv
  ```
- Activate the virtual environment:
  - Windows:
    ```console
    $ .venv\Scripts\activate
    ```
  - Linux and macOS:
    ```console
    $ source .venv/bin/activate
    ```
- Install the library and its dependencies:
  ```console
  $ pip install -e .
  ```
- Complete the exercise(s) and run them:
  ```console
  $ python 00_symmetric_crypto/00_plaintext.py  # Or any other exercise.
  ```
