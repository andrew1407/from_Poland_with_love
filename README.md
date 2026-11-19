# from_Poland_with_love

<p align="center">
  <a href="https://andrew1407.github.io/from_Poland_with_love/" title="Open the app in the browser">
    <img src="docs/icon.svg" alt="From Poland with Love" width="140" height="140">
  </a>
</p>

[![CI](https://github.com/andrew1407/from_Poland_with_love/actions/workflows/ci.yml/badge.svg)](https://github.com/andrew1407/from_Poland_with_love/actions/workflows/ci.yml)
[![GitHub Pages](https://github.com/andrew1407/from_Poland_with_love/actions/workflows/pages.yml/badge.svg)](https://github.com/andrew1407/from_Poland_with_love/actions/workflows/pages.yml)

A Python interpreter that converts arithmetic expressions to and from Polish (prefix) notation. It runs as an interactive console application or as a graphical desktop window.

**Live demo:** [andrew1407.github.io/from_Poland_with_love](https://andrew1407.github.io/from_Poland_with_love/) — both modes running in the browser.

## Overview

The core engine, [`PolishNotation`](src/interpreter/Interpreter.py), performs two conversions:

- **toPolish** — translates a standard infix expression (for example `(a + b) / c`) into Polish notation (`a b + c /`).
- **fromPolish** — translates a Polish-notation expression back into infix form, restoring parentheses according to operator precedence.

The interpreter supports the operators `+`, `-`, `*`, `/`, and `^`, parentheses, negative operands, and multi-character variable names. Results are computed by a stack-based algorithm that respects operator priorities. A [`Memoizator`](src/interpreter/Memoizator.py) caches each conversion as a regular-expression pattern, so structurally identical expressions (and their inverse) are returned from cache instead of being recomputed.

In both modes the produced result is also copied to the system clipboard.

## Modes

| Mode | Interface | Entry point |
| --- | --- | --- |
| Console | Interactive text prompt | [`ConsoleIOI`](src/ioInterfaces/ConsoleIOI.py) |
| Window | Tkinter GUI | [`WindowIOI`](src/ioInterfaces/WindowIOI.py) |

### Console mode

The console reads expressions or commands from a prompt loop. Available commands:

| Command | Aliases | Action |
| --- | --- | --- |
| Help | `.h`, `.help` | List commands |
| To Polish | `.tp`, `.toPolish` | Switch to infix-to-Polish conversion (default) |
| From Polish | `.fp`, `.fromPolish` | Switch to Polish-to-infix conversion |
| Paste example | `.c`, `.p`, `.cp` | Read an expression from the clipboard and convert it |
| Clear | `.cl`, `.clr`, `.cls`, `.clear` | Clear the terminal |
| Window mode | `.w`, `.wnd`, `.window` | Open the GUI window |
| Exit | `.q`, `.exit`, `.quit`, `.ex` | Quit |

### Window mode

The GUI presents an input field, a drop-down to select `toPolish` or `fromPolish`, and an **Interpret** button that displays the converted result.

## Tech stack

- **Python**
- **Tkinter** — graphical user interface
- **pyperclip** — clipboard access

## Running

Install dependencies:

- Linux: [`./setupLinux.sh`](setupLinux.sh) (installs `xclip` and `pyperclip`)
- Windows: [`setupWindows.bat`](setupWindows.bat) (installs `pyperclip`)

Run from the [`src`](src) directory. The first command-line argument selects the mode (`console` or `window`); console mode is used when no argument is given:

```bash
cd src
python from_Poland_with_love.py            # console mode (default)
python from_Poland_with_love.py console    # console mode
python from_Poland_with_love.py window     # GUI mode
```

Run the test script:

```bash
cd src
python tests.py
```

[`tests.py`](src/tests.py) checks round-trip conversions against expected results and times cached versus freshly computed conversions.

A [`exeBuilder.bat`](exeBuilder.bat) script is provided to package a standalone Windows executable with PyInstaller.

## Project structure

```
.
├── src/
│   ├── from_Poland_with_love.py   # launcher; selects mode from argv
│   ├── tests.py                   # conversion and memoization tests
│   ├── interpreter/
│   │   ├── __init__.py
│   │   ├── Interpreter.py         # PolishNotation conversion engine
│   │   └── Memoizator.py          # regex-pattern result cache
│   └── ioInterfaces/
│       ├── __init__.py
│       ├── ConsoleIOI.py          # console interface
│       └── WindowIOI.py           # Tkinter GUI interface
├── setupLinux.sh                  # Linux dependency setup
├── setupWindows.bat               # Windows dependency setup
├── exeBuilder.bat                 # PyInstaller build script
└── LICENSE
```

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.
