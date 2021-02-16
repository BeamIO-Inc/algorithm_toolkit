.. _docker:

======================
Docker
======================

Building the atk Docker image
=============================

If you have `Docker <https://docs.docker.com/get-docker/>`__ installed, you can build the base Docker image for the ATK:

.. note::

    If you are running Docker on Windows instead of Linux, make sure you have CPU Virtulization enabled in your motherboard BIOS

.. code-block:: console

    $ git clone https://github.com/BeamIO-Inc/algorithm_toolkit.git
    $ cd algorithm_toolkit
    $ docker build -t atk -f ./docker/atk/Dockerfile .

Visit `here <https://docs.docker.com/develop/develop-images/baseimages/>`__ to learn more about base Docker images.

Running the atk Docker image (Optional)
=====================================================

In theory, a user could work purely with this Docker image, however, see `example-project <https://github.com/BeamIO-Inc/algorithm_toolkit/tree/master/cli/examples/project>`_ for its intended use.

The following command can then be used to run this Docker image:

.. code-block:: console

    $ docker run -d -p 5000:5000 --name atk-container atk


The container can then be accessed via:

.. code-block:: console

    $ docker exec -it atk-container /bin/bash

Building the atk-dev Docker image
=================================

This build requires that you have already built the atk Docker image in the previous steps.

With this requirement satisfied, you can proceed with the build:

.. code-block:: console

    $ docker build -t atk-dev -f ./docker/atk-dev/Dockerfile .

This Docker image contains the contents in the atk image, and the `JupyterLab <https://jupyterlab.readthedocs.io/en/stable/getting_started/overview.html>`_ web based user interface.

Running the atk-dev Docker image
==============================================

.. code-block:: console

    $ docker run -d -p 5000:5000 -p 8888:8888 atk-dev


JupyterLab allows you to open a terminal, which gives you full access to your container through your web browser (Pretty cool!).

Running the ATK from the JupyterLab terminal
============================================

Once you open up a terminal, you can go ahead and create a project:

.. code-block:: console

    $ alg cp myproject

To run this project there is one extra little trick.

You will need to specify the Docker container host IP, which will always be 0.0.0.0:

.. code-block:: console

    $ cd myproject
    $ alg run --host 0.0.0.0

Now, you can access the ATK web interface by opening another web browser on your local machine and going to http://localhost:5000/.

Recommendations for atk-dev
===============================

Set an access token for JupyterLab
----------------------------------

For security reasons, JupyterLab recommends that you set an access token.

You define the access token when running the atk-dev docker image:

.. code-block:: console

    $ docker run -d -e JUPYTER_TOKEN=enter_your_token_here -p 5000:5000 -p 8888:8888 atk-dev

Go to http://localhost:8888/ using your local web browser.

Enter the token in the 'Password or token' field, and click login.

After logging in, you can log out and set a password if you would like.

Note that the password will not go into effect until the Docker container is restarted.

Volume mounting
---------------

Earlier we created a project in our Docker container through the JupyterLab terminal.

But what if something happens to our container down the road (Whether it becomes corrupt, or we accidentally remove it)?

Well... all the work inside the container would be lost 😭

Volume mounting allows our container to store our work on a directory on our local machine.

This way, if something happens to our container, we will maintain all of the work we have done.

* You can learn more about volume mounting `here <https://docs.docker.com/storage/volumes/>`__.

Volume mounting is defined when running the atk-dev Docker image:

.. code-block:: console

    $ docker run -d -v /full_path_to_local_directory/:/opt/workspace -p 5000:5000 -p 8888:8888 atk-dev

``/full_path_to_local_directory/`` represents the full path to a directory on your local machine.

``/opt/workspace`` will be a new directory in the Docker container, which will store our work on our local machine, in ``/full_path_to_local_directory/``.