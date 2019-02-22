.. _working-with-chains:

===================
Working With Chains
===================

Now you've seen how to create a single algorithm and make it do something. Pretty cool, but the power of the ATK really shines with processing chains.

What Is A Processing Chain?
===========================

Simply put, a processing chain in the ATK is a series of algorithms, each linking to the next via output parameters.

Imagine a chain like a set of tasks. When you mail a package to someone, your task is complete when you drop it off at the shipping company. But to get to the recipient the package has to go through a series of waystations, each with its own tasks. The whole chain might look like this:

    1. You drop off your package at the post office in the small town you live in
    2. The post office sends it to a central office somewhere else in the state
    3. The state hub sends the package to another hub
    4. That hub sends the package to a local office near the recipient
    5. A local delivery person drops it off at the recipient's location

At each step, information is read about where the package goes next. In addition, the final destination address has to be carried along the route so it ends up in the right place.

Think of the next destination along the route as an input to an algorithm, the journey between points as algorithms, and the information contained in the overall route as the Chain Ledger, and you've basically got the idea. After the package is delivered, you could do back and see all the steps the package went through, how long it took to reach each point, and so on.

How Does This Actually Work?
============================

You define algorithms just like you did in the last section :doc:`creating-your-first-algorithm`. Then, you link those algorithms together to create a workflow, or processing chain. Then you can test the chain using our test harness.

Examining The Example Project
=============================

Sometimes the best way to learn is to read working code. The example project comes with three algorithms and a processing chain; let's examine those.

Go to the Chain Builder in the web interface and select the "map_tiles" chain. This is what it looks like:

.. image:: https://s3.amazonaws.com/atk-docs-images/dev-environment-chain-builder-show-chain.png

The left side of this screen contains the algorithms installed in your project. To the right of that and taking up most of the screen, is the Chain Builder Canvas. As you can see, "map_tiles" links the algorithms together in the following order (top to bottom):

    1. Get Map Tiles in ROI
    2. Stitch together tiles
    3. Output Image to Web

You'll also notice that each algorithm is getting its data from different sources. The three inputs for "Get Map Tiles in ROI" come from the user, but the other two algorithms get data from algorithms that came before. "Stitch together tiles" gets its one input value from an *output* of "Get Map Tiles in ROI" called "image_chips_dir". "Stitch together tiles" also provides two outputs for "Output Image to Web": "image_path" and "image_bounds".

Let's take a step back and talk about what this chain actually does. In the first algorithm, this chain acquires map tiles from a public tile server (provided by the U.S. Geological Survey) for a given region of interest (ROI). The chain then hands those tiles over to a second algorithm, which stitches the image tiles together into a GeoTIFF mosaic that is orthorectified. Finally, the chain hands the mosaic to a third algorithm that converts the GeoTIFF to a web format (PNG) and sends the PNG data along with the geographic bounding box data back to the client.

To use this chain, it's not really necessary for you to know *how* the individual algorithms do what they do. All you need to know is what information goes in, and what comes out. However, because you have the source code for the algorithms in the chain, you can see how it all works.

That's the beauty of the ATK platform: you can use it to do some really complicated things and have it "just work," and you can also see the details about how the work was done.

We built the ATK specifically to have these two capabilities. Many who use the ATK rely on its power to make their data processing lives easier, while others need to tweak the algorithms in order to understand fully the results of a chain run.

chains.json
-----------

The Chain Builder provides a graphical view for a chain's structure and lets you change how it's put together. Under the hood, the chain is defined by a JSON file in your project called ``chains.json``. Here's what one looks like with the example project:

.. code-block:: json

    {
        "my_first_chain": [
            {
                "algorithm": "my_first_algorithm",
                "parameter_source": "user"
            }
        ],
        "map_tiles": [
            {
                "algorithm": "getmaptiles_roi",
                "parameter_source": "user"
            },
            {
                "parameters": {
                    "image_chips_dir": {
                        "source": "chain_ledger",
                        "occurrence": "first",
                        "key": "image_chips_dir",
                        "source_algorithm": "getmaptiles_roi"
                    }
                },
                "algorithm": "stitch_tiles"
            },
            {
                "parameters": {
                    "image_bounds": {
                        "source": "chain_ledger",
                        "occurrence": "first",
                        "key": "image_bounds",
                        "source_algorithm": "stitch_tiles"
                    },
                    "image_path": {
                        "source": "chain_ledger",
                        "occurrence": "first",
                        "key": "image_path",
                        "source_algorithm": "stitch_tiles"
                    }
                },
                "algorithm": "output_image_to_client"
            }
        ]
    }

