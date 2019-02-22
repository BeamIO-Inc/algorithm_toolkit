.. _tutorial:

==================
Tutorial: Do Maths
==================

OK, with your Hello World algorithm under your belt, it's time to see more of what the ATK can really do. In this tutorial, you'll learn the following:

    - How to chain multiple algorithms together
    - How to log messages to a file from your algorithms
    - How to provide status updates to the user
    - How to use the Chain Ledger
    - How to test your algorithm

We're calling this "Do Maths" because that's what the chain will do for us. We'll create a series of algorithms that together calculate a value, and present that value to the user. This tutorial assumes you went through the Hello World example earlier, so we won't go into detail for areas covered in that section.

Let's dive right in!

Setting Up
==========

First, create a project. You can use the same one you created for :doc:`creating-your-first-algorithm`.

Next, we'll create an algorithm called "add_numbers". It should have two required parameters and one output:

**Parameters**:
    - ``starting_value``: an integer
    - ``number_to_add``: another integer

**Output**:
    - ``result``: yet another integer

If you went through the :doc:`creating-your-first-algorithm` section, this should be a breeze. Your algorithm form should look like this:

.. image:: https://s3.amazonaws.com/atk-docs-images/tutorial-1.png

The First Algorithm
===================

Save your new algorithm, copy the code below and paste into the algorithm's ``main.py``:

.. code-block:: python

    import time
    from algorithm_toolkit import Algorithm, AlgorithmChain


    class Main(Algorithm):

        def run(self):
            cl = self.cl  # type: AlgorithmChain
            params = self.params  # type: dict
            # Add your algorithm code here

            starting_value = params['starting_value']
            number_to_add = params['number_to_add']

            result = starting_value + number_to_add

            cl.add_to_metadata('result', result)

            status_msg = 'result so far: ' + str(result)
            cl.set_status(status_msg)

            chain_output = {
                'output_type': 'text',
                'output_value': status_msg
            }
            cl.add_to_metadata('chain_output_value', chain_output)
            time.sleep(1)

            # Do not edit below this line
            return cl

We've added a bunch of code to this algorithm. Let's go through it step by step:

::

    import time

We're adding a delay for testing purposes so that you can see the chain status messages appear. Otherwise, this chain would run too quickly.

::

    starting_value = params['starting_value']
    number_to_add = params['number_to_add']

Here we're creating local variables for parameters coming in from the ATK. Because we specified Integer data types, we can be sure that these are integers.

::

    result = starting_value + number_to_add

This line simply adds the two values together, which is the primary purpose of this algorithm.

::

    cl.add_to_metadata('result', result)

This places the result of the add operation onto the Chain Ledger. Note that we used the key "result". This is important, because it's the name of the output we defined for this algorithm. That means that another algorithm that comes after this one can receive and use this value (which we said we would provide in the algorithm definition).

The other important point here is that we're placing the value onto the Chain Ledger as an integer. Since we specified that the "result" output would be of data type Integer, we have to keep our word.

::

    status_msg = 'result so far: ' + str(result)
    cl.set_status(status_msg)

These two lines create a status message we will send to the client. Using the ``set_status()`` function of the Chain Ledger places our status message into a special global variable that can be retrieved by other parts of the ATK. When we run the chain, you'll see this in action.

::

    chain_output = {
        'output_type': 'text',
        'output_value': status_msg
    }
    cl.add_to_metadata('chain_output_value', chain_output)

This should look familiar. We're outputting the same status message to ``chain_output_value`` in case this is the last algorithm in the chain.

.. note::
    You should always output something to the chain's ``chain_output_value`` in case your algorithm is last in a chain. It's not a requirement, but it's a good practice.

::

    time.sleep(1)

This is the delay timer. Each algorithm will wait one second before completing.

That's it! We then return the modified Chain Ledger (``cl``) to the ATK for it to pass to the next algorithm in the chain.

Testing Your Algorithm
======================

Although we said earlier that the ATK doesn't run individual algorithms, we can write code to test each algorithm. If you've written tests for Python programs before, then you're in luck: the ATK uses Python's built-in testing tools.

Our algorithm has basically only one thing we need to test: does it add two numbers together correctly? To test this, we'll make use of some functionality included in the ATK.

The test module
---------------

When you create a new algorithm, the ATK will create a ``test.py`` module in the algorithm's folder. It will look like this:

