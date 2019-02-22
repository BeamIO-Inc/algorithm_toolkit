.. dev-environment:

===============================
The ATK Development Environment
===============================

When you work on algorithm projects, you can use the ATK's web-based development environment to make your life easier.

Running the environment
=======================

Once you have created a project, you can use:

.. code-block:: bash

    alg run

to start the development environment. This command starts a basic web server and provides access to API endpoints within the ATK that allow you to create and edit algorithms and processing chains, and test your chains to see if they work.

.. note::
    If you are running the ATK virtual server, such as with VirtualBox, you may need to run the development environment with the --host parameter as follows:

    .. code-block:: bash

        alg run --host=0.0.0.0

After you use `alg run`, you can point your web browser to http://localhost:5000/ and you will see the screen below:

.. image:: https://s3.amazonaws.com/atk-docs-images/dev-environment-home.png

Under the hood
--------------

When you use `alg run` from a Terminal window, you will see lines like the following appear:

.. code-block:: bash

     * Serving Flask app "run" (lazy loading)
     * Environment: development
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: 225-327-370

If you've worked with the web microframework `Flask <http://flask.pocoo.org/docs/1.0/>`_, this will look familiar. Each algorithm project is a Flask app.

Here's what's happening:

    - The name of the app is "run" (the run.py module in your project)
    - You're in "development" mode
    - "Debug" is enabled
    - The address to which to point your browser is http://127.0.0.1:5000/ (you can also use localhost, which is easier to remember)
    - It also gives you a debugger PIN code, which will be handy later (see the Debugging section)

Stopping The Environment
========================

From the terminal window. you can hit ``^C`` on your keyboard to stop the development server. On the web interface, the home page has a Stop button in the footer (see screen shot above); this can be useful when it seems as though your development server will not shut down.

The Project Homepage
====================

The first page you come to (shown above) is the project homepage (naturally enough). This gives you some helpful hints and links about what you can do with the ATK. There are also other links to related sites you may find useful.

Across the top of the screen is the ATK menu bar. It provides access to these areas of the ATK development environment:

    - **Project Home** (the current page)
    - **Algorithms**: A listing of the algorithms installed in this project, and information about them
    - **Chain Builder**: A tool to link algorithms together in processing chains
    - **Documentation**: A link to this site, or to local docs if you created the project using the `--with-docs` flag
    - **Test Run**: A test harness for running algorithm chains

Let's go over each of these pages in turn.

Algorithms Page
===============

For a new project, this page will be empty except for a link to create an algorithm. If you installed the example project, you'll see this screen:

.. image:: https://s3.amazonaws.com/atk-docs-images/dev-environment-algorithms.png

You can click on the name of an algorithm to get more information about it.

.. image:: https://s3.amazonaws.com/atk-docs-images/dev-environment-algorithms-expanded.png

See the section :doc:`working-with-algorithms` for more details about what this page does.

Chain Builder Page
==================

If you installed the example project, you'll see this page:

.. image:: https://s3.amazonaws.com/atk-docs-images/dev-environment-chain-builder.png

The example project comes with one chain, called "map_tiles". You can select it from the drop-down menu that reads "Select a chain to view/edit". When you select a chain, the chain definition is displayed:

.. image:: https://s3.amazonaws.com/atk-docs-images/dev-environment-chain-builder-show-chain.png

See the section Building Chains for more details on this feature.

Test Run Page
=============

Each chain you create becomes an option under the "Test Run" menu in the top navigation bar. In the example project, selecting the "map_tiles" chain displays this screen:

.. image:: https://s3.amazonaws.com/atk-docs-images/dev-environment-test-run.png

The form on this page allows you to run the chain by inputting various parameters and clicking "Run Algorithm Chain". See the section Testing Algorithm Chains for more details on how to use the test harness.
