.. _creating-your-first-algorithms:

=============================
Creating Your First Algorithm
=============================

Let's dive into algorithm development with everyone's favorite trope: the Hello World program!

We'll use the development environment web interface to set up the algorithm, then modify the code in main.py to enhance the functionality of our algorithm.

Creating a Project
==================

We'll need an algorithm project to start things off. Take a look at the :doc:`quick_start` documentation for how to create a new project with the example project included. Having the example available is a great reference for how to make your own algorithms.

Setting Things Up
=================

As you'll recall from the last page, the create new algorithm form looks like this (click the Create a New Algorithm button from the Algorithms page):

.. image:: https://s3.amazonaws.com/atk-docs-images/working-with-algorithms-form.png

Let's fill in some details about our algorithm. We'll name it "my_first_algorithm", give it a brief description, and choose the MIT license (we're feeling generous today):

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-1.png

Click "Save Algorithm" and you'll see your algorithm appear in the list:

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-2.png

That's it! Notice we did not even have to name any inputs or outputs in order to create the algorithm. It will be more useful once we have those, but for now let's leave it at that.

What Just Happened?
===================

After we clicked the Save button, the ATK created a new folder in our project called **algorithms/my_first_algorithm**. Within that folder, you'll find the same files described in :doc:`working-with-algorithms`:

.. code:: bash

    __init__.py
    algorithm.json
    LICENSE
    main.py
    README.md
    test.py

The algorithm.json file contains the basic information you entered:

.. code:: json

    {
        "description": "This is my first algorithm, and I'm proud of it.",
        "display_name": "My First Algorithm",
        "homepage": "",
        "license": "MIT",
        "name": "my_first_algorithm",
        "optional_parameters": [],
        "outputs": [],
        "private": false,
        "required_parameters": [],
        "version": "0.0.1"
    }

Now What?
=========

We have the basic structure of an algorithm; now we need to make it do something.

Open up the ``main.py`` file in your new algorithm folder, using your favorite text editor or programming tool. You'll see the following code:

.. code-block:: python

    from algorithm_toolkit import Algorithm, AlgorithmChain


    class Main(Algorithm):

        def run(self):
            cl = self.cl  # type: AlgorithmChain.ChainLedger
            params = self.params  # type: dict
            # Add your algorithm code here

            # Do not edit below this line
            return cl

:doc:`working-with-algorithms` describes the basics of what's going on here.

In order to make our Hello World program complete, we need to have it greet the world with its friendly message. To send a message to the user or calling function, we need to make use of the Chain Ledger. You'll recall from :doc:`working-with-algorithms` that the Chain Ledger is a Python dictionary, and you can access it using the variable ``cl`` in your algorithm.

We'll use a special key the Chain Ledger maintains: ``chain_output_value``. Essentially, this key outputs a message or other result to the client. The output value can be unstructured text, JSON, CSV, or even binary files. For our program we'll just use text. Here's how you would output the famous greeting in your algorithm:

.. code-block:: python

    # Add your algorithm code here

    chain_output = {
        'output_type': 'text',
        'output_value': 'Hello World!'
    }
    cl.add_to_metadata('chain_output_value', chain_output)

    # Do not edit below this line
    return cl

As you can see, ``chain_output_value`` is itself a dictionary with two keys: ``output_type`` ("text" in this case) and ``output_value`` ("Hello World!"). You use the Chain Ledger's ``add_to_metadata`` function to set the value of this key, and the function takes two arguments: the key name ("chain_output_value") and the key value (our dictionary).

Save the ``main.py`` file.

Running The Algorithm
=====================

In order to run this code, we need to set up a basic chain. The ATK does not run individual algorithms: it requires a chain, and once you create one you can use the Test Run harness provided in the development environment.

In the web interface, click the link for Chain Builder. You'll see your algorithm listed along with the example project algorithms:

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-3.png

When you click the name of your algorithm, you'll see a block representing it:

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-4.png

Drag the block to the right onto the Chain Canvas. You'll get a prompt to give this chain a name:

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-5.png
    :width: 50%
    :align: center

After that you'll see your chain, with your single algorithm:

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-6.png

Believe it or not, that's it! However modest, you now have an algorithm processing chain.

The chain name will now appear in the Test Run menu at the top of the screen. Select it, and you'll see a basic web form:

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-7.png

Because we don't have any input parameters, there's not much here. You will however need your API key.

What is my API key?
-------------------

The API key is a simple security mechanism to make sure no one runs your chain or does anything with your algorithm project unless you want them to. To find your key, open the ``.env`` file in your algorithm project, and copy the value in ATK_API_KEY (don't copy the quotation marks).

Paste the value into the API Key form field. Then click "Run Algorithm Chain".

This chain will run pretty fast, since you're just outputting text to the screen. After it's finished, you'll see this:

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-8.png

There it is! Our welcome message to the world.

Adding An Input
===============

Now that we have a working algorithm and chain, we begin to see all kinds of possibilities. Let's start by allowing our greeting to be more personal.

Edit your algorithm in the web interface by clicking the Edit button next to its name in the Algorithms page. Then click Add Parameter.

We'll add a required input for the name of the person we want to greet. Fill out the relevant fields like this:

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-9.png

Click the Save button on the parameter form. You'll see the parameter listed:

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-10.png

Now click Save Algorithm.

If you open your algorithm.json file, you'll see the new parameter has been added to the definition:

.. code-block:: json

    {
        "description": "This is my first algorithm, and I'm proud of it.",
        "display_name": "My First Algorithm",
        "homepage": "",
        "license": "MIT",
        "name": "my_first_algorithm",
        "optional_parameters": [],
        "outputs": [],
        "private": false,
        "required_parameters": [
            {
                "custom_validation": "",
                "data_type": "string",
                "default_value": "",
                "description": "What should I call you?",
                "display_name": "Name of person to greet",
                "field_type": "text",
                "help_text": "Please enter your full name",
                "max_value": "",
                "min_value": "",
                "name": "greeting_name",
                "parameter_choices": "",
                "required": true,
                "sort_order": 0
            }
        ],
        "version": "0.0.1"
    }

Since we added an input parameter, we need to modify the chain to tell the ATK how the input will get a value. Click Chain Builder, then select your chain from the drop-down menu:

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-11.png
    :width: 50%
    :align: center

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-12.png

Look at that! The ATK figured out that you wanted the user to input a value for the new field without you having to do anything. Awesome!

There are other options for how an input gets its value, which we'll explore in a later section. For now, let's run this chain using Test Run again:

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-13.png

You'll see the new input parameter on the form, along with the help text explaining what the field is for. If you hover over the info icon to the right, you'll see the description you entered for the parameter:

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-14.png
    :width: 50%
    :align: center

Click Run Algorithm Chain.

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-15.png

Huh, you got the same result. How come?

Using The Input
===============

Your algorithm code needs to do something with the input value. Let's open ``main.py`` again and change the code like this:

.. code-block:: python

    # Add your algorithm code here

    name = params['greeting_name']
    msg = 'Hello, %s!' % name

    chain_output = {
        'output_type': 'text',
        'output_value': msg
    }
    cl.add_to_metadata('chain_output_value', chain_output)

    # Do not edit below this line
    return cl

Here you see we're using the ``params`` dictionary to take the parameter called "greeting_name" and assign it to a variable. The ATK saves the user input in that key in ``params``. While you're developing, it can be helpful to open the algorithm.json file if you forget what you named a parameter.

Then we create the new greeting and assign it to the "output_value" for placing on the Chain Ledger. Looks like we're done here.

Save the changes to ``main.py``

.. note::
    The development environment can detect some changes to your algorithm code and restart itself so you don't have to remember to do it. When that happens, you'll see lines like this in your Terminal window:

    .. code-block:: bash

         * Detected change in '/myproject/algorithms/my_first_algorithm/main.py', reloading
         * Restarting with stat
         * Debugger is active!
         * Debugger PIN: 225-327-370

Now go back to Test Run and run your chain. This time you'll see the right greeting:

.. image:: https://s3.amazonaws.com/atk-docs-images/creating-your-first-algorithm-16.png

This is fantastic. You can create algorithms that accept user input, process that input, and display something to the user. In all, you wrote six lines of code and filled out a couple of forms. Not bad.

Where To Go From Here?
======================

Although this was a basic example, you've seen how most of the development environment works and how you can use the ATK to run an application. You're ready to take on a bigger project.

We suggest you go through the next section :doc:`working-with-chains` to understand how chains work and how to manipulate them. Then, you can run through the :doc:`tutorial` to see how you can practically use processing chains. You'll also learn how to log information and provide status updates to the user.
