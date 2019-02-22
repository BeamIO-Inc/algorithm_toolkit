def get_chains():
    chain_def = {
        "map_tiles": [
            {
                "algorithm": "getmaptiles_roi",
                "parameter_source": "user"
            }, {
                "algorithm": "stitch_tiles",
                "parameters": {
                    "image_filenames": {
                        "source": "chain_ledger",
                        "source_algorithm": "getmaptiles_roi",
                        "key": "image_filenames",
                        "occurrence": "first"
                    }
                }
            }, {
                "algorithm": "output_image_to_client",
                "parameters": {
                    "image_path": {
                        "source": "chain_ledger",
                        "source_algorithm": "stitch_tiles",
                        "key": "image_path",
                        "occurrence": "first"
                    },
                    "image_bounds": {
                        "source": "chain_ledger",
                        "source_algorithm": "stitch_tiles",
                        "key": "image_bounds",
                        "occurrence": "first"
                    }
                }
            }
        ]
    }
    return chain_def


def get_updated_chain():
    original_chain = get_chains()
    new_chain = {
        "do_some_math": [
            {
                "algorithm": "add_numbers",
                "parameter_source": "user"
            }, {
                "algorithm": "subtract_numbers",
                "parameters": {
                    "starting_value": {
                        "source": "chain_ledger",
                        "occurrence": "first",
                        "key": "result",
                        "source_algorithm": "add_numbers"
                    },
                    "number_to_subtract": {
                        "source": "user"
                    }
                }
            }, {
                "algorithm": "multiply_numbers",
                "parameters": {
                    "number_to_multiply": {
                        "source": "user"
                    },
                    "starting_value": {
                        "source": "chain_ledger",
                        "occurrence": "first",
                        "key": "result",
                        "source_algorithm": "subtract_numbers"
                    }
                }
            }, {
                "algorithm": "divide_numbers",
                "parameters": {
                    "number_to_divide": {
                        "source": "user"
                    },
                    "starting_value": {
                        "source": "chain_ledger",
                        "occurrence": "first",
                        "key": "result",
                        "source_algorithm": "multiply_numbers"
                    }
                }
            }, {
                "algorithm": "output_text",
                "parameters": {
                    "result": {
                        "source": "chain_ledger",
                        "occurrence": "first",
                        "key": "result",
                        "source_algorithm": "divide_numbers"
                    }
                }
            }
        ]
    }
    new_chain.update(original_chain)
    return new_chain


