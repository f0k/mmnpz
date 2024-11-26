# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import inspect
import os
import sys
from datetime import datetime

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

sys.path.insert(0, os.path.abspath("../../src"))

import mmnpz

# -- Project information -----------------------------------------------------

project = "mmnpz"
author = "Jan Schlüter"
copyright = f"{datetime.today().year}, {author}"
release = mmnpz.__version__
version = ".".join(release.split(".", 2)[:2])


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
    "sphinx_copybutton",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
# exclude_patterns = []


# -- Options for MyST --------------------------------------------------------
# https://myst-parser.readthedocs.io/en/latest/configuration.html

# Create anchors up to h2 so MyST does not complain about #anchor links
myst_heading_anchors = 2


# -- Options for autodoc -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

autodoc_member_order = "bysource"
autodoc_typehints = "description"


# -- Options for intersphinx -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}


# -- Options for linkcode ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html#configuration


def linkcode_resolve(domain, info):
    if domain != "py" or not info["module"]:
        return None
    try:
        obj = sys.modules[info["module"]]
        for part in info["fullname"].split("."):
            obj = getattr(obj, part)
        absolute_filename = inspect.getsourcefile(obj)
        source, firstline = inspect.getsourcelines(obj)
        lastline = firstline + len(source) - 1
    except Exception:
        return None
    if absolute_filename is None:
        return None
    elif absolute_filename.startswith(os.path.dirname(mmnpz.__file__)):
        # mmnpz package
        filename = os.path.relpath(absolute_filename, start=os.path.dirname(mmnpz.__file__))
        tag = "main" if "dev" in release else ("v" + release)
        base_url = f"https://github.com/f0k/mmnpz/blob/{tag}/src/mmnpz"
    elif absolute_filename.startswith(os.path.dirname(os.__file__)):
        # Python standard library
        filename = os.path.relpath(absolute_filename, start=os.path.dirname(os.__file__))
        tag = "v%d.%d.%d" % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        base_url = f"https://github.com/python/cpython/blob/{tag}/Lib"
    else:
        return None
    return f"{base_url}/{filename}#L{firstline}-L{lastline}"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages.
html_theme = "furo"

# The title for the HTML pages.
html_title = f"mmnpz {release} docs"
html_short_title = f"mmnpz-{release}"

# Whether to copy the source files into a _source directory.
html_copy_source = False

# Whether to create alphabetic indices of everything.
html_use_index = False

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

# Icon for the HTML pages.
# html_favicon = "_static/favicon.ico"

# Logo for the project.
# html_logo = "_static/logo.png"


# -- Options for furo theme -------------------------------------------------
# https://pradyunsg.me/furo/customisation/#theme-options

html_theme_options = {
    "source_repository": "https://github.com/f0k/mmnpz",
    "source_branch": "main",
    "source_directory": "docs/",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/f0k/mmnpz",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,  # noqa: E501
            "class": "",
        },
    ],
}
