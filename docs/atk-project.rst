.. atk-project:

==================
Algorithm Projects
==================

When you use the Algorithm Toolkit (ATK), you will create and work on an Algorithm Project. A project contains one or more algorithms that you write, or that you install from the Algorithm Registry. It also contains some code to configure and run the project itself.

Creating a new project using the CLI will also create all the files and folders you need to get started. A new, empty project will look like this:

.. code-block:: bash

    algorithms/
        __init__.py
    logs/
        app.log
    .env
    .gitignore
    __init__.py
    chains.json
    config.py
    licenses.json
    run.py

Let's look at what each of these files and folders do:
    - The **algorithms/** folder will contain the algorithms used by this project. As you create or install algorithms, they will be placed in this folder.
    - The **logs/** folder contains ``app.log``, which algorithms can write to in order to provide information to a developer.
    - ``.env``: Environment variables needed by the project are stored in this file.
    - ``.gitignore``: This file will be familiar to you if you have used the git utility for managing source code. It tells git which files to leave out of a repository when saving or publishing it.
    - ``__init__.py``: This file tells Python that the folder should be considered a Python package.
    - ``chains.json``: When you create processing chains, the definitions of those chains will be saved in this file. When you start a new project, the file is empty.
    - ``config.py``: This is where you can set different parameters for the project, changing the way it works. See the Configuring a Project section below.
    - ``licenses.json``: This file is a placeholder for now, but will store license keys issued by developers for algorithms that require them.
    - ``run.py``: This file essentially links the project to the ATK.

Creating a project
==================

The easiest way to create a project is to use the ATK CLI:

.. code-block:: bash

    alg cp myproject

See the CLI docs for more information and examples.

Configuring a Project
=====================

config.py
---------

The ``config.py`` file contains different project settings. A new project's config.py will look like this:

.. code-block:: python

    import logging
    import os
    import sys

    from logging import Formatter
    from logging.handlers import RotatingFileHandler


    SECRET_KEY = os.environ['FLASK_SECRET_KEY']
    ATK_PATH = os.path.dirname(os.path.abspath(__file__))
    API_KEY = os.environ['ATK_API_KEY']

    sys.path.append(ATK_PATH)
    dirname = os.path.dirname
    logfile = os.path.join(dirname(__file__), 'logs', 'app.log')
    handler = RotatingFileHandler(logfile, maxBytes=10240, backupCount=10)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    # Add additional logger handlers here, add to LOG_HANDLERS list

    LOG_HANDLERS = [handler, ]

    # Add your custom settings below

These settings should probably not be changed, but you can add your own as the comment at the bottom of the file indicates.

About logging
-------------

As you can see from the configuration here, the LogLevel by default is set to ``DEBUG``. If you want to write more information to your log file (located in **logs/app.log** in your project), then keep this at ``DEBUG``. If you want to write less - such as when you're in a production setting - you can raise this to something like ``WARNING`` or ``ERROR``. Just change it like so:

.. code-block:: python

    handler.setLevel(logging.WARNING)

See `Python's documentation <https://docs.python.org/2/library/logging.html>`_ on ``logging`` for more details.

Optional settings
-----------------

Here are some additional settings you can add to the project using config.py:

.. py:data:: CORS_ORIGIN_WHITELIST

    You probably will never need to adjust this setting, but if you create an application that uses the ATK (e.g.: to run a chain from another application on the web), then that application's URL needs to be in this list. This is a safety measure to prevent unwanted apps from hitting your site.

    Default: ``[]``

    Example::

        CORS_ORIGIN_WHITELIST = ['http://mysite.com', ]

.. py:data:: DEFAULT_WORKING_ROOT

    When a chain runs, an algorithm can use this folder to store temporary files as well as file-based results. Each chain gets a unique ID, and the ATK makes a folder under DEFAULT_WORKING_ROOT with that ID as its name. Within that folder, a folder named **temp** and one named **results** are also created. Anything stored in **temp** gets deleted after a chain finishes, but files in **results** remain and can be used later.

    Default: ``'/tmp'``

    Example::

        DEFAULT_WORKING_ROOT = '/users/myusername/atk'

.env
----

``.env`` is a special configuration file. Anything placed in this file gets added to the system environment variables when the ATK is running. This is a place to store information that will be different from one environment to another (e.g.: one set of variables for development, one for production). Because of this, the ``.env`` file is listed in ``.gitignore`` and will not be added to a git repository if you create one. It's also a place to store information you don't want anyone to see (like security tokens).

A new project will have a ``.env`` file that looks like this::

    FLASK_SECRET_KEY="*********************************************************************"
    ATK_API_KEY="********************"
    ATK_MANAGEMENT_API_KEY="****************************************"
    FLASK_ENV=development

The "*"s will be random characters generated when you create the project using the CLI.

Notice that this is not a Python program, but just a text file. Here is an explanation of the parameters:

.. py:data:: FLASK_SECRET_KEY

    This is a key used internally by Flask to protect data submitted through forms and also to sign cookies. This key can contain unicode characters.

    **To be on the safe side, do not change this value**

.. py:data:: ATK_API_KEY

    This key is used when running a chain. You will paste it into the Test Run form when testing your chains, and use it when you run a chain from an external program. It's also used when querying the ATK about what chains and algorithms are installed.

.. py:data:: ATK_MANAGEMENT_API_KEY

    This key is used to find out information about the ATK node, like how much load the system has or to retrieve the application log file. This key must be different than the ATK_API_KEY. If you don't want to enable these features, you can remove this line from the ``.env`` file.

    **Note: If you use TileDriver Process** |trade| **, removing this key will reduce functionality**

.. py:data:: FLASK_ENV

    This is another Flask internal configuration setting. The two recognized options are "development" and "production". The development environment enables "DEBUG" in Flask automatically, which provides you the developer with useful information when testing out your code.

    Also, the development environment itself cannot be accessed when this is set to "production".

    .. note::
        You do not use quotation marks for this setting. The line would be::

            FLASK_ENV=production

        if you wanted to use the production environment.














