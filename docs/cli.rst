.. _cli:

===
CLI
===

The ATK includes a Command Line Interface (CLI) that helps you with a number of tasks. Several sections of these docs show you practical examples; this page contains all the commands and options for each.

alg
===

All of the commands are prefaced by the word ``alg``.

Syntax::

    Usage: alg [OPTIONS] COMMAND [ARGS]...

If you type ``alg`` by itself, you'll get the help message:

::

    Usage: alg [OPTIONS] COMMAND [ARGS]...

      Welcome to the Algorithm Toolkit CLI!

    Options:
      --help  Show this message and exit.

    Commands:
      ca                 Create an algorithm.
      cp                 Create an algorithm project.
      generate_settings  Generate new environment variables for your...
      info               Get detailed info about an algorithm from the...
      install            Install an algorithm from the Registry.
      list               List algorithms in the current project.
      publish            Plublish an algorithm to the Algorithm...
      run
      search             Search the Algorithm Registry for algorithm...
      shell
      test               Test algorithms in your project.
      uninstall          Remove an algorithm from your project.

The ``--help`` or ``-h`` option will also display this message. Using ``--help`` with a command will display help for that command; e.g.::

    alg cp --help

Commands
========

cp
--

Create a new algorithm project.

Syntax::

    Usage: alg cp [OPTIONS] PROJECT_NAME

      Create an algorithm project.

    Options:
      -e, --example     Install example project
      -wd, --with-docs  Add documentation to portal
      -q, --quiet       Suppress screen output
      -h, --help        Show this message and exit.

Use the ``-e`` option to install the example project.

Use the ``-wd`` option to install local documentation (same as these docs).

Use the ``-q`` option to suppress output messages from this command.

ca
--

Create a new algorithm.

Syntax::

    Usage: alg ca [OPTIONS] ALGORITHM_NAME

      Create an algorithm.

    Options:
      -h, --help  Show this message and exit.

When you create a new algorithm, the CLI steps you through each of the algorithm fields of information one at a time. You can also create parameters and outputs by responding to additional questions.

generate_settings
-----------------

Create a new ``.env`` file for the project, with randomized values for security tokens.

Syntax::

    Usage: alg generate_settings [OPTIONS]

      Generate new environment variables for your algorithm project.

    Options:
      -p, --production  Use production settings
      -h, --help        Show this message and exit.

This is particularly useful when deploying an algorithm project to production, so that you don't have to worry about transporting sensitive information to the new environment.

Using the ``-p`` option sets ``FLASK_ENV`` to "production", thus disabling debug mode for the project.

info
----

Get information about an algorithm installed in the Algorithm Registry.

Syntax::

    Usage: alg info [OPTIONS] ALGORITHM

      Get detailed info about an algorithm from the Registry.

    Options:
      -r, --registry TEXT  Get algorithm info from which registry?
      -v, --version TEXT   Specify an algorithm version
      -h, --help           Show this message and exit.

If you have access to a private Registry, you can use the ``-r`` option to query that registry.

Use the ``-v`` option if you want to specify which version of an algorithm you want information on.

install
-------

Install an algorithm from the Algorithm Registry.

Syntax::

    Usage: alg install [OPTIONS] ALGORITHM

      Install an algorithm from the Registry.

    Options:
      -r, --registry TEXT  Install algorithm from which registry?
      -v, --version TEXT   Specify an algorithm version
      -h, --help           Show this message and exit.

If you have access to a private Registry, you can use the ``-r`` option to install from that registry.

Use the ``-v`` option if you want to specify which version of an algorithm you want to install.

list
----

List algorithms in the current project.

Syntax::

    Usage: alg list [OPTIONS]

      List algorithms in the current project.

    Options:
      -h, --help  Show this message and exit.

Algorithms will be displayed in a tidy tabular format::

    >>> alg list

    Algorithm Name          Version    Description
    ----------------------  ---------  ------------------------------------------------------------------------------
    multiply_numbers        0.0.1      Multiply two numbers together to get a result.
    output_image_to_client  0.0.1      This algorithm will pull the path to an image (RGB png currently supported)...
    add_numbers             0.0.1      Add two numbers together to get a result.
    getmaptiles_roi         0.0.1      This algorithm will gather up map tiles at a given zoom level that intesect...
    subtract_numbers        0.0.1      Subtract one number from another to get a result.
    divide_numbers          0.0.1      Divide one number from another to get a result.
    my_first_algorithm      0.0.1      This is my first algorithm, and I'm proud of it.
    stitch_tiles            0.0.1      This algorithm stitches a group of map tiles saved in a directory together....

publish
-------

Publish an algorithm to the Algorithm Registry.

Syntax::

    Usage: alg publish [OPTIONS] ALGORITHM_NAME

      Publish an algorithm to the Algorithm Registry.

    Options:
      -r, --registry TEXT  Publish to which registry?
      -h, --help           Show this message and exit.

If you have access to a private Registry, you can use the ``-r`` option to publish the algorithm to that registry.

run
---

Run the ATK development environment.

Syntax::

    Usage: alg run [OPTIONS] [ARGS]...

    Options:
      --help  Show this message and exit.

If you're running on a virtual server (such as with VirtualBox), you can use the ``--host=0.0.0.0`` option.

search
------

Search the Algorithm Registry for an algorithm by name.

Syntax::

    Usage: alg search [OPTIONS] SEARCH_STRING

      Search the Algorithm Registry for algorithm names matching a string.

    Options:
      -r, --registry TEXT  Search algorithms from which registry?
      -h, --help           Show this message and exit.

If you have access to a private Registry, you can use the ``-r`` option to search that registry.

shell
-----

Launch a Python shell with the current algorithm project settings active.

Syntax::

    Usage: alg shell [OPTIONS] [ARGS]...

    Options:
      --help  Show this message and exit.

test
----

Test one or more algorithms in the current project.

Syntax::

    Usage: alg test [OPTIONS] [ALGORITHM]

      Test algorithms in your project. You may specify an algorithm to test:
          >>> alg test my_algorithm

      or test all algorithms:
          >>> alg test

    Options:
      -h, --help  Show this message and exit.

uninstall
---------

Remove an algorithm from the current project.

Syntax::

    Usage: alg uninstall [OPTIONS] ALGORITHM

      Remove an algorithm from your project.

    Options:
      -h, --help  Show this message and exit.