def get_algorithms():
    algs = [
        {
            "name": "getmaptiles_roi",
            "display_name": "Get Map Tiles In ROI",
            "description":
                "This algorithm will gather up map tiles at a given zoom "
                "level that intersect with the provided polygon. The source "
                "is the national map provided by USGS. All tiles will be "
                "written out to disk at a specified location. This "
                "location is also saved onto the chain ledger.",
            "version": "0.0.1",
            "license": "MIT",
            "private": False,
            "homepage": "https://tiledriver.com/developer",
            "required_parameters": [
                {
                    "name": "roi",
                    "description":
                        "Polygon WKT to obtain tiles that intersect.",
                    "display_name": "Polygon WKT",
                    "data_type": "string",
                    "field_type": "text",
                    "help_text":
                        "Enter well known text (WKT) for the polygon region "
                        "to obtain intersecting tiles.",
                    "min_value": None,
                    "max_value": None,
                    "default_value":
                        "POLYGON((-77.0419692993164 38.9933585922412,"
                        "-77.17311859130861 38.891887936025896,"
                        "-77.03853607177736 38.790272111428706,"
                        "-76.91013336181642 38.891887936025896,"
                        "-77.0419692993164 38.9933585922412))",
                    "custom_validation": None,
                    "parameter_choices": [],
                    "sort_order": 0
                },
                {
                    "name": "zoom",
                    "description": "Zoom level",
                    "display_name": "Zoom level",
                    "data_type": "integer",
                    "field_type": "number",
                    "help_text":
                        "Enter an integer corresponding to the zoom "
                        "level, 16 is max value supported.",
                    "min_value": 5,
                    "max_value": 16,
                    "default_value": 14,
                    "custom_validation": None,
                    "parameter_choices": [],
                    "sort_order": 1
                }
            ],
            "optional_parameters": [],
            "outputs": [
                {
                    "name": "image_filenames",
                    "description":
                        "Absolute paths to each image collected separated "
                        "by commas.",
                    "display_name": "Names of images collected",
                    "data_type": "string",
                    "sort_order": 0
                }
            ]
        }, {
            "name": "stitch_tiles",
            "display_name": "Stitch together tiles",
            "description":
                "This algorithm stitches a group of map tiles saved in a "
                "directory together. The resulting image is saved in png "
                "format with the image path and bounds saved onto the "
                "chain ledger.",
            "version": "0.0.1",
            "license": "MIT",
            "private": False,
            "homepage": "https://tiledriver.com/developer",
            "required_parameters": [
                {
                    "name": "image_filenames",
                    "description":
                        "List of image filenames to stitch together",
                    "display_name": "Images to Stitch Together",
                    "data_type": "string",
                    "field_type": "text",
                    "help_text": "Comma separated list.",
                    "min_value": None,
                    "max_value": None,
                    "default_value": None,
                    "custom_validation": None,
                    "parameter_choices": [],
                    "sort_order": 0
                }
            ],
            "optional_parameters": [],
            "outputs": [
                {
                    "name": "image_path",
                    "description": "Path to image that was stitched together",
                    "display_name": "Stitched Image Path",
                    "data_type": "string",
                    "sort_order": 0
                },
                {
                    "name": "image_bounds",
                    "description":
                        "Array containing the leaflet bounds of stiched "
                        "image extent",
                    "display_name": "Stitched Image Bounds",
                    "data_type": "string",
                    "sort_order": 1
                }
            ]
        }, {
            "name": "output_image_to_client",
            "display_name": "Output Image To Web",
            "description":
                "This algorithm will pull the path to an image (RGB png "
                "currently supported) and image bounds (as defined by "
                "leaflet) from the chain ledger and re-enter this "
                "information with the correct keys needed by the Algorithm "
                "Toolkit to send an image back to a chain endpoint request "
                "for placement onto a map.",
            "version": "0.0.1",
            "license": "MIT",
            "private": False,
            "homepage": "https://tiledriver.com/developer",
            "required_parameters": [
                {
                    "name": "image_path",
                    "description": "Path of image to send to client",
                    "display_name": "Image Path",
                    "data_type": "string",
                    "field_type": "text",
                    "help_text": "Absolute path to image",
                    "min_value": None,
                    "max_value": None,
                    "default_value": None,
                    "custom_validation": None,
                    "parameter_choices": [],
                    "sort_order": 0
                },
                {
                    "name": "image_bounds",
                    "description":
                        "Array containing the leaflet bounds of image extent",
                    "display_name": "Image Bounds",
                    "data_type": "string",
                    "field_type": "text",
                    "help_text":
                        "String array containing image bounds numbers.",
                    "min_value": None,
                    "max_value": None,
                    "default_value": None,
                    "custom_validation": None,
                    "parameter_choices": [],
                    "sort_order": 1
                }],
            "optional_parameters": [],
            "outputs": [
                {
                    "name": "image_url",
                    "description": "Path of image to send to client",
                    "display_name": "Image Path",
                    "data_type": "string",
                    "sort_order": 0
                },
                {
                    "name": "image_extent",
                    "description":
                        "Array containing the leaflet bounds of image extent",
                    "display_name": "Image Bounds",
                    "data_type": "string",
                    "sort_order": 1
                }
            ]
        }
    ]
    return algs


def get_chain_algs():
    algs = get_algorithms()
    chain_algs = []
    for alg in algs:
        for p in alg['required_parameters']:
            if alg['name'] == 'getmaptiles_roi':
                p['source'] = 'user'
            else:
                p['source'] = 'chain_ledger'
        chain_algs.append(alg)

    return chain_algs


