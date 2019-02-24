.. _quick-start:

============
Installation
============

Super Quick Start
=================

Python projects should be installed in virtual environments in order to keep versions of various packages in sync with the project code. However, if you want to get up and running immediately you can do the following in a Terminal window (assumes `Python <https://www.python.org/>`_ and `pip <https://pip.pypa.io/en/stable/>`_ are installed):

.. code-block:: bash

    pip install algorithm_toolkit
    alg cp myproject
    cd myproject
    alg run

Point your browser to http://localhost:5000/. You should see the development environment welcome page.

See the next section for a more detailed install process.

Slightly More Involved But Still Pretty Quick Start
===================================================

A word about virtual environments
=================================

As noted above, it's a best practice to start new Python projects in virtual environments. As you work on code, you rely more and more on external libraries. As time passes, changes to those libraries will eventually break your code unless you are constantly updating it. So when you install a new version of a library for another project, suddenly you find that your earlier project no longer works.

Virtual environments solve this problem. Each environment contains a discreet set of the libraries used by your code, at the versions you determine.

Thankfully, creating virtual environments in Python is easy.

Python 3
--------

Linux and Mac:

.. code-block:: bash

    python3 -m venv myenvironment
    source myenvironment/bin/activate

.. note::
    On some Linux systems, python3-venv is not installed by default. If you get an error with the command above, try:

    .. code-block:: bash

        # Debian/Ubuntu
        sudo apt install python3-venv

        # RedHat/CentOS
        sudo yum install python3-venv

On Windows:

.. code-block:: dosbatch

    py -3 -m venv myenvironment
    myenvironment\Scripts\activate.bat

Python 2
--------

Python 2 does not come with a built in virtual environment creator. We recommend using virtualenvwrapper. `Their install docs are excellent <https://virtualenvwrapper.readthedocs.io/en/latest/install.html>`_.

Once you've installed and configured virtualenvwrapper, create your virtual environment:

.. code-block:: bash

    mkvirtualenv myenvironment

Setting up your ATK project
===========================

.. code-block:: bash

    pip install algorithm_toolkit
    alg cp myproject
    cd myproject
    alg run

Point your browser to http://localhost:5000/. You should see the development environment welcome page.

What just happened?
-------------------

Let's walk through this line by line.

.. code-block:: bash

    pip install algorithm_toolkit

The ATK lives on `PyPi <https://pypi.org/>`_, so this line downloads and installs the ATK in your virtual environment. Several dependencies will be installed as well.

.. code-block:: bash

    alg cp myproject

This line uses the ATK's Command Line Interface (CLI) called `alg`. The `cp` command stands for "create project". "myproject" is the name of your project, which will also be the name of the folder created for the project (feel free to use a more original name).

.. code-block:: bash

    cd myproject

Puts you in the project folder.

.. code-block:: bash

    alg run

This command also uses the CLI. The `run` command starts a development web server. As we discuss elsewhere in the docs (see TODO: create page), setting up your algorithms and processing chains is accomplished using a web-based interface.

.. _installing-the-example-project:

Installing the example project
==============================

The ATK comes with an example project to help you understand how it works.

Prerequisites
-------------

The example project has some additional dependencies, including `NumPy <http://www.numpy.org/>`_, in order to work. If you're on a Linux machine, you can install the example project and it will handle this dependency for you.

However, if you're on a Mac or Windows machine, installing NumPy is more complicated.

Anaconda
--------

For these operating systems, we highly recommend using Anaconda or it's smaller cousin Miniconda. The only difference between these two is that Anaconda installs over 150 packages (including SciPy and NumPy) out of the box whereas with Miniconda you need to install everything separately. Either way is fine.

    - `Anaconda installation Page <https://www.anaconda.com/download/#linux>`_
    - `Miniconda installation Page <https://docs.conda.io/en/latest/miniconda.html>`_

Once Anaconda or Miniconda is installed do the following:

.. code-block:: bash

    conda install Pillow requests numpy Shapely

Install the example project
---------------------------

To set up the example project, just use the `--example` flag when setting up a new project:

.. code-block:: bash

    alg cp myproject --example

Installing documentation locally
================================

If you want these docs to be installed locally, use the `--with-docs` flag when creating a project. You need to have Sphinx installed for this to work.

.. code-block:: bash

    pip install Sphinx sphinx_rtd_theme
    alg cp myproject --with-docs

Troubleshooting Install Issues
==============================

On some systems, additional libraries may be needed to install the Algorithm Toolkit. Try these packages if your ATK install fails:

**Debian/Ubuntu Linux**

.. code-block:: bash

    # python 3
    sudo apt install python3-dev build-essential

    # python 2
    sudo apt install python-dev build-essential

**RedHat/CentOS Linux**

.. code-block:: bash

    # python 3
    sudo yum install python3-devel

    # python 2
    sudo yum install python-devel
