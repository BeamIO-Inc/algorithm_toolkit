.. _contributing:

=======================
Contributing to the ATK
=======================

Thanks for your interest in contributing to the Algorithm Toolkit codebase! You should know a few things.

Code of Conduct
===============

First of all: this project has a code of conduct. Please read the CODE_OF_CONDUCT file in the project root folder and stick to its principles.

License
=======

The MIT license (see LICENSE file) applies to all contributions.

Issue Conventions
=================

We use GitHub's Issue functionality to track issues submitted by users and developers. We ask that you abide by a few rules:

If you have questions about installation, distribution, and usage of the ATK, please first review the project's fairly decent documentation. If you open an issue of this kind, you will be reminded of the importance of reading the documentation. Indicate you have done so in your issue.

Questions about development of the ATK, brainstorming, requests for comment, and not-yet-actionable proposals should be prefaced with the word IDEA: at the top of the issue, on its own line. Please understand that although we enjoy getting these we may not respond at all to the issue once it's posted. We may also close the issue without responding, which generally means we've either logged it in our internal tracking system or we're not going to do anything with it at all. We will try to indicate which in a response.

Please search existing issues, open and closed, before creating a new one.

The following details would be helpful to know when you post bug reports, so please include them:

- Operating system type and version (Windows? Ubuntu 16.04? 18.04?)
- The version and source of the ATK (PyPI, GitHub, or somewhere else?)
- Any external dependencies your project has (particularly gnarly ones to troubleshoot like GDAL are good to know about)

Please provide these details as well as tracebacks and relevant logs.

Design Principles
=================

If there is a spectrum between a "batteries included" and "batteries not included" open source project (and we think there is), the ATK tends to want to be a "batteries included" project. That said, we want to make the ATK easy to install and use; therefore, contributions that increase the burden on the end user of the Toolkit are to be avoided.

Multiple interfaces
-------------------

You've probably noticed from reading these docs that we provide multiple paths to using the ATK. The two principal means are through a Web browser interface and a command line interface (CLI). Please consider how your new or revised feature would be used by both of these interfaces.

We believe that providing a fully featured Web interface makes a big difference to the usability of this project. Make sure that your contributions take that into account, and enhance the usability of the ATK as well as add functionality.

Scientific computing roots
--------------------------

The developers of this project are deeply rooted in the scientific community, particularly in the realm of Physics known as Imaging Science. As a result, it is common to see ATK-based projects depending on packages that are geared toward science and mathematics (Python packages like NumPy, SciPy, Matplotlib and so on) as well as C-based programs in the imaging and geospatial areas (particularly GDAL, OpenCV and proj.4).

While true, this does not mean that we are only interested in contributions from this community. We believe the ATK has broad appeal for any type of data processing, and we hope that we have a diverse set of contributor backgrounds.

Code Conventions
================

The ATK is first and foremost a Python project.

The ATK supports Python 2.7 and Python 3. It will likely continue to support Python 2 beyond the official end of life of that version (`currently January 1, 2020 <https://legacy.python.org/dev/peps/pep-0373/>`_). Contributions are expected to support both major versions.

We strongly prefer code adhering to `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_.

Tests are mandatory for new features. We use Python's `unittest <https://docs.python.org/2/library/unittest.html>`_. There is a ``.coveragerc`` file in the root folder for configuring the `coverage utility <https://coverage.readthedocs.io/en/v4.5.x/>`_, which is a handy tool for ensuring code coverage.

We aspire to 100% test coverage for the ATK, but as of this writing we are not there yet. We welcome any contributions that enhance our code coverage for testing. In particular, we do not have any tests for JavaScript code nor any end-to-end tests.

Development Environment
=======================

Developing the ATK requires Python 2.7 or any final release after and including 3.6. See above for version adherence guidelines.

Initial Setup
-------------

First, clone the ATK's ``git`` repo:

.. code-block:: console

    $ git clone https://github.com/BeamIO-Inc/algorithm_toolkit

Development should occur within a `virtual environment <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_ to better isolate
development work from custom environments. For Python 2 environments, we recommend either `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ or `virtualenvwrapper <https://virtualenvwrapper.readthedocs.io/en/stable/>`_.

All your work should be done in a separate branch from master. Currently we use the `Feature Branch Workflow <https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow>`_, and we ask that you do the same. Once you feel it's ready (including having unit tests), you may make a pull request on GitHub.

Running the tests
-----------------

The project's tests currently live in a single file called ``test_main.py`` in the project root folder. This will likely change in future.

To run the entire suite and the code coverage report:

.. code-block:: console

    $ pip install coverage
    $ coverage run -m unittest discover
    $ coverage html

A single test:

.. code-block:: console

    $ coverage run -m unittest test_main.NAME_OF_TEST_CLASS.name_of_test
    $ coverage html

You can also run without coverage:

.. code-block:: console

    $ python -m unittest discover

or:

.. code-block:: console

    $ python -m unittest test_main.NAME_OF_TEST_CLASS.name_of_test

Note that many of the tests create and destroy a test ATK project within the ATK folder structure. Your setUp and tearDown methods should follow the example set by the ATKTestCase class.

Place shared test utilities and mocked data in ``t_utils.py``.

Contributing to Docs
====================

We also welcome contributions to these docs. You should follow the same workflow above for contributing code as for contributing documentation. Also, please follow the reSructuredText format used by the existing documents (`guidelines here <https://www.sphinx-doc.org/en/stable/usage/restructuredtext/basics.html>`_).

You will need to install `Sphinx <https://www.sphinx-doc.org/en/stable/index.html>`_ and the `RTD theme <https://sphinx-rtd-theme.readthedocs.io/en/stable/>`_ to build docs locally (which you should do to make sure they look OK).

.. code-block:: console

    $ pip install sphinx sphinx_rtd_theme
    $ sphinx-build docs docs/html -a

