# load cnn for training
loads a convolutional neural network for training.  This removes the top layer of the network, so it is ready to be trained for any number of image classes.
Version: 0.0.1
License: MIT
Homepage: []

## Parameters:
Name|Description|Required
---|---|:---:
model_type||Yes
pretrained_weights_path||Yes

## Outputs:
Name|Description
---|---
cnn_model|