def get_test_run_chain():
    chain = {
        "algorithms": [
            {
                "name": "getmaptiles_roi",
                "parameters": {
                    "roi":
                        "POLYGON((-77.0419692993164 38.9933585922412,"
                        "-77.17311859130861 38.891887936025896,"
                        "-77.03853607177736 38.790272111428706,"
                        "-76.91013336181642 38.891887936025896,"
                        "-77.0419692993164 38.9933585922412))",
                    "zoom": "14"
                }
            }, {
                "name": "stitch_tiles",
                "parameters": {}
            }, {
                "name": "output_image_to_client",
                "parameters": {}
            }
        ],
        "chain_name": "map_tiles"
    }
    return chain


def test_algorithm_form_data():
    alg = {
        "description": "Add two numbers together to get a result.",
        "display_name": "Add two numbers",
        "homepage": "google.com",
        "license": "Proprietary",
        "name": "add_numbers",
        "parameters": [
            {
                "custom_validation": "",
                "data_type": "integer",
                "default_value": "",
                "description": "The starting value for the add operation.",
                "display_name": "Starting Value",
                "field_type": "number",
                "help_text": "Enter a starting value",
                "max_value": "0",
                "min_value": "100",
                "name": "starting_value",
                "original_name": "starting_value",
                "parameter_choices": "",
                "required": True,
                "sort_order": 0
            },
            {
                "custom_validation": "",
                "data_type": "integer",
                "default_value": "",
                "description": "The number to add to the starting value.",
                "display_name": "Number to Add",
                "field_type": "number",
                "help_text": "Enter a number to add to the starting value",
                "max_value": "1",
                "min_value": "500",
                "name": "number_to_add",
                "original_name": "number_to_add",
                "parameter_choices": "",
                "required": True,
                "sort_order": 1
            },
            {
                "custom_validation": "",
                "data_type": "string",
                "default_value": "",
                "description": "Random string to display.",
                "display_name": "Random String",
                "field_type": "text",
                "help_text": "Enter a random string",
                "max_value": "",
                "min_value": "",
                "name": "random_string",
                "original_name": "random_string",
                "parameter_choices": "",
                "required": False,
                "sort_order": 0
            }
        ],
        "outputs": [
            {
                "data_type": "integer",
                "description": "The result of the add operation.",
                "display_name": "Result",
                "name": "result",
                "original_name": "result",
                "sort_order": 0
            }
        ],
        'deleted_parameters': '',
        'deleted_outputs': '',
        "private": True,
        "version": "0.0.1"
    }
    return alg


def get_chain_builder_block_list():
    block_list = [
        u'<category name="Get Map Tiles In ROI" colour="222">\n    '
        '<block type="getmaptiles_roi"></block>\n    '
        '<block type="getmaptiles_roi__image_filenames"></block>\n</category>',
        u'<category name="Output Image To Web" colour="222">\n    '
        '<block type="output_image_to_client"></block>\n    '
        '<block type="output_image_to_client__image_url"></block>\n    '
        '<block type="output_image_to_client__image_extent"></block>\n'
        '</category>',
        u'<category name="Stitch together tiles" colour="222">\n    '
        '<block type="stitch_tiles"></block>\n    '
        '<block type="stitch_tiles__image_path"></block>\n    '
        '<block type="stitch_tiles__image_bounds"></block>\n</category>'
    ]
    return block_list


def get_chain_builder_additional_block():
    original_blocks = get_chain_builder_block_list()
    new_block = [
        u'<category name="Add two numbers" colour="222">\n    '
        '<block type="beamio/add_numbers"></block>\n    '
        '<block type="beamio/add_numbers__result"></block>\n</category>'
    ]
    return new_block + original_blocks


