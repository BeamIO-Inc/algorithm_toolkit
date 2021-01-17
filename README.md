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

# Docker

## Building the [atk-base](docker/atk-base/Dockerfile) Docker image

* If you have [Docker](https://docs.docker.com/get-docker/) installed, you can build the base Docker image for the ATK

``` shell
git clone https://github.com/BeamIO-Inc/algorithm_toolkit.git
cd algorithm_toolkit
docker build -t atk-base -f ./docker/atk-base/Dockerfile .
```

* This is a very light weight Ubuntu based Docker image, that contains the algorithm toolkit, as well as the latest version of [Miniconda](https://docs.conda.io/en/latest/miniconda.html) with Python 3 installed

## Running the atk-base Docker image we just built (Optional)

* In theory, a user could work purely with this Docker image, however, see [example-project](cli/examples/project/README.md) for its intended use
* The following command can be used to run this Docker image

``` shell
docker run -d -p 5000:5000 --name atk-base-container atk-base
```

* The container can then be accessed via

``` shell
docker exec -it atk-base-container /bin/bash
```

## Building the [atk-dev-box](/docker/atk-dev-box/Dockerfile) Docker image

* To build this Docker image, it is assumed that you already have the [atk-base](docker/atk-base/Dockerfile) Docker image

``` shell
docker build -t atk-dev-box -f ./docker/atk-dev-box/Dockerfile .
```

* This Docker image contains the contents in the atk-base image, as well as [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/getting_started/overview.html)

## Running the atk-dev-box Docker image we just built

``` shell
docker run -d -p 5000:5000 -p 8888:8888 atk-dev-box
```

* Once the container is up and running, you can access JupyterLab by opening a web browser on your local machine and going to http://localhost:8888/
* You will never need to directly access the container via ```docker exec -it```
* JupyterLab allows you to open a terminal, which gives you full access to your container through your web browser (Pretty cool!)

## Running the ATK from the JupyterLab terminal

* Once you open up a terminal, you can go ahead and create a project

``` shell
alg cp myproject --example
```

* To run this project there is one extra little trick
  * You will need to specify the Docker container host IP, which will always be ```0.0.0.0```

``` shell
alg run --host 0.0.0.0
```

* Now, you can access the ATK web interface by opening another web browser on your local machine and going to http://localhost:5000/

## Recommendations for the atk-dev-box

### Set an access token for JupyterLab

* For security reasons, JupyterLab recommends that you set an access token
* You define the access token when running the atk-dev-box docker image

``` shell
docker run -d -e JUPYTER_TOKEN=enter_your_token_here -p 5000:5000 -p 8888:8888 atk-dev-box
```

* This is a token that you enter the first time you go to http://localhost:8888/ on your local web browser
* When entering the token, you also have the option to set a password
  * Note that the password will not go into effect until the Docker container is restarted

### Volume mounting

* Earlier we created a project in our Docker container through the JupyterLab terminal
* But what if something happens to our container down the road?
  * Whether it becomes corrupt, or we accidentally remove it
* Well... all the work inside the container would be lost ):
* Volume mounting allows our container to store our work on a directory on our local machine
* This way, if something happens to our container, we will maintain all of the work we have done
  * You can learn more about volume mounting [here](https://docs.docker.com/storage/volumes/)
* Volume mounting is defined when running the atk-dev-box Docker image

``` shell
docker run -d -v /full_path_to_local_directory/:/opt/workspace -p 5000:5000 -p 8888:8888 atk-dev-box
```

* ```/full_path_to_local_directory/``` represents the full path to a directory on your local machine
* ```/opt/workspace``` will be a new directory in the Docker container, which will store our work on our local machine, in ```/full_path_to_local_directory/```

## Note

* If you decide to run Docker on Windows instead of Linux, make sure you have CPU Virtulization enabled in your motherboard BIOS

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
