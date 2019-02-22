.. _algorithm-registry:

======================
The Algorithm Registry
======================

The `Algorithm Registry <https://algorithmcentral.com>`_ is a repository of algorithms developed by the community of ATK users. If you make algorithms, we hope that you will consider publishing them to the Registry.

Searching for Algorithms
========================

Your primary interface to the Algorithm Registry as an ATK user is the :doc:`CLI <cli>`.

Finding algorithms to use in your project is easy:

.. code-block:: console

    $ alg search name_to_search_for

You can also use part of a name:

.. code-block:: console

    $ alg search pdal

A list of algorithms that match your search string will appear in your terminal window.

Getting Algorithm Info
======================

Once you know the name of your algorithm, you can get details about it:

.. code-block:: console

    $ alg info getmaptiles_roi

Installing Algorithms
=====================

When you want to install an algorithm into your project, do it like so:

.. code-block:: console

    $ alg install getmaptiles_roi

Publishing Algorithms
=====================

When you've created your awesome algorithm and you want to share it with others, we make it pretty easy to do so. You will need to do a couple of things first:

Get a TileDriver account
------------------------

To publish algorithms, you need a TileDriver account. `You can get one for free <https://app.tiledriver.com/accounts/login>`_.

Once you have an account and have logged in, go to the `Algorithm Toolkit page <https://app.tiledriver.com/atk/>`_ for instructions on how to link your account with the Registry.

Algorithm Naming
----------------

Every algorithm in the Registry has a unique name. You need to check the Registry before publishing to ensure your algorithm's name is not already taken.

Namespacing
-----------

One helpful way to ensure your algorithm's name will be unique is to use **namespacing**. This is simple to do: just add "`namespace`/" to the beginning of your algorithm's name.

For example, if you chose the namespace "crunchy_frog", you would create algorithms with names like "crunchy_frog/my_first_algorithm".

.. note::
    Namespaces must only contain letters, numbers or the underscore ("_"). By convention namespaces are all lowercase, but that is not required.

    Namespaces must end with a single forward slash ("/"). No other slashes may be in the namespace or name of the algorithm.

Make sure your algorithm is complete
------------------------------------

We ask that everyone who publishes algorithms ensure that they contain the following:

- The algorithm's folder MUST contain at least a ``main.py`` and ``algorithm.json`` file.
- A version string (see note below).
- A full description of what the algorithm does, including any dependencies users will need to install.
- Each parameter and output in your algorithm should also have a clear description and help text.
- The algorithm should have a good README file in the algorithm folder.
- A LICENSE file should also be in the algorithm folder providing clear terms of use.
- Unit tests for the algorithm are very helpful; follow the instructions in :doc:`tutorial` for writing and running algorithm tests.

The good news is: if you use the development environment, all of these things should already be in your algorithm. See :doc:`creating-your-first-algorithm` for details on how to create algorithms properly for publishing.

Another helpful but not required file is one called CHANGELOG. If you create one of these, each version of the algorithm you publish can contain information about changes since the prior version. The CHANGELOG should use `Markdown syntax <https://daringfireball.net/projects/markdown/syntax>`_.

Publish!
--------

Once you've done these things, go ahead and publish your algorithm:

.. code-block:: console

    $ alg publish my_algorithm

This will zip up the contents of your algorithm's folder, including all scripts and files it uses within that folder, and add it to the Registry. A copy of the zip file will be created in a folder called **algorithm_uploads** in your algorithm project.

.. note::
    The size of the zip file cannot be larger than 25 MB. If it is, the ATK will refuse to publish it.

A note about versions
---------------------

The version string in your algorithm.json file is important. The ATK scans this string and compares it with what has already been published on the Registry. Importantly, it does not try to guess whether this version is older or newer than what is in the Registry: it assumes that whatever version you are uploading is the current one.

If the version number is the same as one already in the Registry, what you upload will overwrite that version AND THAT VERSION WILL BECOME CURRENT. Therefore, if you want to make adjustments to a prior version of an algorithm, you may have to publish twice in order to ensure that the version you wish to be current is current.

Obviously, before you publish an algorithm make sure you have updated the version number.

Users can also view or install specific versions of an algorithm:

.. code-block:: console

    $ alg info -v 0.1.2 your_algorithm
    $ alg install -v 0.1.2 your_algorithm

If not specified, the current version will be used in these commands. An equivalent command would be:

.. code-block:: console

    $ alg info -v current your_algorithm

Note that you do not use the ``-v`` option when publishing.

.. note::
    You can use any versioning scheme you wish in your algorithms. Instead of a number, you could use "Beta", "v2", "Fred" or anything else you like.

About Licensing Your Algorithm
==============================

As you've probably guessed, we place a lot of emphasis on algorithms having some version of an `Open Source license <https://opensource.org/licenses>`_. However, you can put whatever restrictions you wish on usage of your algorithm.

We provide several Open Source license types out of the box with the ATK:

- MIT
- BSD-3-Clause
- GNU AGPLv3
- GNU GPLv3
- GNU LGPLv3
- Mozilla
- Apache
- The Unlicense

If you select one of these when creating your algorithm, the corresponding license text will be added to the algorithm's LICENSE file.

We also provide two other license options:

- Proprietary
- See LICENSE File

Both are essentially equivalent when creating your algorithm: the LICENSE file will be blank, and you can paste in any terms you wish (such as another Open Source license if we don't provide it).

The difference between these options is that choosing "Proprietary" is a signal to users that you require them to contact you and negotiate rights to use the algorithm. In any case, it is important that you place the terms of use in the LICENSE file.

License Enforcement
-------------------

As stated in the Registry Terms of Use, we do not attempt to enforce your license terms. Publishing your algorithm to the Registry is done at your own risk.