def get_chain_builder_block_scripts():
    block_scripts = [
        u'Blockly.Blocks["output_image_to_client"] = {init: function() '
        '{this.appendDummyInput().setAlign(Blockly.ALIGN_CENTRE)'
        '.appendField(new Blockly.FieldLabel("ALGORITHM", "font-weight-bold"'
        '));this.appendDummyInput().appendField("Output Image To Web");'
        'this.appendDummyInput().setAlign(Blockly.ALIGN_RIGHT)'
        '.appendField(new Blockly.FieldLabel("Required Input Fields:", '
        '"font-weight-bold"));this.appendValueInput("image_path")'
        '.setCheck("string").setAlign(Blockly.ALIGN_RIGHT)'
        '.appendField("image_path");this.appendValueInput("image_bounds")'
        '.setCheck("string").setAlign(Blockly.ALIGN_RIGHT)'
        '.appendField("image_bounds");this.setInputsInline(false);'
        'this.setPreviousStatement(true, null);this.setNextStatement('
        'true, null);this.setColour(222);this.setTooltip("Output Image '
        'To Web");this.data = "algorithm";} };\nBlockly'
        '.Blocks["output_image_to_client__image_url"] = {init: function() '
        '{this.appendDummyInput().setAlign(Blockly.ALIGN_CENTRE)'
        '.appendField(new Blockly.FieldLabel("OUTPUT FIELD", '
        '"font-weight-bold"));this.appendDummyInput().appendField("Output '
        'Image To Web").appendField(new Blockly.FieldDropdown(['
        '["first","first"],["second","second"],["third","third"],'
        '["fourth","fourth"],["fifth","fifth"],["sixth","sixth"],]), '
        '"occurrence");this.appendDummyInput().appendField("image_url");'
        'this.setOutput(true, "string");this.setColour(222);this.data = '
        '"input";} };\nBlockly.Blocks["output_image_to_client__image_extent"]'
        ' = {init: function() {this.appendDummyInput().setAlign(Blockly'
        '.ALIGN_CENTRE).appendField(new Blockly.FieldLabel("OUTPUT FIELD", '
        '"font-weight-bold"));this.appendDummyInput().appendField("Output '
        'Image To Web").appendField(new Blockly.FieldDropdown([["first",'
        '"first"],["second","second"],["third","third"],["fourth","fourth"],'
        '["fifth","fifth"],["sixth","sixth"],]), "occurrence");this'
        '.appendDummyInput().appendField("image_extent");this.setOutput(true, '
        '"string");this.setColour(222);this.data = "input";} };\n',
        u'Blockly'
        '.Blocks["getmaptiles_roi"] = {init: function() {this'
        '.appendDummyInput().setAlign(Blockly.ALIGN_CENTRE).appendField(new '
        'Blockly.FieldLabel("ALGORITHM", "font-weight-bold"));this'
        '.appendDummyInput().appendField("Get Map Tiles In ROI");this'
        '.appendDummyInput().setAlign(Blockly.ALIGN_RIGHT).appendField(new '
        'Blockly.FieldLabel("Required Input Fields:", "font-weight-bold"));'
        'this.appendValueInput("roi").setCheck("string").setAlign(Blockly'
        '.ALIGN_RIGHT).appendField("roi");this.appendValueInput("zoom")'
        '.setCheck("integer").setAlign(Blockly.ALIGN_RIGHT)'
        '.appendField("zoom");this.setInputsInline(false);this'
        '.setPreviousStatement(true, null);this.setNextStatement(true, null);'
        'this.setColour(222);this.setTooltip("Get Map Tiles In ROI");'
        'this.data = "algorithm";} };\nBlockly.Blocks['
        '"getmaptiles_roi__image_filenames"] = {init: function() {this'
        '.appendDummyInput().setAlign(Blockly.ALIGN_CENTRE).appendField(new '
        'Blockly.FieldLabel("OUTPUT FIELD", "font-weight-bold"));this'
        '.appendDummyInput().appendField("Get Map Tiles In ROI").appendField('
        'new Blockly.FieldDropdown([["first","first"],["second","second"],'
        '["third","third"],["fourth","fourth"],["fifth","fifth"],["sixth",'
        '"sixth"],]), "occurrence");this.appendDummyInput().appendField('
        '"image_filenames");this.setOutput(true, "string");this.setColour(222)'
        ';this.data = "input";} };\n',
        u'Blockly.Blocks["stitch_tiles"] = {'
        'init: function() {this.appendDummyInput().setAlign(Blockly'
        '.ALIGN_CENTRE).appendField(new Blockly.FieldLabel("ALGORITHM", '
        '"font-weight-bold"));this.appendDummyInput().appendField("Stitch '
        'together tiles");this.appendDummyInput().setAlign(Blockly'
        '.ALIGN_RIGHT).appendField(new Blockly.FieldLabel("Required Input '
        'Fields:", "font-weight-bold"));this.appendValueInput('
        '"image_filenames").setCheck("string").setAlign(Blockly.ALIGN_RIGHT)'
        '.appendField("image_filenames");this.setInputsInline(false);this'
        '.setPreviousStatement(true, null);this.setNextStatement(true, null);'
        'this.setColour(222);this.setTooltip("Stitch together tiles");'
        'this.data = "algorithm";} };\nBlockly.Blocks['
        '"stitch_tiles__image_path"] = {init: function() {this'
        '.appendDummyInput().setAlign(Blockly.ALIGN_CENTRE).appendField(new '
        'Blockly.FieldLabel("OUTPUT FIELD", "font-weight-bold"));this'
        '.appendDummyInput().appendField("Stitch together tiles").appendField('
        'new Blockly.FieldDropdown([["first","first"],["second","second"],'
        '["third","third"],["fourth","fourth"],["fifth","fifth"],'
        '["sixth","sixth"],]), "occurrence");this.appendDummyInput()'
        '.appendField("image_path");this.setOutput(true, "string");this'
        '.setColour(222);this.data = "input";} };\nBlockly.Blocks['
        '"stitch_tiles__image_bounds"] = {init: function() {this'
        '.appendDummyInput().setAlign(Blockly.ALIGN_CENTRE).appendField(new '
        'Blockly.FieldLabel("OUTPUT FIELD", "font-weight-bold"));this'
        '.appendDummyInput().appendField("Stitch together tiles")'
        '.appendField(new Blockly.FieldDropdown([["first","first"],'
        '["second","second"],["third","third"],["fourth","fourth"],["fifth",'
        '"fifth"],["sixth","sixth"],]), "occurrence");this.appendDummyInput()'
        '.appendField("image_bounds");this.setOutput(true, "string");this'
        '.setColour(222);this.data = "input";} };\n'
    ]
    return block_scripts


