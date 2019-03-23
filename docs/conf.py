# -*- coding: utf-8 -*-
# cSpell:words undoc bysource ivar rtype mathjax ifconfig toctree localtoc
# cSpell:words todos elsarticle utphys pyproject toml

#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import re
import sys
from pathlib import Path


project_root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_root_dir))

from docs._themes.sphinx_customize import MyPyXRefRole  # noqa:

# -- Project information -----------------------------------------------------

project = "SUSY Cross Section"
copyright = "2019, Sho Iwamoto / Misho"
author = "Sho Iwamoto"
github_url = r"https://github.com/misho104/susy_cross_section"
doc_url = r"https://susy-cross-section.readthedocs.io/"

# The short X.Y version
version = ""
# The full version, including alpha/beta/rc tags
release = ""

pyproject = Path("../pyproject.toml").read_text()
ver_match = re.search(r'^version\s*=\s*"((\d+)\.(\d+)\..+?)"', pyproject, flags=re.M)
if ver_match:
    version = "{}.{}".format(ver_match.group(2), ver_match.group(3))
    release = ver_match.group(1)

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
needs_sphinx = "1.7"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.graphviz",
    "docs._themes.conf_bibtex",
    "sphinxcontrib.bibtex",
    "docs._themes.latex_writer",
    "docs._themes.sphinx_customize",
]

autodoc_default_flags = ["members", "undoc-members", "show-inheritance"]
autodoc_member_order = "bysource"

napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = False


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None

default_role = "any"
add_module_names = False

numfig = True

rst_epilog = r"""
.. bibliography:: references.bib cross_section_references.bib
    :filter: docname in docnames
    :style: default

.. |begintwofigure| raw:: latex

                     \begin{figure}[tp]


.. |endtwofigure| raw:: latex

                   \end{figure}
"""


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "SUSYCrossSectiondoc"


# -- Options for LaTeX output ------------------------------------------------
latex_additional_files = [
    "_themes/mysphinx.sty",
    "_themes/utphys27mod.bst",
    "references.bib",
    "cross_section_references.bib",
    "foot_matter.tex.in",
]

latex_abstract = r"""
\texttt{susy\_cross\_section} is a Python package to handle cross-section grid tables regardless of their format.
This package may parse any table-like grid files as a \texttt{pandas.DataFrame} object, and with built-in interpolators users can get interpolated values of cross sections together with uncertainties.
Several table data is also pre-installed in this package.
"""

latex_preamble = r"""
\makeatletter
\long\def\sphinxmaketitle{
\vrule
{\smallskip\par\vskip64pt plus 8pt minus 10pt\par}
{\LARGE\flushleft\sffamily\bfseries{\@title}\par}
{\vskip8pt\par}
\hrule height 1.5\p@ %
{\vskip24pt\par}
\hspace{0.1\textwidth} \begin{minipage}{0.89\textwidth}\noindent
{\bfseries\sffamily\@author}
{\par\vskip8pt\par}
Dipartimento di Fisica e Astronomia, Universit\`a degli Studi di Padova\\
Via Marzolo~8, I-35131 Padova, Italia
{\par\vskip8pt\par}
\href{mailto:sho.iwamoto@pd.infn.it}{\texttt{sho.iwamoto@pd.infn.it}}
{\par\vskip24pt\par}
package \texttt{\bfseries susy\_cross\_section} for Python 2.7, 3.5+\\
version: \texttt{<<RELEASE>>}\\
repository: \url{<<GITHUB>>}\\
document: \url{<<DOC_URL>>}\\
License: \href{https://tldrlegal.com/license/mit-license}{MIT License}
\end{minipage}
{\par\vskip48pt\par}
\subsubsection*{Abstract}\par<<ABSTRACT>>\par
{\par\vskip12pt\par}
\autogeneratedwarning
}
\makeatother
"""
latex_preamble = latex_preamble.replace("<<RELEASE>>", release)
latex_preamble = latex_preamble.replace("<<GITHUB>>", github_url)
latex_preamble = latex_preamble.replace("<<DOC_URL>>", doc_url)
latex_preamble = latex_preamble.replace("<<ABSTRACT>>", latex_abstract)


latex_elements = {"figure_align": "ht", "preamble": latex_preamble}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass).
latex_documents = [
    (
        master_doc,
        "SUSYCrossSection.tex",
        "Package \\texttt{susy\\_cross\\_section} Manual",
        "Sho Iwamoto / Misho",
        None,
    )
]

latex_toplevel_sectioning = "section"

# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.6/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "numpy": ("https://docs.scipy.org/doc/numpy", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    # 'matplotlib': ('https://matplotlib.sourceforge.net', None),
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


def setup(app):
    if napoleon_use_ivar:
        app.registry.domains["py"].roles["attr"] = MyPyXRefRole()
    app.add_stylesheet("custom.css")
    return {"parallel_read_safe": True, "parallel_write_safe": True}
