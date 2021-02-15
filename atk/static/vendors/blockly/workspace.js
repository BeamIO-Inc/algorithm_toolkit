/* TODO: Change toolbox XML ID if necessary. Can export toolbox XML from Workspace Factory. */
var toolbox = document.getElementById("toolbox");

var options = {
	zoom: {
		controls: true,
		wheel: true
	},
	toolbox : toolbox,
	collapse : true,
	comments : false,
	disable : false,
	maxBlocks : Infinity,
	trashcan : true,
	horizontalLayout : false,
	toolboxPosition : 'start',
	css : true,
	media : '/static/vendors/blockly/media/',
	rtl : false,
	scrollbars : true,
	sounds : true,
	oneBasedIndex : true
};

/* Inject your workspace */
//var workspace = Blockly.inject("workspace", options);
var blocklyArea = document.getElementById('blocklyArea');
var blocklyDiv = document.getElementById('workspace');
var workspace = Blockly.inject(blocklyDiv, options);
var onresize = function(e) {
  	var element = blocklyArea;
  	var x = 0;
  	var y = 0;
  	do {
    	x += element.offsetLeft;
    	y += element.offsetTop;
    	element = element.offsetParent;
  	} while (element);
  	// Position blocklyDiv over blocklyArea.
 	blocklyDiv.style.left = x + 'px';
  	blocklyDiv.style.top = y + 'px';
  	blocklyDiv.style.width = blocklyArea.offsetWidth + 'px';
  	blocklyDiv.style.height = blocklyArea.offsetHeight + 'px';
    Blockly.svgResize(workspace);
};
window.addEventListener('resize', onresize, false);
onresize();
Blockly.svgResize(workspace);

/* Load Workspace Blocks from XML to workspace. Remove all code below if no blocks to load */

/* TODO: Change workspace blocks XML ID if necessary. Can export workspace blocks XML from Workspace Factory. */
//var workspaceBlocks = document.getElementById("workspaceBlocks");

/* Load blocks to workspace. */
//Blockly.Xml.domToWorkspace(workspaceBlocks, workspace);