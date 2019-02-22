.. _chain-ledger:

================
The Chain Ledger
================

The Chain Ledger is a powerful feature of the ATK. It lets you store arbitrary data throughout the course of a chain run. By default the Chain Ledger will contain all the inputs provided to each algorithm in the chain.

In your algorithms, you can store and retrieve values from the Ledger easily by using the ``cl`` object in your algorithm's ``main.py`` (see :doc:`working-with-algorithms`). Here's how:

.. code-block:: python

    # store a value
    cl.add_to_metadata('my key', 'my value')

    # retrieve a value stored by your algorithm
    cl.get_from_metadata('my key')

Chain History
=============

Throughout its life, your processing chain stores values on the Ledger. Often, you'll want to retrieve a value stored by an earlier algorithm in the chain. If you want a value from the algorithm that immediately preceded the current one, typically you would use an **output** and add that output to the first algorithm's definition (again, see :doc:`working-with-algorithms`). Then you would map the output to the second algorithm's input where appropriate (see :doc:`working-with-chains`).

Sometimes however, you want a value from several algorithms ago. The chain's metadata dictionary is cleaned out after each algorithm runs, so you won't see it if you use ``cl.get_from_metadata()``. What do you do in this case?

You can use the chain history, which is basically a copy of each algorithm's metadata after it runs and before the metadata are cleared. To retrieve a value from an earlier algorithm:

.. code-block:: python

    # if you know the numeric index of the algorithm in the chain
    cl.get_from_history(0, 'my key')

    # if you don't
    cl.search_history('my key', 'my_algorithm')
    # returns a list of values, one for each 'my key'
    # instance in every 'my_algorithm' in the chain history

    # or, just find the key name in any algorithm
    cl.search_all_history('my key')

    # find out if an algorithm is in the history
    cl.is_algo_in_history('my_algorithm')
    # returns True if it's there, False otherwise

Historic record
---------------

After your chain runs, you will find a new JSON file in a folder called **/history** in your algorithm project. The file name will match a random string of characters the ATK uses to uniquely identify your chain run (this is how it can report status information to you).

Here's an example of a history file from the example project:

.. code-block:: json

    {
        "atk_chain_metadata": [
            {
                "algorithm_name": "getmaptiles_roi",
                "algorithm_params": {
                    "roi": "POLYGON((-77.0419692993164 38.9933585922412,-77.17311859130861 38.891887936025896,-77.03853607177736 38.790272111428706,-76.91013336181642 38.891887936025896,-77.0419692993164 38.9933585922412))",
                    "zoom": 14
                },
                "image_filenames": "/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6273_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6273_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6273_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6272_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6272_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6272_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6272_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6272_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6271_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6271_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6271_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6271_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6271_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6271_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6271_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4681_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4689_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4680_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4681_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4689_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4690_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4679_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4680_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4681_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4689_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4690_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4691_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4679_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4680_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4681_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4689_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4690_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4691_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4680_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4681_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4689_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4690_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4681_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4689_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6264_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6264_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6264_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6264_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6264_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6264_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6264_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6263_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6263_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6263_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6263_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6263_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6262_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6262_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6262_14.png"
            },
            {
                "algorithm_name": "stitch_tiles",
                "algorithm_params": {
                    "image_filenames": "/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6273_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6273_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6273_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6272_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6272_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6272_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6272_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6272_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6271_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6271_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6271_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6271_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6271_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6271_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6271_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4681_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4689_6270_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4680_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4681_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4689_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4690_6269_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4679_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4680_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4681_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4689_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4690_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4691_6268_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4679_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4680_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4681_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4689_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4690_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4691_6267_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4680_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4681_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4689_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4690_6266_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4681_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4689_6265_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4682_6264_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6264_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6264_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6264_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6264_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6264_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4688_6264_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4683_6263_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6263_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6263_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6263_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4687_6263_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4684_6262_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4685_6262_14.png,/tmp/f1hp6CrpMadJUxmNEi/temp/4686_6262_14.png"
                },
                "image_path": "/tmp/f1hp6CrpMadJUxmNEi/temp/stitched_tiles.png",
                "image_bounds": "[[38.99357205820944, -77.18994140625], [38.788345355085625, -76.90429687500001]]"
            },
            {
                "algorithm_name": "output_image_to_client",
                "image_extent": "[[38.99357205820944, -77.18994140625], [38.788345355085625, -76.90429687500001]]",
                "algorithm_params": {
                    "image_bounds": "[[38.99357205820944, -77.18994140625], [38.788345355085625, -76.90429687500001]]",
                    "image_path": "/tmp/f1hp6CrpMadJUxmNEi/temp/stitched_tiles.png"
                },
                "image_url": "/tmp/f1hp6CrpMadJUxmNEi/temp/stitched_tiles.png"
            }
        ]
    }

As you can see, even a relatively simple algorithm can generate a lot of data! This is extremely helpful though, because it lets you see exactly what happened over the course of the chain run.

Best Practices
==============

Make good use of the Chain Ledger, not just because it helps you keep track of values throughout a chain run but also because it helps you reproduce results at a later time. The history will also help other people who use your algorithms in their chains.