.. code-block:: python

    from algorithm_toolkit import AlgorithmTestCase

    from main import Main


    class MainTestCase(AlgorithmTestCase):

        def runTest(self):
            # configure params for your algorithm
            self.params = {}

            self.alg = Main(cl=self.cl, params=self.params)
            self.alg.run()

            # Add tests and assertions below

Let's see what's happening here.

.. code-block:: python

    from algorithm_toolkit import AlgorithmTestCase

We're making use of a class that the ATK makes available to us: ``AlgorithmTestCase``. This class sets up our tests and provides two attributes and two helper functions:

    - ``cl``: a Chain Ledger object for testing purposes
    - ``params``: an empty dictionary you can use to "fake" inputs to your algorithm
    - ``check_metadata()``: this ensures that the value we expect shows up on the Chain Ledger
    - ``check_status()``: this ensures that we are writing status information correctly

.. code-block:: python

    from main import Main

Here we're simply importing the Main class in our algorithm's ``main.py`` module.

.. code-block:: python

    self.alg = Main(cl=self.cl, params=self.params)

This looks complicated but it really isn't. All this code does is call your algorithm's Main class and pass in the same ``cl`` and ``params`` attributes you're used to seeing in the algorithm code.

.. code-block:: python

    self.alg.run()

This calls your algorithm's ``run()`` function.

With this structure, you can test anything you want about your algorithm. To test "add_numbers", we'll need some numbers. Modify the ``self.params = {}`` line as follows:

.. code-block:: python

    self.params = {
        'starting_value': 3,
        'number_to_add': 5
    }

Here we "fake" our algorithm's inputs. We'll make sure "add_numbers" can add 3 + 5 and get the right result.

Next, add these two assertions:

.. code-block:: python

    self.assertTrue(self.check_metadata('result', 8))
    self.assertTrue(self.check_status('result so far: 8'))

We're making use of the two helper functions mentioned above. Here we make sure that the number 8 is added to a key called "result" on the Chain Ledger. We also make sure that we're writing the correct status message for the user.

The whole ``test.py`` should look like this:

.. code-block:: python
    :emphasize-lines: 11,12,20,21

    from algorithm_toolkit import AlgorithmTestCase

    from main import Main


    class AddNumbersTestCase(AlgorithmTestCase):

        def runTest(self):
            # configure params for your algorithm
            self.params = {
                'starting_value': 3,
                'number_to_add': 5
            }

            self.alg = Main(cl=self.cl, params=self.params)
            self.alg.run()

            # Add tests and assertions below

            self.assertTrue(self.check_metadata('result', 8))
            self.assertTrue(self.check_status('result so far: 8'))

Running the test
----------------

Stop the development environment by typing ``^C`` in your Terminal. Use the CLI ``test`` command to run your tests:

.. code-block:: bash

    alg test

Simple, isn't it? Note that this command will check all of the algorithms in your project and run any tests it finds. If you only want to test one algorithm, just include the algorithm's name:

.. code-block:: bash

    alg test add_numbers

After you run the test, you should see a message like this in your Terminal window:

.. code-block:: bash

    runTest (test.AddNumbersTestCase) ... result so far: 8
    ok

    ----------------------------------------------------------------------
    Ran 1 test in 0.001s

    OK

Not very exciting, but good news: our test passed.

Adding more tests
-----------------

Notice that the message says "Ran 1 test". This may seem odd, since we made two assertions. The way Python's unittest works, the test function (``runTest()`` in this case) counts as one test no matter how many assertions you make.

Some developers like to split things out so that each test only makes one assertion. You can easily add more tests by changing things up a bit. Let's split our assertions into a test called ``test_metadata()`` and one called ``test_status()``:

.. note::
    When you have a single test in a Python TestCase, you typically override the ``runTest()`` function. When you have multiple tests, you name each function ``test_`` and add the name of the test. See Python's `documentation <https://docs.python.org/2/library/unittest.html>`_ on ``unittest`` for more info.

Here's our new ``test.py``:

.. code-block:: python

    from algorithm_toolkit import AlgorithmTestCase

    from main import Main


    class AddNumbersTestCase(AlgorithmTestCase):

        def runTest(self):
            self.alg = Main(cl=self.cl, params=self.params)
            self.alg.run()

        def test_metadata(self):
            # configure params for your algorithm
            self.params = {
                'starting_value': 3,
                'number_to_add': 5
            }
            self.runTest()

            # Add tests and assertions below

            self.assertTrue(self.check_metadata('result', 8))

        def test_status(self):
            # configure params for your algorithm
            self.params = {
                'starting_value': 17,
                'number_to_add': 23
            }
            self.runTest()

            # Add tests and assertions below

            self.assertTrue(self.check_status('result so far: 40'))