def get_chain_builder_additional_script():
    original_scripts = get_chain_builder_block_scripts()
    new_script = [
        u'Blockly.Blocks["beamio/add_numbers"] = {init: function() {this'
        '.appendDummyInput().setAlign(Blockly.ALIGN_CENTRE).appendField'
        '(new Blockly.FieldLabel("ALGORITHM", "font-weight-bold"));this'
        '.appendDummyInput().appendField("Add two numbers");this'
        '.appendDummyInput().setAlign(Blockly.ALIGN_RIGHT).appendField'
        '(new Blockly.FieldLabel("Required Input Fields:", '
        '"font-weight-bold"));this.appendValueInput("starting_value")'
        '.setCheck("integer").setAlign(Blockly.ALIGN_RIGHT).appendField'
        '("starting_value");this.appendValueInput("number_to_add")'
        '.setCheck("integer").setAlign(Blockly.ALIGN_RIGHT).appendField'
        '("number_to_add");this.appendDummyInput().setAlign(Blockly'
        '.ALIGN_RIGHT).appendField(new Blockly.FieldLabel("Optional '
        'Input Fields:", "font-weight-bold"));this.appendValueInput'
        '("random_string").setCheck("string").setAlign(Blockly.ALIGN_RIGHT)'
        '.appendField("random_string");this.setInputsInline(false);this'
        '.setPreviousStatement(true, null);this.setNextStatement(true, null);'
        'this.setColour(222);this.setTooltip("Add two numbers");'
        'this.data = "algorithm";} };\nBlockly'
        '.Blocks["beamio/add_numbers__result"] = {init: function() {this'
        '.appendDummyInput().setAlign(Blockly.ALIGN_CENTRE).appendField'
        '(new Blockly.FieldLabel("OUTPUT FIELD", "font-weight-bold"));'
        'this.appendDummyInput().appendField("Add two numbers").appendField'
        '(new Blockly.FieldDropdown([["first","first"],["second","second"],'
        '["third","third"],["fourth","fourth"],["fifth","fifth"],'
        '["sixth","sixth"],]), "occurrence");this.appendDummyInput()'
        '.appendField("result");this.setOutput(true, "integer");this'
        '.setColour(222);this.data = "input";} };\n'
    ]
    return original_scripts[:3] + new_script + original_scripts[3:]


