.. _working-with-algorithms:

=======================
Working With Algorithms
=======================

What is an algorithm?
=====================

In terms of the ATK, an algorithm is a Python package that contains at least some Python code that follows a specific structure, and a JSON file describing the algorithm's input and outputs. Like any Python package, an algorithm can contain a lot of other things as well.

Creating an Algorithm
=====================

There are three ways you can create an algorithm:

    1. Use the development environment web interface (see below section)
    2. Use the CLI (see the CLI section in the docs for the ``ca`` command)
    3. Manually create it yourself

We recommend the first two options over the third. We've created a lot of checks to make sure things like typos and missing files don't happen.

Structure Of An Algorithm
=========================

When you create an algorithm using the CLI or the development environment web interface, the following five files will be created inside the **algorithms/**\ `algorithm_name` folder in your project:

.. code:: bash

    __init__.py
    algorithm.json
    LICENSE
    main.py
    README.md
    test.py

Let's look at each of these in turn.

    - ``__init__.py``: This file tells Python to consider this folder a Python package; it will probably never have anything in it
    - ``algorithm.json``: This file contains the algorithm's configuration, including any input parameters or data that the algorithm outputs
    - ``LICENSE``: This file contains whatever licensing terms you want to place on the algorithm
    - ``main.py``: This is where you will write the code that your algorithm runs, or call code you write in other Python programs
    - ``README.md``: A helpful document for users of your algorithm
    - ``test.py``: A module for your algorithm's unit tests

Most of the time you will edit only ``main.py`` (and probably ``test.py``) directly. The development environment web interface handles updates to the other files for you.

algorithm.json
--------------

Even though the web interface updates this file on your behalf as you change your algorithm, you can edit it yourself if you wish. Here's what one looks like:

.. code-block:: json

	{
		"name": "getmaptiles_roi",
		"display_name": "Get Map Tiles In ROI",
		"description": "This algorithm will gather up map tiles at a given zoom level that intesect with the provided polygon. The source is the national map provided by USGS. All tiles will be written out to disk at a specified location. This location is also saved onto the chain ledger.",
		"version": "0.0.1",
		"license": "MIT",
		"private": false,
		"homepage": "https://tiledriver.com/developer",
		"required_parameters": [
			{
				"name": "roi",
				"description": "Polygon WKT to obtain tiles that intersect.",
				"display_name": "Polygon WKT",
				"data_type": "string",
				"field_type": "text",
				"help_text": "Enter well known text (WKT) for the polygon region to obtain intersecting tiles.",
				"min_value": null,
				"max_value": null,
				"default_value": "POLYGON((-77.0419692993164 38.9933585922412,-77.17311859130861 38.891887936025896,-77.03853607177736 38.790272111428706,-76.91013336181642 38.891887936025896,-77.0419692993164 38.9933585922412))",
				"custom_validation": null,
				"parameter_choices": [],
				"sort_order": 0
			},
			{
				"name": "zoom",
				"description": "Zoom level",
				"display_name": "Zoom level",
				"data_type": "integer",
				"field_type": "number",
				"help_text": "Enter an integer corresponding to the zoom level, 16 is max value supported.",
				"min_value": 5,
				"max_value": 16,
				"default_value": 14,
				"custom_validation": null,
				"parameter_choices": [],
				"sort_order": 1
			},
			{
				"name": "cache_path",
				"description": "Path to save gathered tiles to.",
				"display_name": "Tile Cache Location",
				"data_type": "string",
				"field_type": "text",
				"help_text": "Absolute path to directory for saving tiles",
				"min_value": null,
				"max_value": null,
				"default_value": "/tmp/tiles/map_tiles",
				"custom_validation": null,
				"parameter_choices": [],
				"sort_order": 2
			}
		],
		"optional_parameters": [],
		"outputs": [
			{
				"name": "image_chips_dir",
				"description": "Local path to directory of map tiles",
				"display_name": "Path To Tiles",
				"data_type": "string"
			}
		]
	}

Here's what each of the fields means:

============ ===========
Parameter    Description
============ ===========
name         A short name with no spaces, which **must** be
             unique across algorithms in your project
display_name A more descriptive name that will be displayed to
             the user
description  A long description of what the algorithm does
version      The algorithm version number in text form
license      A description of the license terms, using the SPDX
             identifier (https://spdx.org/licenses/)
private      If the algorithm is published to the Algorithm
             Registry, setting private to true will cause it
             cause it not to display in a Registry listing
homepage     A web address where more information can be found
             about the algorithm (could also be a link to a
             source code repository)
============ ===========

The algorithm.json file also defines input and output parameters. For inputs, there are "required_parameters" and "optional_parameters". The list of outputs is just called "outputs". Each parameter and each output has the same structure:

**Input Parameters**

================= ===========
Parameter         Description
================= ===========
name              A short name with no spaces, which **must** be
                  unique across parameters in this algorithm
display_name      A more descriptive name that will be displayed to
                  the user
description       A long description of what the parameter is for
data_type         The type of data the input parameter will accept
field_type        When displayed on a web form, which HTML field type to use
help_text         Text that would be displayed below a form field, providing
                  guidance on how to enter a value
min_value         If a numeric field, what is the minimum value the input should accept
max_value         If a numeric field, what is the maximum value the input should accept
default_value     The value to use if not provided (also will display in a web form)
custom_validation Custom validation rules (see below)
parameter_choices A comma-separated list of values that the field will accept
                  (often goes with a Select field type, but does not have to)
sort_order        On a web form, where should this field be displayed
                  relative to other input fields
================= ===========

**Outputs**

================= ===========
Parameter         Description
================= ===========
name              A short name with no spaces, which **must** be
                  unique across outputs of this algorithm
display_name      A more descriptive name that will be displayed to
                  the user
description       A long description of what the output is
data_type         The type of data the output will produce
================= ===========

It may seem like a lot of information for you to fill out, but the more detail you enter into algorithm.json the easier it will be for another developer to use what you create. An important part of the ATK is code sharing and reuse among the developer community.

main.py
-------

As stated earlier, most of your code will live in this file, or this file will point to other code you have written. When you create a new algorithm, the main.py will look like this:

.. code-block:: python

    from algorithm_toolkit import Algorithm, AlgorithmChain


    class Main(Algorithm):

        def run(self):
            cl = self.cl  # type: AlgorithmChain.ChainLedger
            params = self.params  # type: dict
            # Add your algorithm code here

            # Do not edit below this line
            return cl

It may not look like much, but there's a lot going on in these few lines of code.

Every time your algorithm runs, this ``run()`` routine will be called. As you'll notice, this ``Main`` class inherits from a class inside the ATK called ``Algorithm``. To see what the Algorithm class can do, check out the API section of these docs.

When this code runs, a dictionary called ``params`` will contain the data entered by a user or application calling the algorithm. In the get_map_tiles example above, params would look like this:

.. code-block:: python

    {
        'roi': 'POLYGON((-77.0419692993164 38.9933585922412,-77.17311859130861 38.891887936025896,-77.03853607177736 38.790272111428706,-76.91013336181642 38.891887936025896,-77.0419692993164 38.9933585922412))',
        'cache_path': '/tmp/tiles/map_tiles',
        'zoom': 14
    }

If you wanted to get the value of the ``zoom`` parameter in your code, you could refer to it like this:

.. code-block:: python

    zoom = params['zoom']

This is how your algorithm can receive the data it needs to operate. Notice that the ``zoom`` parameter is an integer in the params dictionary? The ATK does some nice things for you, such as making sure the data will be in the proper format you need it to be in (via the ``data_type`` field in the input parameter). If it's not, the user will be alerted to the problem and your code won't even run. This means you can focus on making use of the data inputs rather then spending time validating them.

You also probably noticed a reference to a mysterious variable called simply ``cl``. This stands for Chain Ledger, and is one of the most important aspects of the ATK. It's so important, :doc:`it has its own section in the docs <chain-ledger>`.

The short version is: the Chain Ledger is how you will provide outputs to other algorithms in the chain, and how you can see a history of everything the chain did after it runs. This is a hugely powerful and useful feature, because it gives you the ability to reproduce results at a later time.

You can put literally anything Python can create on the Chain Ledger. Most of the time, you will just place your algorithm's outputs on it. In the ``get_map_tiles`` example, the algorithm might do it like so:

.. code-block:: python

    cl.add_to_metadata('image_chips_dir', '/tmp/chips')

See the Chain Ledger section for more details on how this works.

Algorithm Input Validation
==========================

Data types
----------

The ``data_type`` field can be set to any one of the following options:

    - String (the default)
    - Integer
    - Float
    - Array (entered as a comma-separated list in a form field; the list members can be any data type)

Before an algorithm is called, the ATK uses the ``data_type`` to ensure that the correct type is being sent to the algorithm. If the value can be cast to the correct type, the ATK will do that. Otherwise an error will be raised.

Validation controls
-------------------

We said earlier that the ATK validates inputs before your code runs. In addition to the data type validation, you can set boundaries on what values will be accepted. Several fields within the parameter definition help with this: ``min_value``, ``max_value``, ``parameter_choices``, and ``custom_validation``. The first three are self-explanatory; let's look at ``custom_validation``.

custom_validation
-----------------

The ATK comes with a set of validators you can refer to in this field. They are:

.. py:data:: greaterthan

    The value must be greater than the value of another input parameter. Numeric inputs only.

    Example::

        "custom_validation": "greaterthan.another_input"

    where "another_input" is the name of the parameter whose value that must be smaller than this value.

    .. note::
        ``greaterthan`` and ``lessthan`` should come in pairs. In other words, if input1 should be greater than input2, input1 should use ``greaterthen.input2`` as its custom validation, and input2 should have ``lessthan.input1`` as its custom validation.

.. py:data:: lessthan

    The value must be less than the value of another input parameter. Numeric inputs only.

    Example::

        "custom_validation": "lessthan.another_input"

    where "another_input" is the name of the parameter whose value that must be greater than this value.

    .. note::
        ``greaterthan`` and ``lessthan`` should come in pairs. In other words, if input1 should be less than input2, input1 should use ``lessthen.input2`` as its custom validation, and input2 should have ``greaterthan.input1`` as its custom validation.

.. py:data:: evenonly

    The value must be an even integer. The ``data_type`` must also be Integer.

    Example::

        "custom_validation": "evenonly"

.. py:data:: oddonly

    The value must be an odd integer. The ``data_type`` must also be Integer.

    Example::

        "custom_validation": "oddonly"

.. py:data:: ^

    The value must conform to a regular expression pattern, defined after the caret (^) symbol. String inputs only.

    Example::

        "custom_validation": "^\d{3}-\d{3}-\d{4}$"

    This would require the input to have a US phone number-like format. See the `Python documentation <https://docs.python.org/2/howto/regex.html>`_ for regular expression syntax.

Outputs
-------

If your algorithm outputs a value, that value must also have a data type. When building chains, it's important to think about what type of output your algorithm produces because otherwise the next algorithm in the chain might not get a value of the right data type (and thus would never run, as we stated earlier). In fact, the Chain Builder prevents you from linking an output of one algorithm to the input of another if they're not the same data type (more on this in the Chain Builder section).

Using The Web Interface
=======================

When you click the Create a New Algorithm button on the Algorithms page, you will see the create/edit algorithm form:

.. image:: https://s3.amazonaws.com/atk-docs-images/working-with-algorithms-form.png

If you pull up the ``get_map_tiles`` algorithm, you can see the form filled out with the data from its algorithm.json:

.. image:: https://s3.amazonaws.com/atk-docs-images/working-with-algorithms-form-filled.png

Only the algorithm name and display name fields are required, but the more information you provide the easier it will be for another developer to use your algorithm.

License
-------

We provide several open source licenses that can be applied to your algorithm. When you click the license drop-down menu, you'll see the following options:

.. image:: https://s3.amazonaws.com/atk-docs-images/working-with-algorithms-form-filled-license.png

When you choose a license, a LICENSE file will be placed in your algorithm's folder corresponding to the open source license version you select. The text of these licenses come from the Open Source Initiative website (https://opensource.org/licenses).

If you do not wish to apply an open source license, you can choose one of two additional options: "Proprietary" or "See LICENSE File". Both of these options will create a blank LICENSE file in your algorithm's folder, and you can add whatever terms you deem appropriate.

Adding and editing parameters
-----------------------------

If you click the Edit button (looks like a pencil) for the ``roi`` parameter, you will see the create/edit input parameter form slide in from the right:

.. image:: https://s3.amazonaws.com/atk-docs-images/working-with-algorithms-form-parameter.png

Numeric parameters (integers and floats) look like this:

.. image:: https://s3.amazonaws.com/atk-docs-images/working-with-algorithms-form-integer-parameter.png


Adding and editing Outputs
--------------------------

If you click the Edit button (looks like a pencil) for the ``image_chips_dir`` output, you will see the create/edit output form slide in from the right:

.. image:: https://s3.amazonaws.com/atk-docs-images/working-with-algorithms-form-output.png

Head over to :doc:`creating-your-first-algorithm` to see this form in action.