We keep the ``runTest()`` function and give it the job of calling the ``Main`` class and ``run()`` function from our algorithm. This helps eliminates some redundancy between tests. Notice that we're also changing up the input parameters just to make sure everything's working. Use `alg test` again and you should see two tests:

.. code-block:: bash

    test_metadata (test.AddNumbersTestCase) ... ok
    test_status (test.AddNumbersTestCase) ... ok

    ----------------------------------------------------------------------
    Ran 2 tests in 2.006s

Now you can add as many tests as you like.


The Remaining Algorithms
========================

We need to create three more algorithms that are basically copies of this one with a few tweaks. If your development environment is stopped, just start it again with:

.. code-block:: bash

    alg run

Copy algorithm
--------------

Here's a handy feature. From the Algorithms page in the web interface, click the "Copy" button next to the "add_numbers" algorithm. When you do, you'll see this:

.. image:: https://s3.amazonaws.com/atk-docs-images/tutorial-2.png

An exact duplicate of the "add_numbers" algorithm is now in your list, with a new name ("add_numbers_copy"). Now you can just make changes to that algorithm instead of creating one from scratch.

Click the "Edit" button next to the new algorithm. Change it's name to "subtract_numbers". Also change the display name and description, but keep everything else the same.

Modify subtract_numbers
-----------------------

You really just need to change two lines in the code from "add_numbers". It should look like this when you're done:

.. code-block:: python

    import time
    from algorithm_toolkit import Algorithm, AlgorithmChain


    class Main(Algorithm):

        def run(self):
            cl = self.cl  # type: AlgorithmChain
            params = self.params  # type: dict
            # Add your algorithm code here

            starting_value = params['starting_value']
            number_to_subtract = params['number_to_subtract']

            result = starting_value - number_to_subtract

            cl.add_to_metadata('result', result)

            status_msg = 'result so far: ' + str(result)
            cl.set_status(status_msg)

            chain_output = {
                'output_type': 'text',
                'output_value': status_msg
            }
            cl.add_to_metadata('chain_output_value', chain_output)
            time.sleep(1)

            # Do not edit below this line
            return cl

Add two more algorithms
-----------------------

Now you'll create two more algorithms: "multiply_numbers" and "divide_numbers" by copying either "add_numbers" or "subtract_numbers". After you're done your Algorithms page will look like this:

.. image:: https://s3.amazonaws.com/atk-docs-images/tutorial-3.png

Make sure to modify these two algorithms' ``main.py`` files in the same way you changed "subtract_numbers".

Creating The Chain
==================

Now go to the Chain Builder so we can create our do_maths chain. Select "Add two numbers together" (or whatever display name you gave to the "add_numbers" algorithm). Drag its block into the Canvas:

.. image:: https://s3.amazonaws.com/atk-docs-images/tutorial-4.png

When the pop-up message appears asking for a chain name, call it "do_maths".

Notice that when you clicked the "add_numbers" algorithm, in addition to the Algorithm block there was an Output Field block as well. This is important to remember, and we'll be using it soon.

You now need to tell the ATK where the values for this new algorithm will come from. In this case, they are both User Inputs. You can either drag the User Input block into the two inputs, or highlight the "add_numbers" block in the canvas and hit the letter "u" on your keyboard. When you're done, you should have this:

.. image:: https://s3.amazonaws.com/atk-docs-images/tutorial-5.png

Now, drag "subtract_numbers" onto the canvas and attach it to "add_numbers". You'll hear a slight click when the two come together. The Canvas should look like this:

.. image:: https://s3.amazonaws.com/atk-docs-images/tutorial-6.png

Linking an output to an input
-----------------------------

Now here's the really critical part. The "starting_value" for this second algorithm should come from the result of the first algorithm's addition operation. How do we indicate that?

Remember the Output Field block from earlier? We'll use it here. Click the "add_numbers" algorithm on the left-side list. You'll see the Output Field block like so:

.. image:: https://s3.amazonaws.com/atk-docs-images/tutorial-7.png