def get_chain_builder_chain_blocks():
    chain_blocks = (
        '<xml xmlns="http://www.w3.org/1999/xhtml" '
        'id="workspaceBlocks" style="display:none">\n'
        '<variables></variables>\n'
        '<block type="getmaptiles_roi" id="testid" '
        'x="10" y="10">\n'
        '<data>algorithm</data>\n'
        '<value name="roi">\n'
        '<block type="user_input" id="testid">\n'
        '<data>input</data>\n'
        '</block>\n'
        '</value>\n'
        '<value name="zoom">\n'
        '<block type="user_input" id="testid">\n'
        '<data>input</data>\n'
        '</block>\n'
        '</value>\n'
        '<next>\n'
        '<block type="stitch_tiles" id="testid">\n'
        '<data>algorithm</data>\n'
        '<value name="image_filenames">\n'
        '<block type="getmaptiles_roi__image_filenames" id="testid">\n'
        '<field name="occurrence">first</field><data>input</data>\n'
        '</block>\n'
        '</value>\n'
        '<next>\n'
        '<block type="output_image_to_client" id="testid">\n'
        '<data>algorithm</data>\n'
        '<value name="image_path">\n'
        '<block type="stitch_tiles__image_path" id="testid">\n'
        '<field name="occurrence">first</field><data>input</data>\n'
        '</block>\n'
        '</value>\n'
        '<value name="image_bounds">\n'
        '<block type="stitch_tiles__image_bounds" id="testid">\n'
        '<field name="occurrence">first</field><data>input</data>\n'
        '</block>\n'
        '</value>\n'
        '</block>\n'
        '</next>\n'
        '</block>\n'
        '</next>\n'
        '</block>\n'
        '</xml>\n'
    )
    return chain_blocks


def get_chain_builder_chain_blocks_math():
    chain_blocks = (
        '<xml xmlns="http://www.w3.org/1999/xhtml" '
        'id="workspaceBlocks" style="display:none">\n'
        '<variables></variables>\n'
        '<block type="add_numbers" id="testid" x="10" y="10">\n'
        '<data>algorithm</data>\n'
        '<next>\n'
        '<block type="subtract_numbers" id="testid">\n'
        '<data>algorithm</data>\n'
        '<next>\n'
        '<block type="multiply_numbers" id="testid">\n'
        '<data>algorithm</data>\n'
        '<next>\n'
        '<block type="divide_numbers" id="testid">\n'
        '<data>algorithm</data>\n'
        '<next>\n'
        '<block type="output_text" id="testid">\n'
        '<data>algorithm</data>\n'
        '</block>\n'
        '</next>\n'
        '</block>\n'
        '</next>\n'
        '</block>\n'
        '</next>\n'
        '</block>\n'
        '</next>\n'
        '</block>\n'
        '</xml>\n'
    )
    return chain_blocks
