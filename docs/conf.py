"""Sphinx configuration for pqcdbchk documentation."""

from importlib.metadata import version as _version

project = "pqcdbchk"
copyright = "2026, pqcdbchk contributors"
release = _version("pqcdbchk")
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "myst_parser",
]

napoleon_google_docstring = True
napoleon_numpy_docstring = True

autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
