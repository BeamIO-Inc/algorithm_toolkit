.. pycharm:

=============================
PyCharm Configuration for ATK
=============================

If you use `PyCharm <https://www.jetbrains.com/pycharm/>`_ to develop Python applications, you can set it up to run the development environment for you rather than using the command line. The benefit of this is that you can then use the PyCharm debugging tools to set breakpoints and find out what's going on with your application.

This page will explain how to set up PyCharm correctly. It assumes you know how to use the PyCharm debugger.

Adding a Configuration
======================

Before you set up PyCharm, create your virtual environment and first project as described in :doc:`quick_start`.

Once you've done this, in PyCharm select Edit Configurations from the Run menu. You'll see a screen like this:

.. image:: https://s3.amazonaws.com/atk-docs-images/pycharm-1.png

Click the "+" sign to Add New Configuration.

In the screenshot we've filled in the fields of information you'll need:

- **Name**: Give this configuration a name (like "Run ATK server").
- **Single instance only**: check this box.
- **Module name**: when you first open this screen, the first field will read "Script path". Click the small arrow next to the name to reveal the option "Module name". Type the word ``flask`` into this field.

    .. note::
        As we mention elsewhere in the docs, each Algorithm Project is a `Flask <http://flask.pocoo.org/docs/1.0/>`_ app.

- **Parameters**: type the word ``run`` into this field.
- **Environment variables**: there will already be a variable called ``PYTHONBUFFERED=1`` in this field. Add a semicolon after that, and add: ``FLASK_APP=run;ATK_CONFIG=`` plus the full path to the ``config.py`` file in your Algorithm Project (e.g.: /home/myuser/atk/myproject/config.py). The whole line will read: ``PYTHONBUFFERED=1;FLASK_APP=run;ATK_CONFIG=/home/myuser/atk/myproject/config.py``.

    .. note::
        On Windows, the path to the ``config.py`` file would be indicated more like this: ``C:/Users/myuser/atk/myproject/config.py``. Note the use of forward slashes instead of the more typical back slashes.

- **Python interpreter**: the version of Python `inside your virtual environment`. This is important, because the Python interpreter is linked to the environment containing all the project dependencies (like the Algorithm Toolkit itself). If you use a different interpreter PyCharm will not find the Python packages it needs.

    .. note::
        If you don't see the interpreter for your virtual environment, select "Add Local" from the interpreter drop-down list. Then find the path to the python executable. On Mac OS and Linux, you can find it using ``which python``. On Windows you may be able to use ``where python`` in the same way. NOTE that you must be in the virtual environment for this to work.

- **Working directory**: the full path to your example project's root folder.

    .. note::
        Unlike for the Environment variables field, on Windows this path will have back slashes instead of forward slashes.

Running the server
==================

Once you've saved this configuration, you can run the server using the Play button next to the new configuration.