We threw in the "my_first_chain" from the previous section as well. Focusing on "map_tiles", you can see the same structure depicted in graphical form here:

    - "getmaptiles_roi" gets its input from "user"
    - "stitch_tiles" its one input from "getmaptiles_roi"
    - "output_image_to_client" gets both of its inputs from "stitch_tiles"

If an algorithm gets all of its inputs from the user, you will see "parameter_source": "user". Otherwise, the next link in the processing chain will have a "parameters" dictionary applied, with each parameter named as a key: value pair. If the value comes from the user, it will read:

.. code-block:: json

    {
        "source": "user"
    }

Otherwise, it will have the additional fields as shown here::

    {
        "source": "chain_ledger",
        "occurrence": "first",
        "key": "",                 <-- name of parameter in source algorithm
        "source_algorithm": ""     <-- name of the source algorithm
    }

What is 'occurrence'?
---------------------

Some processing chains use the same algorithm more than once. In these cases, the "occurrence" flag is a mechanism to tell the ATK which occurrence of the algorithm to use for this input. The Chain Builder algorithm blocks have a small drop-down menu for the chain developer to use to indicate this value.

The Chain In Action
===================

When you pull up a chain in the Test Run page, you will see its web form:

.. image:: https://s3.amazonaws.com/atk-docs-images/dev-environment-test-run.png

What you see here is probably making more sense now. This view is presented by the ATK as an interface to the processing chain. In fact, the data to run a chain does not have to come from a web form at all; however, it's a convenient way to explain how this all works.

Copy and paste your API Key into the field provided. You'll notice that all the other fields are filled out: those are the default values defined by the algorithm creator. Especially in the case of the ROI field, this can really make a user's life easier. Let's keep these defaults and click "Run Algorithm Chain".

.. image:: https://s3.amazonaws.com/atk-docs-images/working-with-chains.png

When the chain runs, you'll see some status information and a progress bar indicating how far along the chain we are. An algorithm developer can also pass algorithm progress to the user as we'll see in another section.

In this case, the final output to the client appears in a web map. How did this happen?

Chain outputs
-------------

In the section :doc:`creating-your-first-algorithm`, you output text to the test client. The ATK allows you to output a variety of other formats:


.. py:data:: geo_raster

    Send a PNG or JPG to the client along with the geographic bounds (in lat,lon pairs) of the image. The image will display in a web map.

    Format of ``chain_output_value``:

    .. code-block:: python

        {
            "output_type": "geo_raster",
            "output_value": {
                "extent": "",
                "raster": ""
            }
        }

    - ``extent`` is a nested array of lat,lon values (using the default ROI, the value would be: [[38.99357205820944,-77.18994140625], [38.788345355085625,-76.90429687500001]])
    - ``raster`` is a base64 encoded string of the image data

.. py:data:: geojson

    Send a GeoJSON object to the client. It will display in a web map.

    Format of ``chain_output_value``:

    .. code-block:: python

        {
            "output_type": "geojson",
            "output_value": {}
        }

    - the ``output_value`` must be properly formatted GeoJSON

.. py:data:: json

    Send a JSON object to the client. It will display in a text box.

    Format of ``chain_output_value``:

    .. code-block:: python

        {
            "output_type": "json",
            "output_value": {}
        }

.. py:data:: csv

    Send a comma-delimited text file to the client. It will display in a text box.

    Format of ``chain_output_value``:

    .. code-block:: python

        {
            "output_type": "csv",
            "output_value": {
                "data": ""
            }
        }

    - ``data`` should be a series of lines of comma-delimited text separated by newline characters

.. py:data:: binary

    Send a binary file to the user. The user will be prompted to download the file.

    Format of ``chain_output_value``:

    .. code-block:: python

        {
            "output_type": "binary",
            "output_value": {
                "mimetype": "",
                "file": "",
                "filename": ""
            }
        }

    - ``mimetype`` is the MIME encoding for the file; if not provided, the file will be rejected by the test client (e.g.: "application/pdf")
    - ``file`` is a base64 encoded string of the binary file
    - ``filename`` is the name of the file

.. py:data:: text

    Send a string to the client.

    Format of ``chain_output_value``:

    .. code-block:: python

        {
            "output_type": "text",
            "output_value": ""
        }
