# Browser front-end for from_Poland_with_love, executed by Brython.
# It runs the unmodified `interpreter` package from src/:
#  - on GitHub Pages the workflow copies src/interpreter next to this file;
#  - for local preview (serving the repo root) it is read from ../src.
#
# Brython's stdlib already has a module called `interpreter`, so a plain
# `import interpreter` would load the wrong one. Instead the original sources
# are fetched and registered under the name `polish_interpreter`.
import re
import sys
import types
from browser import document, window, html

PACKAGE = "polish_interpreter"
SOURCE_DIRS = ("interpreter/", "../src/interpreter/")
SUBMODULES = ("Memoizator", "Interpreter")  # dependency order


def fetch_text(url):
  xhr = window.XMLHttpRequest.new()
  xhr.open("GET", url, False)
  xhr.send()
  return xhr.responseText if xhr.status == 200 else None


def run_source(source, filename, namespace):
  # Brython's exec() can't resolve relative imports, so `from .X import Y`
  # is rewritten to an absolute import of the registered package (in memory only).
  source = re.sub(r"^(\s*)from \.(\w+)", rf"\1from {PACKAGE}.\2", source, flags=re.M)
  # CPython keeps the backslash of the invalid escape in f"\{x}" (Memoizator's
  # regex escaping); Brython drops it. Spell it out so both behave the same.
  source = source.replace('f"\\{', 'f"\\\\{')
  exec(compile(source, filename, "exec"), namespace)


def load_package():
  for base in SOURCE_DIRS:
    init_src = fetch_text(base + "__init__.py")
    if init_src is not None:
      break
  else:
    raise ImportError("interpreter sources not found")

  package = types.ModuleType(PACKAGE)
  package.__path__ = []
  package.__package__ = PACKAGE
  sys.modules[PACKAGE] = package
  for name in SUBMODULES:
    full_name = f"{PACKAGE}.{name}"
    module = types.ModuleType(full_name)
    module.__package__ = PACKAGE
    sys.modules[full_name] = module
    run_source(fetch_text(f"{base}{name}.py"), f"{base}{name}.py", module.__dict__)
    setattr(package, name, module)
  run_source(init_src, base + "__init__.py", package.__dict__)
  return package


PolishNotation = load_package().PolishNotation

MODES = ("toPolish", "fromPolish")


class TrackedInterpreter:
  """Wraps PolishNotation and reports whether the Memoizator cache answered."""

  # A cache hit is the only path where interpret() skips Memoizator.addExpression,
  # so an unchanged pattern count means the answer came from the cache.
  # (Patching memoized() on the instance doesn't work: Brython keeps calling the class method.)

  def __init__(self):
    self.engine = PolishNotation()
    self.patterns = self.engine._PolishNotation__memoizator._Memoizator__patternsMemoized
    self.cached = False

  def pattern_count(self):
    return sum(len(table) for table in self.patterns.values())

  def interpret(self, text, mode):
    before = self.pattern_count()
    result = self.engine.interpret(text, mode)
    self.cached = self.pattern_count() == before
    return result


def copy_to_clipboard(text):
  try:
    window.navigator.clipboard.writeText(text)
  except Exception:
    pass


# ---------------------------------------------------------------- window mode
tk_interpreter = TrackedInterpreter()
tk_input = document["tk-input"]
tk_mode = document["tk-mode"]
tk_output = document["tk-output"]


def tk_interpret(ev=None):
  if ev is not None:
    ev.preventDefault()
  tk_output.clear()
  tk_output.classList.remove("error")
  text = tk_input.value
  try:
    result = tk_interpreter.interpret(text, tk_mode.value)
  except Exception as exc:
    tk_output.classList.add("error")
    tk_output.text = f"  Interpretation error: {type(exc).__name__} — check the expression and mode."
    return
  copy_to_clipboard(result)
  tk_output <= f"  Output result:\t{result}"
  if tk_interpreter.cached:
    tk_output <= html.SPAN("ⓜ cached", Class="badge", title="Returned from the Memoizator pattern cache")


def use_example(ev):
  btn = ev.currentTarget
  tk_input.value = btn.attrs["data-expr"]
  tk_mode.value = btn.attrs["data-mode"]
  tk_interpret()


document["tk-form"].bind("submit", tk_interpret)
for chip in document.select(".chip"):
  chip.bind("click", use_example)


# --------------------------------------------------------------- console mode
COMMANDS = {
  "exit": [".q", ".exit", ".quit", ".ex"],
  "help": [".h", ".help"],
  "interprete to Polish notation": [".tp", ".toPolish"],
  "interprete from Polish notation": [".fp", ".fromPolish"],
  "paste example from clipboard": [".c", ".p", ".cp"],
  "clear": [".cl", ".clr", ".cls", ".clear"],
  "window mode": [".w", ".wnd", ".window"],
}

term_interpreter = TrackedInterpreter()
term_log = document["term-log"]
term_input = document["term-input"]
term_state = {"mode": "toPolish"}


def say(text, cls=None):
  line = html.DIV(text)
  if cls:
    line.classList.add(cls)
  term_log <= line
  term_log.scrollTop = term_log.scrollHeight


def is_command(text, name):
  return text in COMMANDS[name]


def term_calculate(text):
  try:
    result = term_interpreter.interpret(text, term_state["mode"])
  except Exception as exc:
    say(f"Interpretation error: {type(exc).__name__}", "err")
    return
  copy_to_clipboard(result)
  say("###############")
  say(f"Output result:  {result}" + ("   ⓜ" if term_interpreter.cached else ""), "res")
  say("###############")


def term_paste():
  def on_text(text):
    say(f"Pasted from clipboard:  {text}")
    term_calculate(text)

  def on_fail(err):
    say("Clipboard is not available (permission denied).", "err")

  try:
    window.navigator.clipboard.readText().then(on_text, on_fail)
  except Exception:
    on_fail(None)


def term_banner():
  say("Default interpretation: to Polish notation")
  say("Help (commands): .h (.help)")


def term_submit(ev):
  ev.preventDefault()
  text = term_input.value
  term_input.value = ""
  say(f"Enter a case/command: {text}", "in")

  if is_command(text, "exit"):
    say("Session ended. Starting a new one…")
    term_state["mode"] = "toPolish"
    term_banner()
  elif is_command(text, "window mode"):
    document["window-mode"].scrollIntoView({"behavior": "smooth"})
    tk_input.focus()
  elif is_command(text, "help"):
    say("")
    say("Commands:")
    for name, aliases in COMMANDS.items():
      say(f"{name}: {', '.join(aliases)}")
    say("")
  elif is_command(text, "interprete to Polish notation"):
    term_state["mode"] = "toPolish"
    say("Mode's switched: to Polish")
  elif is_command(text, "interprete from Polish notation"):
    term_state["mode"] = "fromPolish"
    say("Mode's switched: from Polish")
  elif is_command(text, "clear"):
    term_log.clear()
  elif is_command(text, "paste example from clipboard"):
    term_paste()
  else:
    term_calculate(text)


document["term-form"].bind("submit", term_submit)
document["terminal"].bind("click", lambda ev: term_input.focus())


# ---------------------------------------------------------------------- ready
term_banner()
for el_id in ("tk-btn", "term-input"):
  document[el_id].disabled = False
tk_interpret()
