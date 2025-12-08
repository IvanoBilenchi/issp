# Vulnerable C Programs

This folder contains a collection of **vulnerable C programs**.
Each program accepts user input and executes a very simple functionality.

### Instructions

Generally speaking, your goal is threefold:

1. **Identify** the specific security flaws affecting each program.
2. **Determine** how these flaws can be securely fixed.
3. **Exploit** the vulnerabilities by providing carefully crafted input
   to achieve a specific malicious task, such as leaking confidential data
   or executing unauthorized functions.

Specific instructions for analyzing and exploiting each program are provided
within the comments at the top of its respective `.c` source file.

### General Guidance

- You can **ignore** all statements starting with `dlog_`; these are part
  of the internal debug logging system and are not relevant to the program's
  core logic or vulnerabilities.
- Each compiled executable accepts a command-line flag (`-d` or `--debug`).
  Using this flag will display **useful debugging information** concerning
  the data and function layout, which may aid in your analysis.
- User input can be provided as standard **ASCII text**. Alternatively,
  **individual bytes** can be specified by encoding each byte as a backslash
  (`\`) followed by one or two hexadecimal characters.
  > **Example:** 16 bytes made of 8 ASCII characters and 8 hex-encoded bytes:
  > `abcdefgh\0\1\2\3\a0\b1\c2\d3`