Now, drag the Output Field block and attach it to the "starting_value" input of "subtract_numbers". The Canvas should now look like this:

.. image:: https://s3.amazonaws.com/atk-docs-images/tutorial-8.png

Next, the "number_to_subtract" input should come from the user, so drag the User Input over and connect it to that input.

Continue building the chain this way, bringing in "multiply_numbers" and then "divide_numbers". In each case, the "starting_value" should come from the algorithm that preceded it and the "number_to_multiply" or "number_to_divide" should come from the user.

When you're done, your chain should look like this:

.. image:: https://s3.amazonaws.com/atk-docs-images/tutorial-9.png

Running The Chain
=================

Now let's try it out! Select the "do_maths" chain from the Test Run menu. You'll see our new web form:

.. image:: https://s3.amazonaws.com/atk-docs-images/tutorial-10.png

Notice that only the first algorithm in the chain ("add_numbers") has a Starting Value field. That's because the Starting Value for the other algorithms come from the Chain Ledger, not the user.

Enter some numbers (and your API Key) and click the "Run Algorithm Chain" button. You should see the status messages appear in the status window, and the progress bars move each second. The result of the calculation will depend on what numbers you entered.

.. image:: https://s3.amazonaws.com/atk-docs-images/tutorial-11.png

Logging Information
===================

Sometimes as a developer you want messages to be logged when there are problems, or just to keep a record of the status of your program. The ATK provides functionality to help you do this.

Let's say you want to record a log message after the last algorithm in the chain runs, and include the result of the maths operation. This is provided to the user at runtime, but maybe you want to save it for later.

Your algorithm project includes a folder called **logs**, and in that folder is a file called ``app.log``. If you've run any chains so far, you will see some informational messages in there already telling you how long your chains took to run. We want to use this same log file to record our maths results.

Adding a log message is easy. Your algorithm has an attribute called ``logger``, which you can use like so:

.. code-block:: python

    self.logger.info('My info message')

As you can see, we're passing a string to the log that reads "My info message". We're also calling it an "info" message by using ``self.logger.info()``. This part of the command is important: it refers to the LogLevel used by Python's ``logging`` library. There are essentially five log levels in order from most to least severe:

    1. ``CRITICAL``
    2. ``ERROR``
    3. ``WARNING``
    4. ``INFO``
    5. ``DEBUG``

When you write a message to the log file using the corresponding function (e.g.: ``info()``), the log level is checked against the current Log Handler's log level. By default, the log handler used by the ATK is set to ``DEBUG``. This means that any message as or more severe than ``DEBUG`` will be written to the log file.

If you raise the handler's LogLevel to something else (say ``ERROR``), then an ``INFO`` message will not appear in the logs. See :doc:`atk-project` for more information on configuring your project.

How this looks in your algorithm
--------------------------------

To write the final result of your maths operation to the log file, you can do this in "divide_numbers":

.. code-block:: python

    import time
    from algorithm_toolkit import Algorithm


    class Main(Algorithm):

        def run(self):
            cl = self.cl
            params = self.params
            # Add your algorithm code here

            starting_value = params['starting_value']
            number_to_divide = params['number_to_divide']

            result = starting_value / number_to_divide

            cl.add_to_metadata('result', result)

            status_msg = 'result so far: ' + str(result)
            cl.set_status(status_msg)

            chain_output = {
                'output_type': 'text',
                'output_value': status_msg
            }
            cl.add_to_metadata('chain_output_value', chain_output)
            time.sleep(1)

            self.logger.info('FINAL RESULT: ' + str(result))  # write the final result to the log

            # Do not edit below this line
            return cl

Run the chain again and you'll see your new log message in ``app.log``. Experiment with other log messages and levels to understand how this simple but powerful feature works.

Next Steps
==========

There's lots you could add to this project. Here are a few things to figure out on your own:

    - Make some or all of the algorithm input parameters float values instead of integers
    - Rearrange the algorithms to perform the maths operation in a different order
    - Use an algorithm more than once in the chain
    - Make the maths more complicated (factorials? cube roots? trigonometric functions?)

Hopefully you can see the potential in the ATK. Without much code, you successfully ran a set of tasks and could be confident that the inputs and outputs would be present and what you expected to get.

The rest of these docs have some in-depth information about how the ATK works, and will introduce you to some other tools and platforms to enhance the ATK and make it even more useful.
