# Welcome to the Algorithm Toolkit (BETA)!

We built the Algorithm Toolkit (ATK) to provide researchers and data anaysts the tools they need to process data quickly and efficiently, so they can focus on actually doing scientific or other analysis work.

Please see this project's official documentation on [Read The Docs](https://algorithm-toolkit.readthedocs.io/en/latest/index.html). Below are instructions for how to install the ATK on your own system.

# Installation

## Super Quick Start

Python projects should be installed in virtual environments in order to keep versions of various packages in sync with the project code. However, if you want to get up and running immediately you can do the following in a Terminal window (assumes [Python](https://www.python.org/) and [pip](https://pip.pypa.io/en/stable/) are installed):

```shell
pip install algorithm_toolkit
alg cp myproject
cd myproject
alg run
```

Point your browser to http://localhost:5000/. You should see the development environment welcome page.

See the next section for a more detailed install process.

## Slightly More Involved But Still Pretty Quick Start

### A word about virtual environments

As noted above, it's a best practice to start new Python projects in virtual environments. As you work on code, you rely more and more on external libraries. As time passes, changes to those libraries will eventually break your code unless you are constantly updating it. So when you install a new version of a library for another project, suddenly you find that your earlier project no longer works.

Virtual environments solve this problem. Each environment contains a discreet set of the libraries used by your code, at the versions you determine.

Thankfully, creating virtual environments in Python is easy.

#### Python 3

Linux and Mac:

```shell
python3 -m venv myenvironment
source myenvironment/bin/activate
```

> On some Linux systems, python3-venv is not installed by default. If you get an error with the command above, try:
> ```shell
> # Debian/Ubuntu
> sudo apt install python3-venv
>
> # RedHat/CentOS
> sudo yum install python3-venv
> ```

On Windows:

```shell
py -3 -m venv myenvironment
myenvironment\Scripts\activate.bat
```

#### Python 2

Python 2 does not come with a built in virtual environment creator. We recommend using virtualenvwrapper. [Their install docs are excellent](https://virtualenvwrapper.readthedocs.io/en/latest/install.html).

Once you've installed and configured virtualenvwrapper, create your virtual environment:

```shell
mkvirtualenv myenvironment
```

## Setting up your ATK project

```shell
pip install algorithm_toolkit
alg cp myproject
cd myproject
alg run
```

Point your browser to http://localhost:5000/. You should see the development environment welcome page.

### What just happened?

Let's walk through this line by line.

```shell
pip install algorithm_toolkit
```

The ATK lives on [PyPi](https://pypi.org/), so this line downloads and installs the ATK in your virtual environment. Several dependencies will be installed as well.

```shell
alg cp myproject
```

This line uses the ATK's Command Line Interface (CLI) called `alg`. The `cp` command stands for "create project". "myproject" is the name of your project, which will also be the name of the folder created for the project (feel free to use a more original name).

```shell
cd myproject
```

Puts you in the project folder.

```shell
alg run
```

This command also uses the CLI. The `run` command starts a development web server. As we discuss elsewhere in the docs (see TODO: create page), setting up your algorithms and processing chains is accomplished using a web-based interface.

## Installing the example project

The ATK comes with an example project to help you understand how it works.

### Prerequisites

The example project requires [NumPy](http://www.numpy.org/) in order to work. If you're on a Linux machine, you can install the example project and it will handle this dependency for you.

However, if you're on a Mac or Windows machine, installing NumPy is more complicated.

### Anaconda

For these operating systems, we highly recommend using Anaconda or it's smaller cousin Miniconda. The only difference between these two is that Anaconda installs over 150 packages (including SciPy and NumPy) out of the box whereas with Miniconda you need to install everything separately. Either way is fine.

* [Anaconda installation Page](https://www.anaconda.com/download/#linux)
* [Miniconda installation Page](https://docs.conda.io/en/latest/miniconda.html)

Once Anaconda is installed, you can set up the example project right away. If you decide to use Miniconda, first do the following:

```shell
conda install numpy
```

### Install the example project

To set up the example project, just use the `--example` flag when setting up a new project:

```shell
alg cp myproject --example
```

## Installing documentation locally

If you want these docs to be installed locally, use the `--with-docs` flag when creating a project. You need to have Sphinx installed for this to work.

```shell
pip install sphinx sphinx_rtd_theme
alg cp myproject --with-docs
```

## Troubleshooting Install Issues

On some systems, additional libraries may be needed to install the Algorithm Toolkit. Try these packages if your ATK install fails:

**Debian/Ubuntu Linux**

```shell
# python 3
sudo apt install python3-dev build-essential

# python 2
sudo apt install python-dev build-essential
```

**RedHat/CentOS Linux**

```shell
# python 3
sudo yum install python3-devel

# python 2
sudo yum install python-devel
```

# Contributing

Thanks for your interest in contributing to the Algorithm Toolkit codebase! You should know a few things.

## Code of Conduct

First of all: this project has a code of conduct. Please read the CODE_OF_CONDUCT file in the project root folder and stick to its principles.

## License

The MIT license (see LICENSE file) applies to all contributions.

## Contributing to Docs

We also welcome contributions to the documentation. You should follow the same workflow for contributing code as for contributing documentation. Also, please follow the reSructuredText format used by the existing documents (guidelines here).

You will need to install Sphinx and the RTD theme to build docs locally (which you should do to make sure they look OK).

```shell
$ pip install sphinx sphinx_rtd_theme
$ sphinx-build docs docs/html -a
```

## More Info

Please see the Contributing page on Read The Docs for more detailed information.
