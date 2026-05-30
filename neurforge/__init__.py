# ruff: noqa
"""`neurforge` is the unified product import namespace.

All implementations currently still live under `utu.*`. This package forwards
every access to `neurforge.*` to the corresponding `utu.*` module, returning the
SAME module objects (zero duplication, identical runtime behavior).

New code should import from `neurforge.*`; existing `utu.*` imports keep working.
Physically moving the code out of `utu` (and removing the `utu` name) is deferred
to a later, well-tested phase.
"""
import importlib
import importlib.abc
import importlib.util
import sys

_LEGACY = "utu"

# Import the real package so its side effects (env checks, logging, tracing) run
# exactly as they would on `import utu`.
_legacy_pkg = importlib.import_module(_LEGACY)


class _ForwardingFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Resolve `neurforge` / `neurforge.<sub>` to `utu` / `utu.<sub>` (same object)."""

    def find_spec(self, fullname, path=None, target=None):
        if fullname != __name__ and not fullname.startswith(__name__ + "."):
            return None
        legacy_name = _LEGACY + fullname[len(__name__):]
        real_module = importlib.import_module(legacy_name)
        sys.modules[fullname] = real_module
        return importlib.util.spec_from_loader(fullname, self)

    def create_module(self, spec):
        return sys.modules[spec.name]

    def exec_module(self, module):
        pass


sys.meta_path.insert(0, _ForwardingFinder())


def __getattr__(name):  # PEP 562: forward `from neurforge import X` to utu
    return getattr(_legacy_pkg, name)
