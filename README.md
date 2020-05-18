# VyPRAnalysis

For Python 2.

A self-contained library to use with VyPRServer at http://github.com/pyvypr/VyPRServer.

In-depth documentation is found at http://cern.ch/vypr/analysis-docs/.

## Building the Documentation

To compile the documentation, run the following:

1. ``pip install Sphinx`` to install the sphinx documentation system.

2. ``pip install sphinx_rtd_theme`` to install the theme that we use.
3. From the directory above your local instance of the VyPRAnalysis repository, run ``sphinx-build -E -b html VyPRAnalysis/docs_source VyPRAnalysis/docs``
This will build the documentation in the ``docs`` directory of the VyPRAnalysis repository.

Note: Do not add the built documentation to the repository.  We only include the source.
