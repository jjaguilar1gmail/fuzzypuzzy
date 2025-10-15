"""I/O adapters package.

This package is intentionally named ``io`` to match the project layout.
It shadows the Python standard library module with the same name; import
the submodules explicitly if you need the adapters (for example:
``from fuzzypuzzy.io import serializers``).
"""

__all__ = ["serializers", "exporters", "parsers"]
